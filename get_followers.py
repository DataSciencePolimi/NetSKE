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
domain = 'finance_20'

if source == 'seed':
	path = 'graphs/data-seed/{}/'.format(domain)
	userlist = list(pd.read_csv(path+'user.csv', sep='\t')['id_user'])[14:]
	ofile2 = open(path+'follower.csv', 'a')
else:
	n_test = int(source)
	path = 'graphs/data-random/'
	#alltestusers = pd.read_csv(path+'user.csv', sep='\t')
	#userlist = list(alltestusers[alltestusers['n_test'] == n_test]['id_user'][:56].unique())
	userlist = [61,66,67,82,320,355,388,430,443,455,519,737,795,842,849,893,946,947,1199,3077,4267,6585,7306,7389,7548,8353,8458,8499,9320,9406,12601,13058,13658,15883,19773,28143,\
			31023,34123,34203,51793,55033,78883,1485051,6936172,9258192,9656292,9736242,19812908,20325834,22329929,27774936,31991535,34033955,35343252,36958712,37187445,42285575,\
			43619077,47688274,47855059,48558004,50018576,53562231,55368724,57902288,62985293,64742913,66267377,66842010,71994935,73562496,76741437,79969037,86124652,90386145,\
			96954724,134084824,193280501,245891047,303264766,308523811,491821618,584963133,741036103,807442880,837198475,860061325,1865120570,2451857593,4902972795]
	ofile2 = open(path+'follower_{}.csv'.format(n_test), 'a')

writer2 = csv.writer(ofile2, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#writer2.writerow(['id_follower','id_followed'])

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
	