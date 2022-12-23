import tweepy
from dagster import resource
import urllib.request
import io

import settings


class Twitter:
    API_KEY = settings.TWITTER_API_KEY
    API_SECRET = settings.TWITTER_API_KEY_SECRET
    BEARER_TOKEN = settings.TWITTER_BEARER_TOKEN
    ACCESS_TOKEN = settings.TWITTER_ACCESS_TOKEN
    ACCESS_SECRET = settings.TWITTER_ACCESS_TOKEN_SECRET

    def __init__(self):
        self.set_auth()
        self.set_api_client()

    def get_client(self):
        return tweepy.Client(
            consumer_key=self.API_KEY,
            consumer_secret=self.API_SECRET,
            access_token=self.ACCESS_TOKEN,
            access_token_secret=self.ACCESS_SECRET
        )

    def set_api_client(self):
        self.api = tweepy.API(self.auth)

    def post_tweet_media(self, text: str, media_filepath: str):
        r = self.api.update_status_with_media(media_filepath, text)
        return r

    def post_tweet_with_uri_image(self, text, uri):
        data = urllib.request.urlopen(uri).read()
        file_like_object = io.BytesIO(data)
        r = self.api.update_status_with_media(text, 'nft_image.png', file=file_like_object)
        return r

    def post_tweet(self, text):
        r = self.api.update_status(text)
        return r

    def set_auth(self):
        self.auth = tweepy.OAuthHandler(
            consumer_key=self.API_KEY,
            consumer_secret=self.API_SECRET
        )
        self.auth.set_access_token(
            key=self.ACCESS_TOKEN,
            secret=self.ACCESS_SECRET
        )

    def verify_credentials(self):
        try:
            self.api.verify_credentials()
            print("Authentication OK")
        except:
            print("Error during authentication")

    @staticmethod
    def update_status(client, status: str):
        r = client.create_tweet(text=status)
        return r


@resource(
    description="Twitter resource to access API"
)
def twitter(init_context):
    return Twitter()
