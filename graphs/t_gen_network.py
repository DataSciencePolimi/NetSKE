import pandas as pd
import snap
import sys

## NB: ID_NODE == USERNAME because id_user == id_tweet is a thing!!!

def generateTables(targetpath, netfile, net):
	#split file into node and edge file
	net_file = open(targetpath+netfile+'.csv', 'r') 
	nodes_file = open(targetpath+netfile+'_nodes.csv', 'w')
	nodes_file.write('id\tcontent\ttype\tid_node\n')
	edges_file = open(targetpath+netfile+'_edges.csv', 'w')
	edges_file.write('source\ttarget\ttype\n')
	
	n_nodes = net.GetNodes()
	n_edges = net.GetEdges()
	
	line_num = 0 
	for line in net_file:
		if line_num>=4 and line_num < (n_nodes+4) : # 4 headers
			nodes_file.write(line)
		elif line_num >= (n_nodes+6) and line_num < (n_nodes+6+n_edges): #skip #END
			edges_file.write(line)
		line_num = line_num + 1

testtype = sys.argv[1] #can be random or mention
domain = sys.argv[2] # can be finance, finance_20,...

if testtype == 'random':
	datapath = ['data-seed/','data-random/']
elif testtype == 'mention':
	datapath = ['data-seed/','data-candidate/']
	 
outpath = '{}/{}-test/'.format(domain, testtype)

corenodes = pd.DataFrame()
coreedges = pd.DataFrame()
mentionnetnodes = pd.DataFrame()
mentionnetedges = pd.DataFrame()

## USER DATA ##
users = pd.DataFrame()
for p in datapath:
	
	if p == 'data-candidates/':
		u = pd.read_csv(p+domain+'/user.csv', sep='\t')
		u['type'] = 'candidate'
		
	elif p == 'data-seed/':
		u = pd.read_csv(p+domain+'/user.csv', sep='\t')
		u['type'] = 'seed'
		
	elif p == 'data-random/':
		u = pd.read_csv(p+'/user.csv', sep='\t')
		u['type'] = 'user'
	users = pd.concat([users, u])
	
userNodes = users[['id_user', 'screen_name', 'type']]
userNodes.columns = ['content', 'id', 'type']
corenodes = pd.concat([corenodes, userNodes])

## POST DATA ##
postdata = pd.DataFrame()
for p in datapath:
	if p == 'data-random/':
		post = pd.read_csv(p+'/tweet.csv', sep='\t', quoting=3)[['id_tweet','screen_name', 'lang']]
	else:
		post = pd.read_csv(p+domain+'/tweet.csv', sep='\t', quoting=3)[['id_tweet','screen_name', 'lang']]
	postdata = pd.concat([postdata, post])
	
postdata.drop_duplicates(subset='id_tweet', inplace=True)
postnodes = postdata[['id_tweet', 'lang']]
postnodes.columns = ['id', 'content']
postnodes['type'] = 'tweet'
corenodes = pd.concat([corenodes, postnodes])
print '|V_post|: {}'.format(postnodes.shape[0])

#add post-user relationship
postedges = postdata[['id_tweet','screen_name']]
postedges.columns = ['target', 'source']
postedges['e_type'] = 'tweet'
coreedges = pd.concat([coreedges, postedges])
print '|E_post|: {}'.format(postedges.shape[0])

## TAG DATA ##
tagdata = pd.DataFrame()
for p in datapath:
	if p == 'data-random/':
		t = pd.read_csv(p+'/tag.csv', sep='\t')
	else:
		t = pd.read_csv(p+domain+'/tag.csv', sep='\t')
	tagdata = pd.concat([tagdata, t])

tagnodes = tagdata[['tag']].drop_duplicates()
tagnodes.columns = ['id'] # key
tagnodes['content'] = tagnodes.apply(lambda x: x['id'], axis=1) # content same as key for hashtags
tagnodes['type'] = 'tag'
tagnetnodes = pd.concat([corenodes, tagnodes])
print '|V_tag|: {}'.format(tagnodes.shape[0])

#add post-tag relationship
tagedges = tagdata[['id_tweet', 'tag']]
tagedges.columns = ['source', 'target']
tagedges['e_type'] = 'tag'
tagnetedges = pd.concat([coreedges, tagedges])
print '|E_tag|: {}'.format(tagedges.shape[0])

## MENTION DATA ##
mentiondata = pd.DataFrame()
for p in datapath:
	if p == 'data-random/':
		m = pd.read_csv(p+'/mention.csv', sep='\t')
	else:
		m = pd.read_csv(p+domain+'/mention.csv', sep='\t')
	mentiondata = pd.concat([mentiondata, m])
		
mentionnodes = mentiondata[['id_user', 'screen_name']].drop_duplicates()
mentionnodes.columns = ['content', 'id']
mentionnodes['type'] = 'user'
		
mentionnetnodes = pd.concat([corenodes, mentionnodes])
mentionnetnodes = mentionnetnodes.drop_duplicates(subset='id')

print '|V_mentioned|: {}'.format(mentionnodes.shape[0])

#add mention relationship
mentionedges = mentiondata[['id_tweet', 'screen_name']]
mentionedges.columns = ['source','target']
mentionedges['e_type'] = 'mention'
mentionnetedges = pd.concat([coreedges, mentionedges])
print '|E_mentioned|: {}'.format(mentionedges.shape[0])


nodefile = 'temp/nodes.csv'
edgefile = 'temp/edges.csv'
## COMPLETE NETWORK FILES ##
pd.concat([mentionnetnodes, tagnodes]).to_csv(nodefile, index = None)
pd.concat([mentionnetedges, tagedges]).to_csv(edgefile, index = None)


## NETWORK CONSTRUCTION ##
e_schema = snap.Schema()
e_schema.Add(snap.TStrTAttrPr("e_type", snap.atStr))
e_schema.Add(snap.TStrTAttrPr("source", snap.atStr))
e_schema.Add(snap.TStrTAttrPr("target", snap.atStr)) 

n_schema = snap.Schema()
n_schema.Add(snap.TStrTAttrPr("content", snap.atStr))
n_schema.Add(snap.TStrTAttrPr("id", snap.atStr))
n_schema.Add(snap.TStrTAttrPr("type", snap.atStr))

#define TTable objects of edges and nodes
context = snap.TTableContext()
edgetable = snap.TTable.LoadSS(e_schema, edgefile, context, ",", snap.TBool(True))
nodetable = snap.TTable.LoadSS(n_schema, nodefile, context, ",", snap.TBool(True))

#define (if any) attribute names using SNAP string vectors
edgeattrv = snap.TStrV()
edgeattrv.Add("e_type")

nodeattrv = snap.TStrV()
nodeattrv.Add("content")
nodeattrv.Add("type")
nodeattrv.Add("id")

#build SNAP network using the two TTable objects
net = snap.ToNetwork(snap.PNEANet, edgetable, "source", "target", edgeattrv, nodetable, "id", nodeattrv, snap.aaFirst)
print '|V| = {}'.format(net.GetNodes())
print '|E| = {}'.format(net.GetEdges()) 
print 'Connected network: {}'.format(snap.IsConnected(net))

networkname = 'c_network'

#save network for metadata and visualization
snap.SaveEdgeListNet(net, outpath+networkname+'.csv', 'Complete Network - {} domain'.format(domain))
generateTables(outpath, networkname, net)

#save network for node2vec input
snap.SaveEdgeList(net, outpath+networkname+'.edgelist')

#save network for relaoding and manipulation
fOut = snap.TFOut(outpath+networkname+'.bin')
net.Save(fOut)
fOut.Flush()