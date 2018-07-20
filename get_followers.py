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
		except tweepy.error.TweepError as e:
			print e
			time.sleep(5 * 60)

# login to API			
twitterAPI = login()

# select source to gather followers
source = sys.argv[1] # it can be seed or a number (test number)
domain = sys.argv[2]

if source == 'seed':
	path = 'graphs/data-seed/{}/'.format(domain)
	userdata = pd.read_csv(path+'user.csv')[['id_user', 'protected']]
	userlist = list(userdata[userdata['protected'] == False]['id_user'])

	if userdata.shape[0] != len(userlist):
		print 'Protected users in the list. Removed from following collection!'

	ofile2 = open(path+'follower.csv', 'a')
else:
	n_test = int(source)
	path = 'graphs/data-random/'
	alltestusers = pd.read_csv(path+'user_data.csv', sep='\t')
	userlist = list(alltestusers[alltestusers['n_test'] == n_test]['id_user'].unique())
	ofile2 = open(path+'follower_{}.csv'.format(n_test), 'a')

writer2 = csv.writer(ofile2, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer2.writerow(['id_follower','id_followed'])

MAX_FOLLOWERS = 250000
processed = 0 # print percentage variable
startall = time.time()
for id_user in userlist:
	start = time.time()
	print 'Followers of '+str(id_user)

	n_curr_followers = 0
	for follower in limit_handled(tweepy.Cursor(twitterAPI.followers_ids, user_id=id_user).items()):	
		# store follow relationship
		writer2.writerow([follower, id_user])

		n_curr_followers += 1
		if n_curr_followers >= MAX_FOLLOWERS:
			break

	processed = processed + 1
	print 'Completion: {:.1f} %'.format(float(processed)*100/len(userlist))

print 'Overall time needed: {} min'.format((time.time()-startall)/60)
	