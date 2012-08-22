import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'Markdown',
    'pyramid_jinja2',
    'passlib',
    'py-bcrypt',
    ]

setup(name='trivialblog',
      version='0.0',
      description='trivialblog',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='trivialblog',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = trivialblog:main
      [console_scripts]
      initialize_trivialblog_db = trivialblog.scripts.initializedb:main
      """,
      )

