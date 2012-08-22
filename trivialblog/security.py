# -*- coding: utf-8 -*-

from .models import (
        DBSession,
        User,
        )

def get_auth_secret():
    try:
        with open('AUTH_SECRET', 'rb') as f:
            return f.read()
    except IOError:
        with open('AUTH_SECRET', 'w') as f, open('/dev/urandom') as u:
            S = u.read(20)
            f.write(S)
            return S

def get_password_hash(userid):
    pw_hash = DBSession.query(User.password).filter_by(name=userid).scalar()
    return pw_hash

def groupfinder(userid, request=''):
    groups = DBSession.query(User.groups).filter_by(name=userid).scalar() or ''
    return groups.split(',')
