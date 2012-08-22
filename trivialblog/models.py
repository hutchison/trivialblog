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

class RootFactory(object):
    __acl__ = [(Allow, Everyone, 'view'),
            (Allow, 'editors', 'edit'),
            ]
    def __init__(self, request):
        pass
