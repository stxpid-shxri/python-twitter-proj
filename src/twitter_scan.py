import datetime
import logging
import math
from typing import List, Tuple
from numpy.core import array
import numpy as np
import pandas as pd
import tweepy
from pandas import DataFrame
from tweepy.api import API
from tweepy.models import Status

from config import AUTH_CONFIG

logging.basicConfig(level=logging.INFO, filename='../twitter_scan.log')
logger = logging.getLogger(__name__)


def get_tweets(client: API):
    screen_name = 'y00tlist'
    start_at = None
    tweets = []
    while True:
        t = client.user_timeline(screen_name=screen_name,
                                 count=200,  # 200 is the maximum allowed count
                                 include_rts=False,
                                 max_id=None if start_at is None else start_at - 1,
                                 tweet_mode='extended')  # Necessary to keep > 140 chars

        if not t:
            break

        tweets.extend(t)
        logger.info(f'Fetched tweets: [{"Newest Tweet" if start_at is None else start_at} - {t.max_id}]')
        start_at = t.max_id - 1

    return tweets


def get_valid_users(tweets: List[Status]) -> List[Tuple[int, str]]:
    users = []
    valid_str = 'Your application for @y00tsNFT has been accepted'
    for tweet in tweets:

        if len(tweet.entities['user_mentions']) != 2:
            logger.error(f'Couldn\'t find user for {tweet.full_text}.')

        elif valid_str not in tweet.full_text:
            continue

        else:
            user = tweet.entities['user_mentions'][0]['id']
            user_id = tweet.entities['user_mentions'][0]['screen_name']
            users.append((user, user_id))

    return users


def get_user_details(client, users: List[Tuple[int, str]]):
    rows = []
    columns = ['id', 'name', 'username', 'following', 'followers', 'tweets', 'days_since_join']

    # Split Array into Evenly Sized Chunks (<= 100 items)
    user_chunks = np.array_split(users, math.ceil(len(users) / 100))

    user_details = []
    for chunk in user_chunks:
        user_details.extend(client.lookup_users(user_id=[user[0] for user in chunk], include_entities=False))

    # Get Relevant Data and Prepare for Dataframe
    for user in user_details:
        days_since = abs((user.created_at - datetime.datetime.now(datetime.timezone.utc)).days)
        rows.append(
            [str(user.id), user.name, user.screen_name, user.friends_count, user.followers_count, user.statuses_count,
             days_since])

    return DataFrame(rows, columns=columns)


def bucket_data(df: DataFrame, column_bins: List[Tuple[str, array, List[str]]]) -> DataFrame:
    for col in column_bins:
        buckets = pd.cut(df[col[0]].to_list(), col[1]).rename_categories(col[2])
        df[f"{col[0]}_bucket"] = buckets
    return df


def main(save_path: str = None):
    client = tweepy.API(AUTH_CONFIG)
    users = get_user_details(client, get_valid_users(get_tweets(client)))

    column_bins = [
        ('following',
         np.array([0, 500, 2_500, 5_000, 10_000, 50_000, 100_000, 500_000, 1_000_000, 10_000_000, 100_000_000]),
         ['0-500', '500-2500', '2.5-5K', '5-10K', '10-50K', '50-100K', '100-500K', '500K-1M', '1-10M, 10-100M',
          '100M+']),

        ('followers',
         np.array([0, 500, 2_500, 5_000, 10_000, 50_000, 100_000, 500_000, 1_000_000, 10_000_000, 100_000_000]),
         ['0-500', '500-2500', '2.5-5K', '5-10K', '10-50K', '50-100K', '100-500K', '500K-1M', '1-10M, 10-100M',
          '100M+']),

        ('tweets',
         np.array([0, 500, 2_500, 5_000, 10_000, 50_000, 100_000, 500_000, 1_000_000, 10_000_000, 100_000_000]),
         ['0-500', '500-2500', '2.5-5K', '5-10K', '10-50K', '50-100K', '100-500K', '500K-1M', '1-10M, 10-100M',
          '100M+']),

        ('days_since_join',
         np.array([1, 90, 180, 365, 365 * 3, 365 * 5, 365 * 10, 365 * 20]),
         ['< 3 Mo.', '3-6 Mo.', '6-12 Mo.', '1-3 Yr.', '3-5 Yr.', '5-10 Yr.', '10+ Yr.']),
    ]
    bucketed = bucket_data(users, column_bins)
    if save_path is not None:
        bucketed.to_csv(save_path, index=False)


if __name__ == '__main__':
    main('output.csv')
