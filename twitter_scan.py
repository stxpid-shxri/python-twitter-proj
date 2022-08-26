import configparser
import tweepy
import pandas as pd
from datetime import datetime

def get_fourth_elem(elem):
    return elem[3]

def days_between(d2):
    d1 = datetime.now().date()
    d2 = d2.date()
    return abs((d2 - d1).days) / 30

#get config data parser
config = configparser.ConfigParser()
config.read('config.ini')

api_key = config['twitter_keys']['api_key']
api_key_secret = config['twitter_keys']['api_secret_key']
access_key = config['twitter_keys']['access_key']
access_key_secret = config['twitter_keys']['access_secret_key']

auth = tweepy.OAuth1UserHandler(
   api_key, api_key_secret, access_key, access_key_secret
)

api = tweepy.API(auth)
screen_name = 'y00tlist'
substring = 'Your application for @y00tsNFT has been accepted'
count = 0
users = []
tweets = api.user_timeline(screen_name=screen_name, 
                           # 200 is the maximum allowed count
                           count=200,
                           include_rts = False,
                           # Necessary to keep full_text 
                           # otherwise only the first 140 words are extracted
                           tweet_mode = 'extended'
                           )
for info in tweets:
    if substring in info.full_text:
        count += 1
        oldest_id = info.id
        for mentions in info.entities['user_mentions']:
            if mentions['screen_name'] != 'y00tsNFT':
                users.append(mentions['id'])
    else:
        print("not found")

while True:
    tweets = api.user_timeline(screen_name=screen_name, 
                           # 200 is the maximum allowed count
                           count=200,
                           include_rts = False,
                           max_id = oldest_id - 1,
                           # Necessary to keep full_text 
                           # otherwise only the first 140 words are extracted
                           tweet_mode = 'extended'
                           )
    if len(tweets) == 0:
        break
    for info in tweets:
        if substring in info.full_text:
            count += 1
            oldest_id = info.id
            for mentions in info.entities['user_mentions']:
                if mentions['screen_name'] != 'y00tsNFT':
                    users.append(mentions['id'])
        else:
            print("not found")

#storage
data = []
columns = ['Id', 'Twitter Name', 'Created at', 'Follower Count']
followerRows = ['< 500', '> 500 && < 2500', '>2501 && < 5000', '>5001 && < 10k', '>10k && < 50k', '>50k && < 100k', '>100k && < 500k', '>500k && < 1m', '>1m', 'Total']
dateRows = ['< 3mo', '>3mo && < 6mo', '> 6mo && < 1y', '< 1y && > 3y', '>3y', 'Total']

# # of followers group
less_500 = 0
greater_500 = 0
greater_2500 = 0
greater_5000 = 0
greater_10k = 0
greater_50k = 0
greater_100k = 0
greater_500k = 0
greatest = 0

# months created
less_3mo = 0
greater_3mo = 0
greater_6mo = 0
greater_1y = 0
greater_3y = 0

# variable
start = 0
end = 100
remaining = count

while True:
    user_details = api.lookup_users(user_id=users[start:end], include_entities=False)
    remaining = remaining - (end - start)
    start = end
    end += 100 if remaining > 100 else remaining 
    for user in user_details:
        data.append([user.id, user.screen_name, user.created_at, user.followers_count])
        if user.followers_count < 500:
            less_500 +=1
        elif user.followers_count >= 500 and user.followers_count <=2500:
            greater_500 +=1
        elif user.followers_count >= 2501 and user.followers_count <=5000:
            greater_2500 +=1
        elif user.followers_count >= 5001 and user.followers_count <=10000:
            greater_5000 +=1
        elif user.followers_count >= 10001 and user.followers_count <=50000:
            greater_10k +=1
        elif user.followers_count >= 50001 and user.followers_count <=100000:
            greater_50k +=1
        elif user.followers_count >= 100001 and user.followers_count <=500000:
            greater_100k +=1
        elif user.followers_count >= 500001 and user.followers_count < 1000000:
            greater_500k +=1
        elif user.followers_count > 1000001:
            greatest +=1
        
        months_created = days_between(user.created_at)
        if months_created < 3:
            less_3mo += 1
        elif months_created > 3 and months_created < 6:
            greater_3mo += 1
        elif months_created > 6 and months_created < 12:
            greater_6mo += 1
        elif months_created > 12 and months_created < 36:
            greater_1y += 1
        elif months_created > 36:
            greater_3y +=1

    if remaining == 0:
        break
    

series = [less_500, greater_500, greater_2500, greater_5000, greater_10k, greater_50k, greater_100k, greater_500k, greatest, len(data)]
dateSeries = [less_3mo, greater_3mo, greater_6mo, greater_1y, greater_3y, len(data)]


data.sort(key=get_fourth_elem)
df = pd.DataFrame(data, columns=columns)
ser = pd.Series(series, index=followerRows)
dateSer = pd.Series(dateSeries, index=dateRows)
df2 = pd.DataFrame({'# of followers':ser.index, 'total # of users':ser.values})
df3 = pd.DataFrame({'twitter date created':dateSer.index, 'total # of users':dateSer.values})

df2.to_csv("yootlist_overview.csv", index=False)
df3.to_csv("yootlist_overview.csv", index=False, mode="a")
df.to_csv("yootlist_overview.csv", index=False, mode="a")
