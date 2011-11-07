# this is an extremely simple Satchmo standalone store.
# -*- coding: UTF-8 -*-

import logging
import os, os.path
from settings import *

LOCAL_DEV = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG

if LOCAL_DEV:
    INTERNAL_IPS = (
		    '127.0.0.1',
		    '10.0.1.5',
		    '91.90.18.172',
		    '195.43.146.65',
		    )
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    INSTALLED_APPS += ('debug_toolbar',)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS' : False,
}

DIRNAME = os.path.dirname(os.path.abspath(__file__))

SATCHMO_DIRNAME = DIRNAME
    
gettext_noop = lambda s:s

LANGUAGE_CODE = 'ru-ua'
LANGUAGES = (
   ('en', gettext_noop('English')),
   ('ru', gettext_noop('Russian')),
   ('ua', gettext_noop('Ukrainian')),
)

#These are used when loading the test data
SITE_NAME = "simple"

DATABASES = {
    'default': {
        # The last part of ENGINE is 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'ado_mssql'.
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'showua',  # Or path to database file if using sqlite3
        'USER': 'show',             # Not used with sqlite3.
        'PASSWORD': 'feeP6ooJ',         # Not used with sqlite3.
        'HOST': 'localhost',             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',             # Set to empty string for default. Not used with sqlite3.
    }
}

SECRET_KEY = 'ahlohz6ieTahSh6riecaipeevohfaeyahzoongaeShaugai7wei7ienge8oot8ti'

##### For Email ########
# If this isn't set in your settings file, you can set these here
#EMAIL_HOST = 'host here'
#EMAIL_PORT = 587
#EMAIL_HOST_USER = 'your user here'
#EMAIL_HOST_PASSWORD = 'your password'
#EMAIL_USE_TLS = True

#These are used when loading the test data
SITE_DOMAIN = "localhost"
SITE_NAME = "Simple Satchmo"

# not suitable for deployment, for testing only, for deployment strongly consider memcached.
#CACHE_BACKEND = "locmem:///"
CACHE_TIMEOUT = 60*5
#CACHE_PREFIX = "Z"

CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
			'LOCATION': '127.0.0.1:11211',
                        'TIMEOUT':  60*60*5,
		}
	}



ACCOUNT_ACTIVATION_DAYS = 7

L10N_SETTINGS = {
  'currency_formats' : {
     'UAH' : {'symbol': u'₴', 'positive' : u"%(val)0.0f грн.", 'negative': u"(%(val)0.0f грн.)",
         'positivelabel' : u"<label>%(val)0.0f</label> грн.", 'negativelabel': u"(<label>%(val)0.0f</label> грн.)",
               'decimal' : ','},
  },
  'default_currency' : 'UAH',
  'show_admin_translations': False,
  'allow_translation_choice': False,
}

#Configure logging
LOGFILE = "satchmo.log"
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=os.path.join(DIRNAME,LOGFILE),
                    filemode='w')

logging.getLogger('keyedcache').setLevel(logging.INFO)
logging.getLogger('l10n').setLevel(logging.INFO)
logging.info("Satchmo Started")
