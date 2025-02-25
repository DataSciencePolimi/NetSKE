import tweepy
import csv
import json
import pandas as pd
import time
import sys

#login
path_credentials = '../credentials.json' #complete path of twitter credentials
def login():
    fileKeys = open(path_credentials).read()

    keys = json.loads(fileKeys)
    auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
    auth.set_access_token(keys['access_token'], keys['access_token_secret'])
    twitter = tweepy.API(auth, wait_on_rate_limit=False)
    return twitter


def limit_handled(cursor):
	while True:
		try:
			yield cursor.next()
		except tweepy.RateLimitError:
			print 'API Rate Limit exceeded. Waiting...'
			time.sleep(15 * 60)
		except tweepy.error.TweepError:
			print 'Connection aborted by peer. Waiting...'
			time.sleep(5 * 60)

# login to API			
twitterAPI = login()

# select source to gather followers
source = sys.argv[1] # it can be seed or a number (test number)
domain = sys.argv[2]

if source == 'seed':
	path = 'graphs/data-seed/{}/'.format(domain)
	userlist = list(pd.read_csv(path+'user.csv', sep='\t')['id_user'])
	ofile = open(path+'user_data.csv', 'w')
else:
	n_test = int(source)
	path = 'graphs/data-random/'
	alltestusers = pd.read_csv(path+'user.csv', sep='\t')
	userlist = list(alltestusers[alltestusers['n_test'] == n_test]['id_user'].unique())
	ofile = open(path+'user_data_{}.csv'.format(n_test), 'w')
'''
ofile = open('graphs/finance_20/random-test/test-network-features/top_followed_data.csv', 'w')
userlist = list(pd.read_csv('graphs/finance_20/random-test/test-network-features/top_followed.csv')['id_user'])
'''

writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer.writerow(['id_user','screen_name','followers','following','lang','location','created_at','link_img','protected'])

processed = 0 # print percentage variable
api_success = False
for id_user in userlist:
	
	while not api_success:
		try:
			u = twitterAPI.get_user(user_id = id_user)
			api_success = True
		except tweepy.RateLimitError:
			print 'API Rate Limit exceeded. Waiting...'
			time.sleep(15 * 60)
		except tweepy.error.TweepError as e:
			print e
			time.sleep(5 * 60)
		
	writer.writerow([u.id, u.screen_name.encode('utf-8'), u.followers_count, u.friends_count, u.lang, u.location.encode('utf-8'), u.created_at, u.profile_image_url,u.protected])
	
	api_success = False
	processed = processed + 1
	print 'Completion: {:.1f} %'.format(float(processed)*100/len(userlist))