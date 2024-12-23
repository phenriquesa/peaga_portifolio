import csv
import os
from typing import io
from bs4 import BeautifulSoup
from datetime import datetime
import textwrap
from flask import (
    Flask,
    render_template,
    request,
    flash,
    session,
    send_file,
    redirect,
    url_for,
    jsonify,
)
import requests
import feedparser
import threading

from .auth import login_required
from .db import get_db
from .blog import get_post
from dotenv import load_dotenv
import unicodedata


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        DATABASE=os.path.join(app.instance_path, "db.sqlite"),
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import blog

    app.register_blueprint(blog.bp)
    app.add_url_rule("/blog", endpoint="blog")

    from . import db

    db.init_app(app)

    from . import auth

    app.register_blueprint(auth.bp)

    rss_urls = [
        "https://g1.globo.com/rss/g1/",
        "https://g1.globo.com/dynamo/loterias/rss2.xml",
        "https://g1.globo.com/rss/g1/carros/",
        "https://g1.globo.com/dynamo/ciencia-e-saude/rss2.xml",
        "https://g1.globo.com/dynamo/economia/rss2.xml",
        "https://g1.globo.com/dynamo/educacao/rss2.xml",
        "https://g1.globo.com/dynamo/mundo/rss2.xml",
        "https://g1.globo.com/rss/g1/politica/",
        "https://g1.globo.com/rss/g1/pop-arte/",
        "https://g1.globo.com/dynamo/tecnologia/rss2.xml",
        "https://g1.globo.com/dynamo/turismo-e-viagem/rss2.xml",
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

    # Noticias
    @app.route("/noticias")
    def noticias():
        try:
            feed = feedparser.parse(rss_urls[current_rss_url_index])
            newspaper = []
            num_noticias_a_exibir = 7
            max_caracteres_description = 450

            for entry in feed.entries[:num_noticias_a_exibir]:
                date_published = datetime.strptime(
                    entry.published, "%a, %d %b %Y %H:%M:%S %z"
                )
                formatted_date = f" {date_published.strftime('%d/%m/%Y %H:%M')}"
                description = entry.get("summary", entry.title)
                description_text = BeautifulSoup(description, "html.parser").get_text()

                limited_description = textwrap.shorten(
                    description_text,
                    width=max_caracteres_description,
                    placeholder="...",
                )

                noticia = {
                    "title": entry.title,
                    "content": limited_description,
                    "published": formatted_date,
                }

                newspaper.append(noticia)
        except Exception as e:
            newspaper = [
                {
                    "title": "Erro ao recuperar notícias",
                    "content": str(e),
                    "published": "",
                }
            ]

        return render_template("noticias.html", noticias=newspaper)

    # Noticias
    @app.route("/noticias/<string:noticia_tag>")
    def exibir_noticia(noticia_tag):
        try:
            feed = feedparser.parse(rss_urls[current_rss_url_index])
            entry = None

            for item in feed.entries:
                if noticia_tag in item.title:
                    entry = item
                    break

            if entry:
                date_published = datetime.strptime(
                    entry.published, "%a, %d %b %Y %H:%M:%S %z"
                )
                formatted_date = f" {date_published.strftime('%d/%m/%Y %H:%M')}"
                description = entry.get("summary", entry.title)
                description_text = BeautifulSoup(description, "html.parser").get_text()

                noticia = {
                    "title": entry.title,
                    "content": description_text,
                    "published": formatted_date,
                }
            else:
                raise IndexError("Notícia não encontrada")
        except Exception as e:
            noticia = {
                "title": "Erro ao recuperar notícia",
                "content": str(e),
                "published": "",
            }

        return render_template("noticia.html", noticia=noticia)

    # Geolocalização
    def get_user_location(user_ip):
        try:
            response = requests.get(f"https://ipinfo.io/{user_ip}/json")
            data = response.json()
            city = data.get("city")
            if city:
                return city
        except:
            pass
        return "São Paulo"

    def get_weather_data(city):
        API_KEY = os.getenv("API_KEY")
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(weather_url)
        if response.status_code == 200:
            weather_data = response.json()
            return weather_data
        return None

    def traduzir_condicao(condicao_ingles):
        traducoes = {
            "Clear": "Limpo",
            "Clouds": "Nublado",
            "Drizzle": "Garoa",
            "Rain": "Chuva",
            "Thunderstorm": "Tempestade",
            "Snow": "Neve",
            "Mist": "Neblina",
            "Fog": "Nevoeiro",
        }
        return traducoes.get(condicao_ingles, condicao_ingles)

    # Index
    @app.route("/")
    def index():
        user_ip = request.remote_addr
        user_location = get_user_location(user_ip)
        weather_data = get_weather_data(user_location)
        condicao_meteorologica = (
            traduzir_condicao(weather_data["weather"][0]["main"])
            if weather_data
            else None
        )
        db = get_db()
        posts = db.execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " ORDER BY created DESC"
        ).fetchall()
        return render_template(
            "index.html",
            user_location=user_location,
            weather_data=weather_data,
            condicao_meteorologica=condicao_meteorologica,
            posts=posts,
        )

    # Sobre
    @app.route("/sobre")
    def sobre():
        return render_template("sobre.html")

    # Projetos
    @app.route("/projetos")
    def projetos():

        return render_template("projetos.html")

    # Calculadora
    @app.route("/calculadora", methods=["GET", "POST"])
    @login_required
    def calculadora():
        result = None
        error_message = None
        if request.method == "POST":
            try:
                num1 = float(request.form["num1"])
                num2 = float(request.form["num2"])
                operation = request.form["operation"]
                if operation == "add":
                    result = num1 + num2
                elif operation == "subtract":
                    result = num1 - num2
                elif operation == "multiply":
                    result = num1 * num2
                elif operation == "divide":
                    if num2 == 0:
                        raise ZeroDivisionError
                    result = num1 / num2
                session["last_result"] = result
            except ValueError:
                error_message = "Por favor, insira valores válidos."
            except ZeroDivisionError:
                error_message = "Erro: Divisão por zero não é permitida."
            except Exception as e:
                error_message = f"Erro: {str(e)}"

        return render_template(
            "calculadora.html",
            result=result,
            last_result=session.get("last_result"),
            error_message=error_message,
        )

    @app.route("/moedas")
    @login_required
    def moedas():
        api_url = "https://api.exchangerate-api.com/v4/latest/USD"

        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()

            rates = {
                "USD": 1,
                "BRL": data["rates"].get("BRL", 0),
                "EUR": data["rates"].get("EUR", 0),
                "BTC": data["rates"].get("BTC", 0),
                "ARS": data["rates"].get("ARS", 0),
                "CAD": data["rates"].get("CAD", 0),
                "GBP": data["rates"].get("GBP", 0),
                "JPY": data["rates"].get("JPY", 0),
                "CNY": data["rates"].get("CNY", 0),
                "AUD": data["rates"].get("AUD", 0),
            }

            return render_template("moedas.html", rates=rates)

        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados da API: {str(e)}")
            rates = {}
            return render_template("moedas.html", rates=rates)

    # PRAIAS:
    def criar_slug(texto):
        texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8")
        return texto.lower().replace(" ", "-")

    @app.route("/praias")
    @login_required
    def praias():
        estados = {
            "Rio de Janeiro": "https://praialimpa.net/",
            "São Paulo": "https://praialimpa.net/sao-paulo/",
            "Santa Catarina": "https://praialimpa.net/santa-catarina/",
        }

        praias_limpas = {estado: [] for estado in estados.keys()}

        # Coleta as praias de cada estado
        for estado, url in estados.items():
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")

            praias = soup.find_all("div", class_="beach")
            for praia in praias:
                nome = praia.find("div", class_="name").text.strip()
                localizacao = praia.find("div", class_="location").text.strip()
                status = praia.find("div", class_="status").text.strip()
                praias_limpas[estado].append(
                    {"nome": nome, "localizacao": localizacao, "status": status}
                )

        return render_template("praias.html", praias=praias_limpas)

    @app.route("/praias/<estado>")
    @login_required
    def praias_por_estado(estado):
        estados = {
            "rio-de-janeiro": "https://praialimpa.net/",
            "sao-paulo": "https://praialimpa.net/sao-paulo/",
            "santa-catarina": "https://praialimpa.net/santa-catarina/",
        }

        estado_slug = criar_slug(estado)

        if estado_slug not in estados:
            return "Estado não encontrado", 404

        url = estados[estado_slug]
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        praias_limpas = []

        praias = soup.find_all("div", class_="beach")
        for praia in praias:
            nome = praia.find("div", class_="name").text.strip()
            localizacao = praia.find("div", class_="location").text.strip()
            status = praia.find("div", class_="status").text.strip()
            praias_limpas.append(
                {"nome": nome, "localizacao": localizacao, "status": status}
            )

        return render_template("praias_estado.html", estado=estado, praias=praias_limpas)

    # Bloco de notas::

    @app.route("/bloco-de-notas", methods=["GET", "POST"])
    @login_required
    def bloco_de_notas():
        db = get_db()

        if request.method == "POST":
            note_content = request.form["note"]
            user_id = session.get("user_id")
            db.execute(
                "INSERT INTO note (content, user_id) VALUES (?, ?)",
                (note_content, user_id),
            )
            db.commit()
            flash("Nota salva com sucesso!")
            return redirect(url_for("bloco_de_notas"))

        notes = db.execute(
            "SELECT id, content FROM note WHERE user_id = ?", (session.get("user_id"),)
        ).fetchall()

        return render_template("bloco_notas.html", notes=notes)

    @app.route("/download_note/<int:note_id>")
    @login_required
    def download_note(note_id):
        db = get_db()
        note = db.execute(
            "SELECT content FROM note WHERE id = ? AND user_id = ?",
            (note_id, session.get("user_id")),
        ).fetchone()

        if note:
            return send_file(
                io.BytesIO(note["content"].encode("utf-8")),
                as_attachment=True,
                download_name=f"note_{note_id}.txt",
            )
        flash("Nota não encontrada ou você não tem permissão para acessá-la.")
        return redirect(url_for("bloco_de_notas"))

    @app.route("/delete_note/<int:note_id>", methods=["DELETE"])
    @login_required
    def delete_note(note_id):
        db = get_db()
        db.execute(
            "DELETE FROM note WHERE id = ? AND user_id = ?",
            (note_id, session.get("user_id")),
        )
        db.commit()
        return jsonify({"message": "Nota excluída com sucesso!"}), 200

    # Gestão financeira::

    # Funções para manipular despesas e salários
    def get_expenses(user_id):
        file_path = os.path.join(app.instance_path, f"expenses_{user_id}.csv")
        if os.path.exists(file_path):
            with open(file_path, mode="r", newline="") as file:
                reader = csv.DictReader(file)
                return [
                    {**row, "valor": float(row["valor"])} for row in reader
                ]
        return []

    def save_expense(user_id, despesa, valor):
        file_path = os.path.join(app.instance_path, f"expenses_{user_id}.csv")
        file_exists = os.path.exists(file_path)
        with open(file_path, mode="a", newline="") as file:
            fieldnames = ["despesa", "valor"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({"despesa": despesa, "valor": valor})

    def delete_expense(user_id, despesa_id):
        file_path = os.path.join(app.instance_path, f"expenses_{user_id}.csv")
        temp_file_path = os.path.join(app.instance_path, f"expenses_{user_id}_temp.csv")

        with open(file_path, mode="r", newline="") as file, open(
                temp_file_path, mode="w", newline=""
        ) as temp_file:
            reader = csv.DictReader(file)
            writer = csv.DictWriter(temp_file, fieldnames=reader.fieldnames)
            writer.writeheader()

            for row in reader:
                if row["despesa"] != despesa_id:
                    writer.writerow(row)

        os.replace(temp_file_path, file_path)

    def get_salary(user_id):
        file_path = os.path.join(app.instance_path, f"salary_{user_id}.csv")
        if os.path.exists(file_path):
            with open(file_path, mode="r", newline="") as file:
                reader = csv.DictReader(file)
                salary_row = list(reader)
                if salary_row:
                    return float(
                        salary_row[0]["salary"]
                    )  
        return 0.0

    def save_salary(user_id, salary):
        file_path = os.path.join(app.instance_path, f"salary_{user_id}.csv")
        with open(file_path, mode="w", newline="") as file:
            fieldnames = ["salary"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({"salary": salary})

    @app.route("/gestao-financeira", methods=["GET", "POST"])
    @login_required
    def gestao_financeira():
        user_id = session.get("user_id")

        if request.method == "POST":
            if "salary" in request.form:
                salary = float(
                    request.form["salary"]
                    .replace("R$ ", "")
                    .replace(".", "")
                    .replace(",", ".")
                )
                save_salary(user_id, salary)
                flash("Salário registrado com sucesso!")
            elif "despesa" in request.form:
                despesa = request.form["despesa"]
                valor_str = (
                    request.form["valor"]
                    .replace("R$ ", "")
                    .replace(".", "")
                    .replace(",", ".")
                )
                valor = float(valor_str)
                save_expense(user_id, despesa, valor)
                flash("Despesa registrada com sucesso!")
            elif "delete_expense" in request.form:
                despesa_id = request.form["delete_expense"]
                delete_expense(user_id, despesa_id)
                flash("Despesa excluída com sucesso!")
            return redirect(url_for("gestao_financeira"))

        despesas = get_expenses(user_id)
        salario = get_salary(user_id)
        total_despesas = sum(float(d["valor"]) for d in despesas)
        saldo = salario - total_despesas

        return render_template(
            "gestao_financeira.html",
            despesas=despesas,
            salario=salario,
            total_despesas=total_despesas,
            saldo=saldo,
        )

    @app.route("/download-expenses")
    @login_required
    def download_expenses():
        user_id = session.get("user_id")
        file_path = os.path.join(app.instance_path, f"expenses_{user_id}.csv")
        return send_file(file_path, as_attachment=True)

    return app
