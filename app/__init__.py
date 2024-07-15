import csv
import os
from typing import io

from bs4 import BeautifulSoup
from datetime import datetime
import textwrap
from flask import Flask, render_template, request, flash, session, send_file, redirect, url_for
import requests
import feedparser
import threading

from .auth import login_required
from .db import get_db
from .blog import get_post


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'db.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/blog', endpoint='blog')

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    rss_urls = [
        'https://g1.globo.com/rss/g1/',
        'https://g1.globo.com/dynamo/loterias/rss2.xml',
        'https://g1.globo.com/rss/g1/carros/',
        'https://g1.globo.com/dynamo/ciencia-e-saude/rss2.xml',
        'https://g1.globo.com/dynamo/economia/rss2.xml',
        'https://g1.globo.com/dynamo/educacao/rss2.xml',
        'https://g1.globo.com/dynamo/mundo/rss2.xml',
        'https://g1.globo.com/rss/g1/politica/',
        'https://g1.globo.com/rss/g1/pop-arte/',
        'https://g1.globo.com/dynamo/tecnologia/rss2.xml',
        'https://g1.globo.com/dynamo/turismo-e-viagem/rss2.xml'
    ]

    current_rss_url_index = 0

    def update_rss_url():
        nonlocal current_rss_url_index
        current_rss_url_index = (current_rss_url_index + 1) % len(rss_urls)
        print(f"RSS URL atualizada para: {rss_urls[current_rss_url_index]}")

    def fetch_rss():
        nonlocal current_rss_url_index
        rss_url = rss_urls[current_rss_url_index]
        feed = feedparser.parse(rss_url)

    def schedule_rss_update():
        threading.Timer(100, schedule_rss_update).start()
        update_rss_url()

    def schedule_rss_fetch():
        threading.Timer(100, schedule_rss_fetch).start()
        fetch_rss()

    schedule_rss_update()
    schedule_rss_fetch()

    @app.route('/noticias')
    def noticias():
        try:
            feed = feedparser.parse(rss_urls[current_rss_url_index])
            newspaper = []
            num_noticias_a_exibir = 7
            max_caracteres_description = 450

            for entry in feed.entries[:num_noticias_a_exibir]:
                date_published = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
                formatted_date = f" {date_published.strftime('%d/%m/%Y %H:%M')}"
                description = entry.get('summary', entry.title)
                description_text = BeautifulSoup(description, 'html.parser').get_text()

                limited_description = textwrap.shorten(description_text, width=max_caracteres_description,
                                                       placeholder='...')

                noticia = {
                    'title': entry.title,
                    'content': limited_description,
                    'published': formatted_date
                }

                newspaper.append(noticia)
        except Exception as e:
            newspaper = [{
                'title': 'Erro ao recuperar notícias',
                'content': str(e),
                'published': ''
            }]

        return render_template('noticias.html', noticias=newspaper)

    @app.route('/noticias/<string:noticia_tag>')
    def exibir_noticia(noticia_tag):
        try:
            feed = feedparser.parse(rss_urls[current_rss_url_index])
            entry = None

            for item in feed.entries:
                if noticia_tag in item.title:
                    entry = item
                    break

            if entry:
                date_published = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
                formatted_date = f" {date_published.strftime('%d/%m/%Y %H:%M')}"
                description = entry.get('summary', entry.title)
                description_text = BeautifulSoup(description, 'html.parser').get_text()

                noticia = {
                    'title': entry.title,
                    'content': description_text,
                    'published': formatted_date
                }
            else:
                raise IndexError("Notícia não encontrada")
        except Exception as e:
            noticia = {
                'title': 'Erro ao recuperar notícia',
                'content': str(e),
                'published': ''
            }

        return render_template('noticia.html', noticia=noticia)

    def get_user_location(user_ip):
        try:
            response = requests.get(f"https://ipinfo.io/{user_ip}/json")
            data = response.json()
            city = data.get('city')
            if city:
                return city
        except:
            pass
        return "São Paulo"

    def get_weather_data(city):
        API_KEY = 'eb971a2f3fb4e02e6f3a0b14acc379bb'
        weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
        response = requests.get(weather_url)
        if response.status_code == 200:
            weather_data = response.json()
            return weather_data
        return None

    def traduzir_condicao(condicao_ingles):
        traducoes = {
            'Clear': 'Limpo',
            'Clouds': 'Nublado',
            'Drizzle': 'Garoa',
            'Rain': 'Chuva',
            'Thunderstorm': 'Tempestade',
            'Snow': 'Neve',
            'Mist': 'Neblina',
            'Fog': 'Nevoeiro',
        }
        return traducoes.get(condicao_ingles, condicao_ingles)

    @app.route('/')
    def index():
        user_ip = request.remote_addr
        user_location = get_user_location(user_ip)
        weather_data = get_weather_data(user_location)
        condicao_meteorologica = traduzir_condicao(weather_data['weather'][0]['main']) if weather_data else None
        db = get_db()
        posts = db.execute(
            'SELECT p.id, title, body, created, author_id, username'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' ORDER BY created DESC'
        ).fetchall()
        return render_template('index.html', user_location=user_location, weather_data=weather_data,
                               condicao_meteorologica=condicao_meteorologica, posts=posts)

    @app.route('/sobre')
    def sobre():
        return render_template('sobre.html')

    def fetch_coupons():
        keywords = ['eletronicos', 'roupa', 'comida', 'viajem', 'beleza']
        base_url = 'https://www.coupongpts.com/en-us/result?search='
        coupons = []

        for keyword in keywords:
            url = f"{base_url}{keyword}"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            coupon_elements = soup.find_all('div', class_='card card-1 sale-type')

            for coupon in coupon_elements:
                title = coupon.find('div', class_='title').get_text()
                link = coupon.find('button', class_='btn getDeal')['data-url']
                coupons.append({'title': title, 'link': link})

        return coupons

    @app.route('/projetos')
    def projetos():

        coupons = fetch_coupons()

        return render_template('projetos.html', cupons=coupons)

    @app.route('/calculadora', methods=['GET', 'POST'])
    @login_required
    def calculadora():
        result = None
        if request.method == 'POST':
            try:
                num1 = float(request.form['num1'])
                num2 = float(request.form['num2'])
                operation = request.form['operation']
                if operation == 'add':
                    result = num1 + num2
                elif operation == 'subtract':
                    result = num1 - num2
                elif operation == 'multiply':
                    result = num1 * num2
                elif operation == 'divide':
                    result = num1 / num2
                session['last_result'] = result
            except (ValueError, ZeroDivisionError):
                result = 'Valor inválido ou divisão por zero'
                session['last_result'] = result
        return render_template('calculadora.html', result=result, last_result=session.get('last_result'))

    @app.route('/moedas')
    @login_required
    def moedas():
        api_url = 'https://api.exchangerate-api.com/v4/latest/BRL'  # Exemplo de API de taxas de câmbio
        response = requests.get(api_url)
        data = response.json()
        rates = {
            'BRL': 1,
            'USD': data['rates']['USD'],
            'EUR': data['rates']['EUR'],
            'BTN': data['rates']['BTN'],
            'ARS': data['rates']['ARS'],
            'CAD': data['rates']['CAD'],
            'GBP': data['rates']['GBP'],
            'JPY': data['rates']['JPY'],
            'CNY': data['rates']['CNY'],
            'AUD': data['rates']['AUD'],
        }
        return render_template('moedas.html', rates=rates)

    @app.route('/praias')
    @login_required
    def praias():
        url = "https://praialimpa.net/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        estados = ["São Paulo", "Santa Catarina", "Rio de Janeiro"]
        praias_limpas = {estado: [] for estado in estados}

        sections = soup.find_all('section')
        for section in sections:
            h1 = section.find('h1')
            if h1 and h1.text in estados:
                estado = h1.text
                praias = section.find_all('div', class_='beach')
                for praia in praias:
                    nome = praia.find('div', class_='name').text
                    localizacao = praia.find('div', class_='location').text
                    status = praia.find('div', class_='status').text
                    praias_limpas[estado].append({
                        'nome': nome,
                        'localizacao': localizacao,
                        'status': status
                    })

        return render_template('praias.html', praias=praias_limpas)

    # Bloco de notas::

    @app.route('/bloco-de-notas', methods=['GET', 'POST'])
    @login_required
    def bloco_de_notas():
        db = get_db()

        if request.method == 'POST':
            note_content = request.form['note']
            user_id = session.get('user_id')  # Supondo que o ID do usuário está armazenado na sessão
            db.execute(
                'INSERT INTO note (content, user_id) VALUES (?, ?)',
                (note_content, user_id)
            )
            db.commit()
            flash('Nota salva com sucesso!')
            return redirect(url_for('bloco_de_notas'))

        notes = db.execute(
            'SELECT id, content FROM note WHERE user_id = ?',
            (session.get('user_id'),)
        ).fetchall()

        return render_template('bloco_notas.html', notes=notes)

    @app.route('/download_note/<int:note_id>')
    @login_required
    def download_note(note_id):
        db = get_db()
        note = db.execute(
            'SELECT content FROM note WHERE id = ? AND user_id = ?',
            (note_id, session.get('user_id'))
        ).fetchone()

        if note:
            return send_file(
                io.BytesIO(note['content'].encode('utf-8')),
                as_attachment=True,
                download_name=f'note_{note_id}.txt'
            )
        flash('Nota não encontrada ou você não tem permissão para acessá-la.')
        return redirect(url_for('bloco_de_notas'))

    @app.route('/delete_note/<int:note_id>')
    @login_required
    def delete_note(note_id):
        db = get_db()
        db.execute(
            'DELETE FROM note WHERE id = ? AND user_id = ?',
            (note_id, session.get('user_id'))
        )
        db.commit()
        flash('Nota excluída com sucesso!')
        return redirect(url_for('bloco_de_notas'))

    # Gestão financeira::

    def get_expenses(user_id):
        file_path = os.path.join(app.instance_path, f'expenses_{user_id}.csv')
        if os.path.exists(file_path):
            with open(file_path, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                return list(reader)
        return []

    def save_expense(user_id, despesa, valor):
        file_path = os.path.join(app.instance_path, f'expenses_{user_id}.csv')
        file_exists = os.path.exists(file_path)
        with open(file_path, mode='a', newline='') as file:
            fieldnames = ['despesa', 'valor']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({'despesa': despesa, 'valor': valor})

    def delete_expense(user_id, despesa_id):
        file_path = os.path.join(app.instance_path, f'expenses_{user_id}.csv')
        temp_file_path = os.path.join(app.instance_path, f'expenses_{user_id}_temp.csv')

        with open(file_path, mode='r', newline='') as file, open(temp_file_path, mode='w', newline='') as temp_file:
            reader = csv.DictReader(file)
            writer = csv.DictWriter(temp_file, fieldnames=reader.fieldnames)
            writer.writeheader()

            for row in reader:
                if row['despesa'] != despesa_id:
                    writer.writerow(row)

        os.replace(temp_file_path, file_path)

    def get_salary(user_id):
        file_path = os.path.join(app.instance_path, f'salary_{user_id}.csv')
        if os.path.exists(file_path):
            with open(file_path, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                salary_row = list(reader)
                if salary_row:
                    return float(salary_row[0]['salary'])
        return 0.0

    def save_salary(user_id, salary):
        file_path = os.path.join(app.instance_path, f'salary_{user_id}.csv')
        with open(file_path, mode='w', newline='') as file:
            fieldnames = ['salary']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'salary': salary})

    @app.route('/gestao-financeira', methods=['GET', 'POST'])
    @login_required
    def gestao_financeira():
        user_id = session.get('user_id')  # Supondo que o ID do usuário está armazenado na sessão

        if request.method == 'POST':
            if 'salary' in request.form:
                salary = float(request.form['salary'])
                save_salary(user_id, salary)
                flash('Salário registrado com sucesso!')
            elif 'despesa' in request.form:
                despesa = request.form['despesa']
                valor = float(request.form['valor'])
                save_expense(user_id, despesa, valor)
                flash('Despesa registrada com sucesso!')
            elif 'delete_expense' in request.form:
                despesa_id = request.form['delete_expense']
                delete_expense(user_id, despesa_id)
                flash('Despesa excluída com sucesso!')
            return redirect(url_for('gestao_financeira'))

        despesas = get_expenses(user_id)
        salario = get_salary(user_id)
        total_despesas = sum(float(d['valor']) for d in despesas)
        saldo = salario - total_despesas

        return render_template('gestao_financeira.html', despesas=despesas, salario=salario,
                               total_despesas=total_despesas, saldo=saldo)

    @app.route('/download-expenses')
    @login_required
    def download_expenses():
        user_id = session.get('user_id')  # Supondo que o ID do usuário está armazenado na sessão
        file_path = os.path.join(app.instance_path, f'expenses_{user_id}.csv')
        return send_file(file_path, as_attachment=True)

    return app
