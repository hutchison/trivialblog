# -*- coding: utf-8 -*-

from .models import (
        DBSession,
        User,
        AuthSecret,
        )

def get_auth_secret():
    return DBSession.query(AuthSecret.secret).one().scalar()

def get_password_hash(userid):
    pw_hash = DBSession.query(User.password).filter_by(name=userid).scalar()
    return pw_hash

def groupfinder(userid, request=''):
    groups = DBSession.query(User.groups).filter_by(name=userid).scalar() or ''
    return groups.split(',')
