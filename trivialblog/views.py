import locale
locale.setlocale(locale.LC_ALL, 'de_DE')

from pyramid.view import view_config
from markdown import markdown
from sqlalchemy import desc

from datetime import date

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )

from .models import (
    DBSession,
    Post,
    )

@view_config(route_name='home', renderer='home.jinja2')
def home(request):
    """Die Startseite.
        Zeigt die letzten 10 Posts an."""
    posts = DBSession.query(Post).order_by(Post.pdate.desc()).limit(10)
    return dict(posts=posts)

@view_config(route_name='view_post', renderer='view_post.jinja2')
def view_post(request):
    """Zeigt einen bestimmten Post an."""
    postid = request.matchdict['id']
    post = DBSession.query(Post).filter_by(id=postid).first()
    if post is None:
        return HTTPNotFound('Kein Blogpost mit der ID ' + str(postid) +
            ' vorhanden.')
    else:
        return dict(p=post)

@view_config(route_name='add_post', renderer='add_post.jinja2')
def add_post(request):
    if 'form.submitted' in request.params:
        title = request.params['headline']
        text = request.params['text']
        if title == '' or text == '':
            errmsg = 'Titel oder Inhalt waren leer.'
            return dict(status=errmsg)
        pdate = date.today()
        p = Post(title, text, pdate)
        DBSession.add(p)
        return HTTPFound(location=request.application_url)
    else:
        return dict()
