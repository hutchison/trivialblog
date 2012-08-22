from sqlalchemy import (
    Column,
    Integer,
    Text,
    Date,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

from passlib.context import CryptContext
pwd_context = CryptContext(
        schemes=['bcrypt'],
        default='bcrypt',
        )

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    headline = Column(Text)
    content = Column(Text)
    pdate = Column(Date)

    def __init__(self, h, c, d):
        self.headline = h
        self.content = c
        self.pdate = d


from pyramid.security import (
        Allow,
        Everyone,
        )

class User(Base):
    __tablename__ = 'users'
    name = Column(Text, primary_key=True)
    password = Column(Text)
    groups = Column(Text)

    def __init__(self, n, pw, gr=''):
        self.name = n
        self.password = pwd_context.encrypt(pw)
        self.groups = gr

class RootFactory(object):
    __acl__ = [(Allow, Everyone, 'view'),
            (Allow, 'editors', 'edit'),
            (Allow, 'admins', 'edit_users'),
            ]
    def __init__(self, request):
        pass
