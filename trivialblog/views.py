# -*- coding: utf-8 -*-
import locale
locale.setlocale(locale.LC_ALL, 'de_DE')

from pyramid.view import (
        view_config,
        forbidden_view_config,
        )
from pyramid.security import (
        remember,
        forget,
        authenticated_userid,
        )
from .security import get_password_hash, groupfinder
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
    pwd_context,
    User,
    )

@view_config(route_name='home', renderer='home.jinja2', permission='view')
def home(request):
    """Die Startseite.
        Zeigt die letzten 10 Posts an."""
    posts = DBSession.query(Post).order_by(Post.pdate.desc()).limit(10)
    gr = groupfinder(authenticated_userid(request))
    return dict(posts=posts,
            groups = gr,
            logged_in=authenticated_userid(request),
            login_url=request.route_url('login'),
            logout_url=request.route_url('logout'),
            add_url=request.route_url('add.post'),
            view_url=request.route_url('view.post', id=''),
            add_user_url=request.route_url('add.user'),
            )

@view_config(route_name='view.post', renderer='view_post.jinja2',
    permission='view')
def view_post(request):
    """Zeigt einen bestimmten Post an."""
    postid = request.matchdict['id']
    post = DBSession.query(Post).filter_by(id=postid).first()
    if post is None:
        return HTTPNotFound('Kein Blogpost mit der ID ' + str(postid) +
            ' vorhanden.')
    else:
        gr = groupfinder(authenticated_userid(request))
        return dict(p=post,
                groups = gr,
                logged_in=authenticated_userid(request),
                home_url=request.route_url('home'),
                login_url=request.route_url('login'),
                logout_url=request.route_url('logout'),
                )

@view_config(route_name='add.post', renderer='add_post.jinja2',
    permission='edit.posts')
@forbidden_view_config(route_name='add.post', renderer='login.jinja2')
def add_post(request):
    if 'submitting' in request.params:
        title = request.params['headline']
        text = request.params['text']
        if title == '' or text == '':
            errmsg = 'Titel oder Inhalt waren leer.'
            return dict(status=errmsg,
                    add_url=request.route_url('add.post'),
                    )
        pdate = date.today()
        p = Post(title, text, pdate)
        DBSession.add(p)
        return HTTPFound(location=request.route_url('home'))
    elif 'rendering' in request.params:
        title = request.params['headline']
        text = request.params['text']
        pdate = date.today()
        return dict(title=title, text=text, pdate=pdate,
                add_url=request.route_url('add.post'),
                )
    else:
        gr = groupfinder(authenticated_userid(request))
        return dict(logged_in=authenticated_userid(request),
                add_url=request.route_url('add.post'),
                )

@view_config(route_name='login', renderer='login.jinja2')
def login(request):
    if 'submitting' in request.params:
        login = request.params.get('login', '')
        password = request.params.get('password', '')
        pw_hash = get_password_hash(login)
        if pw_hash and pwd_context.verify(password, pw_hash):
            headers = remember(request, login)
            return HTTPFound(location=request.application_url,
                    headers=headers)
        else:
            errmsg = u'Böser Login!'
            return dict(message=errmsg)
    else:
        return dict()

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location=request.route_url('home'),
            headers=headers)

@view_config(route_name='add.user', renderer='add_user.jinja2',
        permission='edit.users')
@forbidden_view_config(route_name='add.user', renderer='login.jinja2')
def add_user(request):
    if 'submitting' in request.params:
        user = request.params.get('username', '')
        pw = request.params.get('password', '')
        if user == '' or pw == '':
            errmsg = 'Nutzer oder Passwort sind leer! Nix gemacht.'
            return dict(status=errmsg, statustype='error')
        else:
            gr = request.params.get('groups', '')
            u = User(user, pw, gr)
            DBSession.add(u)
            msg = unicode(user) + u' erfolgreich hinzugefügt.'
            return dict(status=msg, statustype='success')
    else:
        gr = groupfinder(authenticated_userid(request))
        return dict(logged_in=authenticated_userid(request),
                groups=gr,
                )
