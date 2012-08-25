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
from sqlalchemy.orm.exc import NoResultFound

from datetime import date
import re

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
    posts = DBSession.query(Post).order_by(Post.pdate.desc(),
            Post.id.desc()).limit(10)
    return dict(
            posts=posts,
            groups=groupfinder(authenticated_userid(request)),
            logged_in=authenticated_userid(request),
            )

@view_config(route_name='view.post', renderer='view_post.jinja2',
    permission='view')
def view_post(request):
    """Zeigt einen bestimmten Post an."""
    postid = request.matchdict['postid']
    post = DBSession.query(Post).filter_by(id=postid).first()
    if post is None:
        return HTTPNotFound('Kein Blogpost mit der ID ' + str(postid) +
            ' vorhanden.')
    else:
        return dict(p=post,
                groups=groupfinder(authenticated_userid(request)),
                logged_in=authenticated_userid(request),
                )

@view_config(route_name='add.post', renderer='add_post.jinja2',
    permission='edit.posts')
@forbidden_view_config(route_name='add.post', renderer='login.jinja2')
def add_post(request):
    ret = dict(
            groups=groupfinder(authenticated_userid(request)),
            logged_in=authenticated_userid(request),
            )
    if 'submitting' in request.params:
        title = request.params['headline']
        text = request.params['text']
        if title == '' or text == '':
            errmsg = 'Titel oder Inhalt waren leer.'
            ret.update(status=errmsg, statustype='error')
            return ret
        pdate = date.today()
        p = Post(title, text, pdate)
        DBSession.add(p)
        return HTTPFound(location=request.route_url('home'))
    elif 'rendering' in request.params:
        title = request.params['headline']
        text = request.params['text']
        pdate = date.today()
        ret.update(title=title, text=text, pdate=pdate)
        return ret
    else:
        return ret

@view_config(route_name='edit.post', renderer='edit_post.jinja2',
        permission='edit.posts')
@forbidden_view_config(route_name='edit.post', renderer='login.jinja2')
def edit_post(request):
    postid = request.matchdict['postid']
    post = DBSession.query(Post).filter_by(id=postid).first()
    ret = dict(post=post,
            groups=groupfinder(authenticated_userid(request)),
            logged_in=authenticated_userid(request),
            )
    # Matcht das Datenformat, was wir brauchen:
    datematcher = re.compile('^\d{4}-\d{2}-\d{2}$')

    if 'submitting' in request.params:
        newheadline = request.params['headline']
        newcontent = request.params['content']
        if datematcher.match(request.params['pdate']):
            d = map(int,request.params['pdate'].split('-'))
            newdate = date(d[0], d[1], d[2])
        else:
            newdate = post.pdate
        if not newheadline and newcontent:
            msg = u'Titel oder Inhalt leer! Nix passiert.'
            ret.update(status=msg, statustype='error')
            return ret
        else:
            post.headline = newheadline
            post.content = newcontent
            post.pdate = newdate
            return HTTPFound(location=request.route_url('view.post',
                postid=postid))
    elif 'rendering' in request.params:
        rendheadline = request.params['headline']
        rendcontent = request.params['content']
        if datematcher.match(request.params['pdate']):
            d = map(int,request.params['pdate'].split('-'))
            renddate = date(d[0], d[1], d[2])
        else:
            renddate = post.pdate
        ret.update(ptitle=rendheadline,
                pcontent=rendcontent,
                pdate=renddate
                )
        return ret
    else:
        if post is None:
            return HTTPNotFound('Kein Blogpost mit der ID ' + str(postid) +
                ' vorhanden.')
        else:
            return ret

@view_config(route_name='delete.post', renderer='delete_post.jinja2',
        permission='edit.posts')
@forbidden_view_config(route_name='delete.post', renderer='login.jinja2')
def delete_post(request):
    postid = request.matchdict['postid']
    post = DBSession.query(Post).filter_by(id=postid).first()
    ret = dict(post=post,
            groups=groupfinder(authenticated_userid(request)),
            logged_in=authenticated_userid(request),
            )
    if 'submitting' in request.params:
        DBSession.delete(post)
        msg = u'Post ' + str(postid) + u' gelöscht'
        ret.update(status=msg, statustype='success')
        return ret
    else:
        if post is None:
            return HTTPNotFound('Kein Blogpost mit der ID ' + str(postid) +
                ' vorhanden.')
        else:
            return ret


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
    ret = dict(
            logged_in=authenticated_userid(request),
            groups=groupfinder(authenticated_userid(request)),
            )
    if 'submitting' in request.params:
        user = request.params.get('username', '')
        pw = request.params.get('password', '')
        pwrpt = request.params.get('passwordrpt', '')
        if user == '' or pw == '':
            msg = 'Nutzer oder Passwort sind leer! Nix passiert.'
            msgtype = 'error'
        elif pw != pwrpt:
            msg = u'Passwörter stimmen nicht überein. Nix passiert'
            msgtype = 'error'
        else:
            gr = request.params.get('groups', '')
            u = User(user, pw, gr)
            DBSession.add(u)
            msg = unicode(user) + u' erfolgreich hinzugefügt.'
            msgtype = 'success'
        ret.update(status=msg, statustype=msgtype)
    return ret

@view_config(route_name='edit.user', renderer='edit_user.jinja2',
        permission='edit.users')
@forbidden_view_config(route_name='edit.user', renderer='login.jinja2')
def edit_user(request):
    ul = DBSession.query(User).all()
    return dict(
            users=ul,
            groups=groupfinder(authenticated_userid(request)),
            )

@view_config(
        route_name='edit.user.details', renderer='edit_user_details.jinja2',
        permission='edit.users',
        )
@forbidden_view_config(route_name='edit.user.details', renderer='login.jinja2')
def edit_user_details(request):
    uid = request.matchdict.get('userid', '')
    try:
        u = DBSession.query(User).filter_by(name=uid).one()
    except NoResultFound:
        errmsg = unicode(uid) + u' nicht vorhanden!'
        return dict(
                user='',
                status=errmsg,
                statustype='error'
                )
    else:
        if 'submitting' in request.params:
            newname = request.params['username']
            newpw = request.params['password']
            newpwrpt = request.params['passwordrpt']
            newgr = request.params['groups']
            if newpw != '':
                if newpw != newpwrpt:
                    msg = u'Passwörter stimmen nicht überein! Keine Änderung.'
                    return dict(
                        user=u,
                        status=msg,
                        statustype='error',
                        )
                else:
                    u = DBSession.merge(User(newname, newpw, newgr))
                    msg = u'Alles geändert.'
            else:
                oldname = u.name
                oldgroups = u.groups
                u.name = newname
                u.groups = newgr
                msg = u"""<h4>Änderungen</h4>
                Name von „%s“ nach „%s“<br/>
                Gruppen von „%s“ nach „%s“""" % (oldname, u.name,
                        oldgroups, u.groups)
            return dict(
                    user=u,
                    status=msg,
                    statustype='success',
                    )
        else:
            return dict(
                    user=u,
                    groups=groupfinder(authenticated_userid(request)),
                    )


@view_config(route_name='delete.user')
def delete_user(request):
    return HTTPFound(location=request.route_url('home'))
