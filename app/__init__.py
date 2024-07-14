import os
<<<<<<< HEAD
from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.urandom(64),
=======
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
import textwrap
from flask import Flask, render_template, request
import requests
from . import tasks
from .db import get_db
from .blog import get_post


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
>>>>>>> dfcd81a (Atualização de arquivos)
        DATABASE=os.path.join(app.instance_path, 'db.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
<<<<<<< HEAD
# Init DB
    from . import db
    db.init_app(app)

    from . import site
    app.register_blueprint(site.bp)
    app.add_url_rule('/', endpoint='index')
=======

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/blog', endpoint='blog')

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    rss_url = 'https://g1.globo.com/dynamo/tecnologia/rss2.xml'

    # 'https://g1.globo.com/dynamo/brasil/rss2.xml',
    # 'https://g1.globo.com/dynamo/concursos-e-emprego/rss2.xml',
    # 'https://g1.globo.com/dynamo/economia/rss2.xml',
    # 'https://g1.globo.com/dynamo/musica/rss2.xml',
    # 'https://g1.globo.com/dynamo/planeta-bizarro/rss2.xml',
    # 'https://g1.globo.com/dynamo/tecnologia/rss2.xml',
    # 'https://g1.globo.com/dynamo/turismo-e-viagem/rss2.xml'

    # current_rss_url_index = 0  # Índice da URL RSS atual

    @app.route('/noticias')
    def noticias():
        try:
            feed = feedparser.parse(rss_url)
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
            feed = feedparser.parse(rss_url)
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

    @app.route('/projetos')
    def projetos():
        return render_template('projetos.html')
>>>>>>> dfcd81a (Atualização de arquivos)

    return app
