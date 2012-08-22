from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from .security import groupfinder, get_auth_secret

from .models import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    config = Configurator(settings=settings,
        root_factory='trivialblog.models.RootFactory')

    config.include('pyramid_jinja2')

    authn_policy = AuthTktAuthenticationPolicy(get_auth_secret(),
        callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('view.post', '/p/{id}')
    config.add_route('add.post', '/add.post')
    config.add_route('add.user', '/add.user')
    config.scan()
    return config.make_wsgi_app()
