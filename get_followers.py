import tweepy
import csv
import json
import pandas as pd
import time

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

# login to API			
twitterAPI = login()
domain = 'finance_20'
path = 'graphs/data-seed/{}/'.format(domain)

seed_list = list(pd.read_csv(path+'user.csv')['id_user'])
ofile = open(path+'follower_data.csv', 'w')
ofile2 = open(path+'follower.csv', 'w')

writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer.write(['id_user','screen_name','followers','following','lang','location','created_at','link_img'])

writer2 = csv.writer(ofile2, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer2.write(['id_follower','id_followed'])

allusers = list(pd.read_csv(path+'user.csv')['id_user'])
start = time.time()
for id_seed in seed_list:
	print 'Followers of '+str(id_seed)
	for follower in limit_handled(tweepy.Cursor(twitterAPI.followers, user_id=id_seed).items()):
		# to avoid duplicate metadata
		if follower.id not in allusers:
			f_row = [follower.id, follower.screen_name, follower.followers_count, follower.friends_count, follower.lang, follower.location, follower.created_at,follower.profile_image_url]
			writer.writerow(f_row)
			allusers.append(follower.id)
			
		# store follow relationship
		writer2.writerow([follower.id, id_seed])
	print 'Time needed: {} s'.format(time.time()-start)

print 'Overall time needed: {} min'.format((time.time()-start)/60)
	