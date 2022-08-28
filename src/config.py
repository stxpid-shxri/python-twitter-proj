import os

import tweepy as tweepy
from dotenv import load_dotenv

load_dotenv()

TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')
TWITTER_API_KEY_SECRET = os.environ.get('TWITTER_API_KEY_SECRET')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

AUTH_CONFIG = tweepy.OAuth1UserHandler(
    TWITTER_API_KEY, TWITTER_API_KEY_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
)
