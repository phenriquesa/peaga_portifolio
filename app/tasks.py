from celery.schedules import crontab
from feedparser import parse
from celery import Celery

app = Celery('rss_updater', broker='pyamqp://guest@localhost//')

app.conf.beat_schedule = {
    'atualizar-feeds': {
        'task': 'tasks.atualizar_feeds',
        'schedule': crontab(minute='*/10'),
    },
}


# Função para atualizar feeds
@app.task
def update_rss_feed(rss_url):
    rss_urls = [
        'https://g1.globo.com/dynamo/brasil/rss2.xml',
    ]

    for rss_url in rss_urls:
        feed = parse(rss_url)
