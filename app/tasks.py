from celery.schedules import crontab
from feedparser import parse
from celery import Celery

app = Celery('rss_updater', broker='pyamqp://guest@localhost//')

app.conf.beat_schedule = {
    'atualizar-feeds': {
        'task': 'tasks.atualizar_feeds',
        'schedule': crontab(minute='*/5'),
    },
}


# Função para atualizar feeds
@app.task
def update_rss_feed(rss_url):
    rss_urls = [
        'https://g1.globo.com/rss/g1/',
        'https://g1.globo.com/dynamo/loterias/rss2.xml',
        'https://g1.globo.com/rss/g1/carros/',
        'https://g1.globo.com/dynamo/ciencia-e-saude/rss2.xml',
        'https://g1.globo.com/dynamo/concursos-e-emprego/rss2.xml',
        'https://g1.globo.com/dynamo/economia/rss2.xml',
        'https://g1.globo.com/dynamo/educacao/rss2.xml',
        'https://g1.globo.com/dynamo/mundo/rss2.xml',
        'https://g1.globo.com/dynamo/musica/rss2.xml',
        'https://g1.globo.com/dynamo/natureza/rss2.xml',
        'https://g1.globo.com/dynamo/planeta-bizarro/rss2.xml',
        'https://g1.globo.com/rss/g1/politica/',
        'https://g1.globo.com/rss/g1/pop-arte/',
        'https://g1.globo.com/dynamo/tecnologia/rss2.xml',
        'https://g1.globo.com/dynamo/turismo-e-viagem/rss2.xml'
    ]

    for rss_url in rss_urls:
        feed = parse(rss_url)
