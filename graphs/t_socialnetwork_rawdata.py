import pandas as pd
import sys

domain = sys.argv[1]
relationship = sys.argv[2] # follower/following


if domain == 'random':
	path = 'data-random/'
	outpath = 'data-random/'
	suffix = '_1' # n_test
	header = [u'created_at', u'followers', u'following', u'id', u'lang', u'link_img', u'location', u'screen_name']
else:
	path = 'data-seed/{}/'.format(domain)
	outpath = '{}/random-test/test-network-features/'.format(domain)
	suffix = ''
	header = [u'created_at', u'followers', u'following', u'id', u'lang', u'link_img', u'location', u'protected', u'screen_name']


followers = pd.read_csv(path+relationship+suffix+'.csv')
userdata = pd.read_csv(path+'user_data'+suffix+'.csv')

if relationship == 'follower':
	nometadatafield = 'id_follower'
elif relationship == 'following':
	nometadatafield = 'id_followed'

# filter users that have too many followers in test 1!
followers = followers[~followers['id_followed'].isin([12,13])]
userdata = userdata[~userdata['id_user'].isin([12,13])]
	
nometadata = followers[[nometadatafield]].drop_duplicates()
nometadata.columns = ['id_user']

nodes = pd.concat([userdata, nometadata])
nodes['followers'] = nodes.apply(lambda x: x['followers'] if not pd.isnull(x['followers']) else 1, axis=1)
nodes['following'] = nodes.apply(lambda x: x['following'] if not pd.isnull(x['following']) else 1, axis=1)
nodes.columns = header
nodes.drop_duplicates(subset='id', inplace=True)
nodes[['id','followers','following']].to_csv(outpath+relationship+'_network_nodes'+suffix+'.csv', index=None)

followers.columns = ['source', 'target']
followers.to_csv(outpath+relationship+'_network_edges'+suffix+'.csv', index=None)