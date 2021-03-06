import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'pyramid_jinja2',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'bcrypt',
    'nameparser',
    'py-bcrypt',
    'requests',
    'psutil',
    'starter',
    'zodb',
    'transaction',
    'supervisor',
    'cython',
    'oursql'
]

setup(name='hr',
      version='0.0',
      description='hr',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Atish Narlawar',
      author_email='anarlawar@hugeinc.com',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='hr',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = hr:main
      [console_scripts]
      initialize_hr_db = hr.scripts.initializedb:main
      """,
)
