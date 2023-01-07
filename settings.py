import os
from dotenv import load_dotenv

CWD = os.getcwd()

if os.path.isfile(os.path.join(CWD, '.env')):
    load_dotenv(os.path.join(CWD, '.env'))
else:
    load_dotenv(os.path.join(CWD, 'src/.env'))


MAGICEDEN_API_KEY = os.getenv("MAGICEDEN_API_KEY")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_KEY_SECRET = os.getenv("TWITTER_API_KEY_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

CONNECTIONS = {
    "superdoppler": f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}",
}