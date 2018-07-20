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

if domain == 'random':
	path = 'data-random/'
	user_header = 'id_user\tscreen_name\tn_test\n'
else:
	path = 'data-seed/{}/'.format(domain)
	user_header = 'id_user\tscreen_name\n'

filenames = [f for f in os.listdir(path) if 'tweets' in f]

tweet_header = 'id_tweet\tid_user\tscreen_name\tlang\tfavourite_count\tretweet_count\ttext\n'
mention_header = 'id_tweet\tid_user\tscreen_name\n'
hashtag_header = 'id_tweet\ttag\n'

it = 0
with open(path+'user.csv', 'a') as userfile:
	with open(path+'tweet.csv', 'a') as tweetfile:
		with open(path+'mention.csv', 'a') as mentionfile:
			with open(path+'tag.csv', 'a') as tagfile:
			
				for f in filenames:
					with open(path+f, 'r') as seedfile:
						seed = json.load(seedfile)
					
					if domain == 'random':
						n_test = f.split('_')[2]
						print 'Test Data - {}'.format(n_test)
						
					if it == 0:
						tweetfile.write(tweet_header)
						mentionfile.write(mention_header)
						tagfile.write(hashtag_header)
						userfile.write(user_header)
						
					for user in seed:
						for id_tweet in seed[user]:
							#  tweet data
							tweet = seed[user][id_tweet]

							id_user = tweet['id_user']
							screen_name = tweet['screen_name'].lower()
							lang = tweet['lang']
							fav_count = tweet['favourite_count']
							#timestamp = tweet['create_at']
							rt_count = tweet['retweet_count']
							text = filterString(tweet['text']).encode('utf-8')
							tweetrow = '{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(id_tweet,id_user,screen_name,lang,fav_count,rt_count,text)
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
						if domain == 'random':
							userrow = '{}\t{}\t{}\n'.format(id_user,screen_name, n_test)
						else:
							userrow = '{}\t{}\n'.format(id_user,screen_name)
						userfile.write(userrow)
					
					it = it + 1
					
# print statistics (seeds file only)
u = pd.read_csv(path+'user.csv', sep='\t').drop_duplicates()
t = pd.read_csv(path+'tweet.csv', sep='\t', quoting=3).drop_duplicates()
m = pd.read_csv(path+'mention.csv', sep='\t').drop_duplicates()
h = pd.read_csv(path+'tag.csv', sep='\t').drop_duplicates()

print 'Seeds: {}'.format(u.shape[0])
print 'Tweets: {}'.format(t.shape[0])
print 'Hashtags: {}'.format(h.shape[0])
print 'Unique Hashtags: {}'.format(len(h['tag'].unique()))
print 'Mentions: {}'.format(m.shape[0])
print 'Unique Mentions: {}'.format(len(m['id_user'].unique()))

# rewrite without duplicates (fashion has one)
u.to_csv(path+'user.csv', sep='\t', index=None)
t.to_csv(path+'tweet.csv', sep='\t', quoting=3, index=None)
m.to_csv(path+'mention.csv', sep='\t', index=None)
h.to_csv(path+'tag.csv', sep='\t', index=None)