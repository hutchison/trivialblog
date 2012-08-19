from pyramid.view import view_config
from markdown import markdown

from .models import (
    DBSession,
    Post,
    )

#@view_config(route_name='home', renderer='templates/basic.jinja2')
@view_config(route_name='home', renderer='templates/basic.jinja2')
def home(request):
    posts = DBSession.query(Post).all()
    return dict(posts=posts)
