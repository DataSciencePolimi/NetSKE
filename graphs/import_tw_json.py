import pandas as pd
import numpy as np
import re

import json

import os
import sys

def filterString(string):
    strOut = string.replace('\r',' ').replace('\n',' ').replace('\t',' ')
    return strOut

domain = sys.argv[1]	
path = 'data-seed/{}/'.format(domain)
with open(os.listdir(path)[0], 'r') as seedfile:
    seed = json.load(seedfile)
	
tweet_header = 'id_tweet\tid_user\tscreen_name\tlang\tfavourite_count\tcreate_at\tretweet_count\ttext\n'
mention_header = 'id_tweet\tid_user\tscreen_name\n'
hashtag_header = 'id_tweet\ttag\n'
user_header = 'id_user\tscreen_name\n'
with open(path+'user.csv', 'w') as userfile:
    with open(path+'tweet.csv', 'w') as tweetfile:
        with open(path+'mention.csv', 'w') as mentionfile:
            with open(path+'tag.csv', 'w') as tagfile:
                tweetfile.write(tweet_header)
                mentionfile.write(mention_header)
                tagfile.write(hashtag_header)
                userfile.write(user_header)
                for user in candidates:
                    for tweet in candidates[user]:
                        #  tweet data
                        id_tweet = tweet['_id']
                        id_user = tweet['id_user']
                        screen_name = tweet['screen_name'].lower()
                        lang = tweet['lang']
                        fav_count = tweet['favourite_count']
                        timestamp = tweet['create_at']
                        rt_count = tweet['retweet_count']
                        text = filterString(tweet['text']).encode('utf-8')
                        tweetrow = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(id_tweet,id_user,screen_name,lang,fav_count,timestamp,rt_count,text)
                        tweetfile.write(tweetrow)
                        
                        # hashtag data
                        p = re.compile("(?<=^|(?<=[^a-zA-Z0-9-_\.]))#([A-Za-z]+[A-Za-z0-9]+)")
                        hashtags = p.findall(text)
                        for tag in hashtags:
                            tagrow = '{}\t{}\n'.format(id_tweet, tag.lower())
                            tagfile.write(tagrow)

                        # mention data
                        mentions = tweet['mentions']
                        for m in mentions:
                            id_user_mentioned = m['id']
                            screen_name_mentioned = m['screen_name'].lower()
                            mentionrow = '{}\t{}\t{}\n'.format(id_tweet, id_user_mentioned, screen_name_mentioned)
                            mentionfile.write(mentionrow)
                        
                    # user data
                    userrow = '{}\t{}\n'.format(id_user,screen_name)
                    userfile.write(userrow)
 
# print statistics
u = pd.read_csv(path+'user.csv', sep='\t')
t = pd.read_csv(path+'tweet.csv', sep='\t', quoting=3)
m = pd.read_csv(path+'mention.csv', sep='\t')
h = pd.read_csv(path+'tag.csv', sep='\t')

print 'Seeds: {}'.format(u.shape[0])
print 'Tweets: {}'.format(t.shape[0])
print 'Hashtags: {}'.format(h.shape[0])
print 'Unique Hashtags: {}'.format(len(h['tag'].unique()))
print 'Mentions: {}'.format(m.shape[0])
print 'Unique Mentions: {}'.format(len(m['id_user'].unique()))