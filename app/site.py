from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

bp = Blueprint('site', __name__)


@bp.route('/')
def index():
    return render_template('site/index.html')


@bp.route('/sobre')
def sobre():
    return render_template('site/sobre.html')


@bp.route('/projetos')
def projetos():
    return render_template('site/projetos.html')
