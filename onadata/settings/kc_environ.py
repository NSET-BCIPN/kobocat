import os
from onadata.settings.common import *

DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'
TEMPLATE_DEBUG = os.environ.get('TEMPLATE_DEBUG', 'True') == 'True'
TEMPLATE_STRING_IF_INVALID = ''

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

import dj_database_url

DATABASES = {
    'default': dj_database_url.config(default="sqlite:///%s/db.sqlite3" % BASE_DIR)
}

MONGO_DATABASE = {
    'HOST': os.environ.get('KOBOCAT_MONGO_HOST', 'localhost'),
    'PORT': int(os.environ.get('KOBOCAT_MONGO_PORT', 27017)),
    'NAME': os.environ.get('KOBOCAT_MONGO_NAME', 'formhub'),
    'USER': os.environ.get('KOBOCAT_MONGO_USER', ''),
    'PASSWORD': os.environ.get('KOBOCAT_MONGO_PASS', '')
}

BROKER_URL = os.environ.get(
    'KOBOCAT_BROKER_URL', 'amqp://guest:guest@localhost:5672/')

try:
    SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
except KeyError:
    raise Exception('DJANGO_SECRET_KEY must be set in the environment.')

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(' ')

TESTING_MODE = False
# This trick works only when we run tests from the command line.
if len(sys.argv) >= 2 and (sys.argv[1] == "test"):
    raise Exception(
        "Testing destroys data and must NOT be run in a production "
        "environment. Please use a different settings file if you want to "
        "run tests."
    )
    TESTING_MODE = True
else:
    TESTING_MODE = False

MEDIA_URL= os.environ.get('KOBOCAT_MEDIA_URL', 'http://localhost:8001/media/')

if TESTING_MODE:
    MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'test_media/')
    subprocess.call(["rm", "-r", MEDIA_ROOT])
    MONGO_DATABASE['NAME'] = "formhub_test"
    CELERY_ALWAYS_EAGER = True
    BROKER_BACKEND = 'memory'
    ENKETO_API_TOKEN = 'abc'
    #TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'
else:
    MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media/')

if PRINT_EXCEPTION and DEBUG:
    MIDDLEWARE_CLASSES += ('utils.middleware.ExceptionLoggingMiddleware',)

# Clear out the test database
if TESTING_MODE:
    MONGO_DB.instances.drop()

# include the kobocat-template directory
TEMPLATE_OVERRIDE_ROOT_DIR = os.environ.get(
    'KOBOCAT_TEMPLATES_PATH',
    os.path.join(PROJECT_ROOT, '..', 'kobocat-template')
)
TEMPLATE_DIRS = ( os.path.join(PROJECT_ROOT, TEMPLATE_OVERRIDE_ROOT_DIR, 'templates'), ) + TEMPLATE_DIRS
STATICFILES_DIRS += ( os.path.join(PROJECT_ROOT, TEMPLATE_OVERRIDE_ROOT_DIR, 'static'), )

KOBOFORM_SERVER=os.environ.get("KOBOFORM_SERVER", "localhost")
KOBOFORM_SERVER_PORT=os.environ.get("KOBOFORM_SERVER_PORT", "8000")
KOBOFORM_SERVER_PROTOCOL=os.environ.get("KOBOFORM_SERVER_PROTOCOL", "http")
KOBOFORM_LOGIN_AUTOREDIRECT=True
KOBOFORM_URL=os.environ.get("KOBOFORM_URL", "http://localhost:8000")

TEMPLATE_CONTEXT_PROCESSORS = (
    'onadata.koboform.context_processors.koboform_integration',
) + TEMPLATE_CONTEXT_PROCESSORS

MIDDLEWARE_CLASSES = ('onadata.koboform.redirect_middleware.ConditionalRedirects', ) + MIDDLEWARE_CLASSES

CSRF_COOKIE_DOMAIN = os.environ.get('CSRF_COOKIE_DOMAIN', None)

if CSRF_COOKIE_DOMAIN:
    SESSION_COOKIE_DOMAIN = CSRF_COOKIE_DOMAIN
    SESSION_COOKIE_NAME = 'kobonaut'

SESSION_SERIALIZER='django.contrib.sessions.serializers.JSONSerializer'

# for debugging
# print "KOBOFORM_SERVER=%s" % KOBOFORM_SERVER
# print "SECRET_KEY=%s" % SECRET_KEY
# print "CSRF_COOKIE_DOMAIN=%s " % CSRF_COOKIE_DOMAIN

# MongoDB - moved here from common.py
if MONGO_DATABASE.get('USER') and MONGO_DATABASE.get('PASSWORD'):
    MONGO_CONNECTION_URL = (
        "mongodb://%(USER)s:%(PASSWORD)s@%(HOST)s:%(PORT)s") % MONGO_DATABASE
else:
    MONGO_CONNECTION_URL = "mongodb://%(HOST)s:%(PORT)s" % MONGO_DATABASE

MONGO_CONNECTION = MongoClient(
    MONGO_CONNECTION_URL, safe=True, j=True, tz_aware=True)
MONGO_DB = MONGO_CONNECTION[MONGO_DATABASE['NAME']]

# BEGIN external service integration codes
AWS_ACCESS_KEY_ID = os.environ.get('KOBOCAT_AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('KOBOCAT_AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('KOBOCAT_AWS_STORAGE_BUCKET_NAME')
AWS_DEFAULT_ACL = 'private'

GOOGLE_ANALYTICS_PROPERTY_ID = os.environ.get("GOOGLE_ANALYTICS_TOKEN", False)
GOOGLE_ANALYTICS_DOMAIN = "auto"
# END external service integration codes

DEFAULT_FILE_STORAGE = os.environ.get('KOBOCAT_DEFAULT_FILE_STORAGE')

EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND',
    'django.core.mail.backends.filebased.EmailBackend')

if EMAIL_BACKEND == 'django.core.mail.backends.filebased.EmailBackend':
    EMAIL_FILE_PATH = os.environ.get(
        'EMAIL_FILE_PATH', os.path.join(BASE_DIR, 'emails'))
    if not os.path.isdir(EMAIL_FILE_PATH):
        os.mkdir(EMAIL_FILE_PATH)

# Optional Sentry configuration: if desired, be sure to install Raven and set
# RAVEN_DSN in the environment
if 'RAVEN_DSN' in os.environ:
    try:
        import raven
    except ImportError:
        print 'Please install Raven to enable Sentry logging.'
    else:
        INSTALLED_APPS = INSTALLED_APPS + (
            'raven.contrib.django.raven_compat',
        )
        RAVEN_CONFIG = {
            'dsn': os.environ['RAVEN_DSN'],
        }
        try:
            RAVEN_CONFIG['release'] = raven.fetch_git_sha(BASE_DIR)
        except raven.exceptions.InvalidGitRepository:
            pass
