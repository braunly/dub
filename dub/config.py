from base64 import b64decode

import environs

environ = environs.Env()
if environ.bool("READ_ENV", True):
    environ.read_env(".env")

# Flask core settings
DEBUG = environ.bool("DEBUG", False)

# Authorization token
AUTH_TOKEN = environ.str("AUTH_TOKEN", "ACCESS TOKEN")

# Texture's upload folder
MEDIA_ROOT = environ.str("MEDIA_ROOT", "media/")

# Database connections
DB_URL = environ.str("DB_URL", "mongodb://{user}:{password}@{host}:{port}/{db}")

PRIVATE_RSA_KEY = b64decode(environ.str('PRIVATE_RSA_KEY'))
PUBLIC_RSA_KEY = b64decode(environ.str('PUBLIC_RSA_KEY'))
