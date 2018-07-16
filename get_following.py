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


MAX_FOLLOWING = 250000

# login to API			
twitterAPI = login()

# select source to gather followers
source = sys.argv[1] # it can be seed or a number (test number)
domain = 'finance_20'

if source == 'seed':
	path = 'graphs/data-seed/{}/'.format(domain)
	userlist = list(pd.read_csv(path+'user.csv', sep='\t')['id_user'])
	ofile2 = open(path+'following.csv', 'w')
else:
	n_test = int(source)
	path = 'graphs/data-random/'
	alltestusers = pd.read_csv(path+'user.csv', sep='\t')
	userlist = list(alltestusers[alltestusers['n_test'] == n_test]['id_user'].unique())
	ofile2 = open(path+'following_{}.csv'.format(n_test), 'w')

writer2 = csv.writer(ofile2, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer2.writerow(['id_follower','id_followed'])


processed = 0 # print percentage variable
startall = time.time()
for id_user in userlist:
	start = time.time()
	print 'Followings of '+str(id_user)

	n_curr_following = 0
	for following in limit_handled(tweepy.Cursor(twitterAPI.friends_ids, user_id=id_user).items()):	
		# store follow relationship
		writer2.writerow([id_user, following])

		n_curr_following += 1
		if n_curr_following >= MAX_FOLLOWING:
			break

	processed = processed + 1
	print 'Completion: {:.1f} %'.format(float(processed)*100/len(userlist))

print 'Overall time needed: {} min'.format((time.time()-startall)/60)
	