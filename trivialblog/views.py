import locale
locale.setlocale(locale.LC_ALL, 'de_DE')

from pyramid.view import view_config
from markdown import markdown
from sqlalchemy import desc

from .models import (
    DBSession,
    Post,
    )

@view_config(route_name='home', renderer='templates/basic.jinja2')
def home(request):
    posts = DBSession.query(Post).order_by(Post.pdate.desc()).all()
    return dict(posts=posts)
