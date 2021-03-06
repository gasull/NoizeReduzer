# Settings specific to the development environment
import sys

#These paths must be added so that Django is aware of all the modules we are using.
# Example: sys.path.append("/home/johndoe/workspace/noizereduzer/",)
sys.path.append('',)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# don't want emails while developing
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'noizereduzer'             # Or path to database file if using sqlite3.
DATABASE_USER = 'nrdev'             # Not used with sqlite3.
DATABASE_PASSWORD = 'password'         # Not used with sqlite3.
DATABASE_HOST = '127.0.0.1'             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = '5432'             # Set to empty string for default. Not used with sqlite3.

# Make this unique, and don't share it with anybody.
# Example: ")i&+g@oht)4tu6=)7t+*g8age_=ijb2x$4$nb$t(ht6y9lz1ka"
SECRET_KEY = ''

INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django_cron',
        #'extensions',
        # NoizeReduzer:
        'folders',
        'users',
)

#  Paths for common JS & CSS files, which can be hosted by a 3rd party
jquery_path = 'http://ajax.googleapis.com/ajax/libs/jquery/1.2.6/jquery.min.js'
yui_css_path = 'http://yui.yahooapis.com/combo?2.6.0/build/reset-fonts-grids/reset-fonts-grids.css&2.6.0/build/base/base-min.css'
