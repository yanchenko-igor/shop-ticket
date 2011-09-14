# Django settings for satchmo project.
# This is a recommended base setting for further customization
import os

DIRNAME = os.path.dirname(__file__)

DJANGO_PROJECT = 'store'
DJANGO_SETTINGS_MODULE = 'store.settings'

ADMINS = (
     ('Yanchenko Igor', 'yanchenko.igor@gmail.com'),         # tuple (name, email) - important for error reports sending, if DEBUG is disabled.
)

MANAGERS = ADMINS

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'Europe/Kiev'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'ru'
USE_I18N = True

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
# Image files will be stored off of this path
#
# If you are using Windows, recommend using normalize_path() here
#
# from satchmo_utils.thumbnail import normalize_path
# MEDIA_ROOT = normalize_path(os.path.join(DIRNAME, 'static/'))
MEDIA_ROOT = os.path.join(DIRNAME, 'static/')

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL="/static/"

STATIC_URL="/media/"

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'r2d$af@=#ri5md5n1u2=r%h2u1-^86q#2p^-1%!6kn(7i5f%t8'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.doc.XViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "threaded_multihost.middleware.ThreadLocalMiddleware",
    "satchmo_store.shop.SSLMiddleware.SSLRedirect",
    #"satchmo_ext.recentlist.middleware.RecentProductMiddleware",
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

#this is used to add additional config variables to each request
# NOTE: If you enable the recent_products context_processor, you MUST have the
# 'satchmo_ext.recentlist' app installed.
TEMPLATE_CONTEXT_PROCESSORS = ('satchmo_store.shop.context_processors.settings',
                               'django.contrib.auth.context_processors.auth',
                               'store.localsite.context_processors.categories',
                               'satchmo_ext.recentlist.context_processors.recent_products',
                               )

ROOT_URLCONF = 'store.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(DIRNAME,'templates'),
)
FIXTURE_DIRS = [
    os.path.join(DIRNAME, 'fixtures'),
]

INSTALLED_APPS = (
    'django.contrib.sites',
    'satchmo_store.shop',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.comments',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.formtools',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'tagging',
    'registration',
    'sorl.thumbnail',
    'keyedcache',
    'livesettings',
    'l10n',
    'satchmo_utils.thumbnail',
    'satchmo_store.contact',
    'tax',
    'tax.modules.no',
    'tax.modules.area',
    'tax.modules.percent',
    'shipping',
    #'satchmo_store.contact.supplier',
    #'shipping.modules.tiered',
    'satchmo_ext.newsletter',
    'satchmo_ext.recentlist',
    #'testimonials',         # dependency on  http://www.assembla.com/spaces/django-testimonials/
    'product',
    'product.modules.configurable',
    'product.modules.custom',
    #'product.modules.downloadable',
    'product.modules.subscription',
    #'satchmo_ext.product_feeds',
    #'satchmo_ext.brand',
    'payment',
    #'payment.modules.dummy',
    'payment.modules.cod',
    #'payment.modules.purchaseorder',
    #'payment.modules.giftcertificate',
    #'satchmo_ext.wishlist',
    #'satchmo_ext.upsell',
    #'satchmo_ext.productratings',
    'satchmo_ext.satchmo_toolbar',
    'satchmo_utils',
    #'shipping.modules.tieredquantity',
    #'satchmo_ext.tieredpricing',
    #'typogrify',            # dependency on  http://code.google.com/p/typogrify/
    #'debug_toolbar',
    'app_plugins',
    'store.localsite',
    'store',
    'debug_toolbar',
    'south',
    'django_extensions',
    'tinymce',
    'flatblocks',
)

AUTHENTICATION_BACKENDS = (
    'satchmo_store.accounts.email-auth.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS' : False,
}

#### Satchmo unique variables ####
from django.conf.urls.defaults import patterns, include, url
SATCHMO_SETTINGS = {
    'SHOP_BASE' : '',
    'MULTISHOP' : False,
    'SHOP_URLS' : patterns('', 
            url(r'^i18n/', include('l10n.urls')),
            url(r'^featured/', 'localsite.views.display_featured', name='localsite_featured'),
            url(r'^related/(?P<id>.*)/$', 'localsite.views.display_related', name='display_related'),
            url(r'^events/$', 'localsite.views.select_event', name='select_event'),
            url(r'^event/(?P<event_id>\d+)/edit/$', 'localsite.views.edit_event', name='edit_event'),
            url(r'^flatpages/$', 'localsite.views.flatpages', name='flatpages'),
            url(r'^flatpage/(?P<flatpage_id>\d+)/$', 'localsite.views.flatpage_editor', name='flatpage_editor'),
            url(r'^tinymce/', include('tinymce.urls')),
            url(r'^ajax_select_city/$', 'localsite.views.ajax_select_city', name='ajax_select_city'),
            url(r'^ajax_select_ticket/$', 'localsite.views.ajax_select_ticket', name='ajax_select_ticket'),
            url(r'^add_ticket/$', 'localsite.views.add_ticket', name='add_ticket'),
            url(r'^wizards/event/$', 'localsite.views.wizard_event', name='wizard_event_step0'),
            url(r'^wizards/event/(?P<step>.*)/$', 'localsite.views.wizard_event'),
            url(r'^$', 'localsite.views.display_recent', name='satchmo_shop_home'),
            url(r'^product/view/bestsellers/$', 'localsite.views.display_bestsellers', name='satchmo_product_best_selling'),
            url(r'^cart/$', 'localsite.views.display', name='satchmo_cart'),
            )
}

SKIP_SOUTH_TESTS=True

TINYMCE_DEFAULT_CONFIG = {
        'mode' : "textareas",
        'theme' : "advanced",
        'plugins' : "autolink,lists,spellchecker,pagebreak,style,layer,table,save,advhr,advimage,advlink,emotions,iespell,inlinepopups,insertdatetime,preview,media,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras,template",
        'theme_advanced_buttons1' : "save,newdocument,|,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,styleselect,formatselect,fontselect,fontsizeselect",
        'theme_advanced_buttons2' : "cut,copy,paste,pastetext,pasteword,|,search,replace,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,cleanup,help,code,|,insertdate,inserttime,preview,|,forecolor,backcolor",
        'theme_advanced_buttons3' : "tablecontrols,|,hr,removeformat,visualaid,|,sub,sup,|,charmap,emotions,iespell,media,advhr,|,print,|,ltr,rtl,|,fullscreen",
        'theme_advanced_buttons4' : "insertlayer,moveforward,movebackward,absolute,|,styleprops,spellchecker,|,cite,abbr,acronym,del,ins,attribs,|,visualchars,nonbreaking,template,blockquote,pagebreak,|,insertfile,insertimage",
        'theme_advanced_toolbar_location' : "top",
        'theme_advanced_toolbar_align' : "left",
        'theme_advanced_statusbar_location' : "bottom",
        'theme_advanced_resizing' : True,
        'relative_urls': False,
        }

TINYMCE_JS_URL = MEDIA_URL + 'js/tiny_mce/tiny_mce.js'
TINYMCE_JS_ROOT = MEDIA_ROOT + 'js/tiny_mce'

# Load the local settings
from local_settings import *
