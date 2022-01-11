import environs

environ = environs.Env()
if environ.bool("READ_ENV", True):
    environ.read_env(".env")

# Flask core settings
DEBUG = environ.bool("DEBUG", False)
HOST = environ.str("HOST", "0.0.0.0")
PORT = environ.int("PORT", 8080)

# Authorization token
AUTH_TOKEN = environ.str("AUTH_TOKEN", "ACCESS TOKEN")

# Texture's upload folder
MEDIA_ROOT = environ.str("MEDIA_ROOT", "media/")

# Database connections
DB_URL = environ.str("DB_URL", "mongodb://{user}:{password}@{host}:{port}/{db}")
