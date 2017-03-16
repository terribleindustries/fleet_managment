import os

#Tornado settings
STATIC_PATH = os.path.join(os.path.dirname(__file__), "static")
TORNADO_SECRET = 'aaaaaaaa'
XSRF_COOKIES = False


root = os.path.dirname(__file__)
template_root = os.path.join(root, 'templates')
blacklist_templates = ('layouts',)

#DB settings, this user will be created and granted permissions.
DB_USER_USER = 'db_user'
DB_USER_PASS = 'db_pass'

BASEDIR=''

#HTTP Settings
HTTPS = False
HTTPS_PORT = 443
HTTP_PORT = 8080
CERTFILE = BASEDIR + "/path/to/cert"
KEYFILE = BASEDIR + "/path/to/key"

#Login settings
ADMIN_KEY = 'super_secure_key'
API_KEY = 'PlaceRandomStringHere'

#jinja2 settings
JINJA2_SETTINGS = {
    'sidenav':False,
   'navbar':True,
}

#Arrow settings
HUMANIZE = True #If false, will use exact time settings below
DATE_FORMAT = 'YYYY-MM-DD HH:mm:ss'
TIMEZONE = 'US/Central'

#Number settings
MAX_NUMBER = 100 #inclusive


#Users settings:
USE_BCRYPT = True
