import pandas as pd
import snap
import sys

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

path = '{}/{}-test/'.format(domain, testtype)

nodefile = 'temp/nodes.csv'
edgefile = 'temp/edges.csv'

# merge followers of seeds and test 1
seed_followers_nodes = pd.read_csv(path+'followers_network_nodes.csv')
seed_followers_edges = pd.read_csv(path+'followers_network_edges.csv')
test_followers_nodes = pd.read_csv(path+'test-network-features/followers_network_nodes.csv')
test_followers_edges = pd.read_csv(path+'test-network-features/followers_network_edges.csv')

allnodes = pd.concat([seed_followers_nodes, test_followers_nodes])
allnodes.drop_duplicates(inplace=True)
allnodes.to_csv(nodefile, index=None)

alledges = pd.concat([seed_followers_edges, test_followers_edges])
alledges.drop_duplicates(inplace=True)
alledges.to_csv(edgefile, index=None)


## NETWORK CONSTRUCTION ##
e_schema = snap.Schema()
e_schema.Add(snap.TStrTAttrPr("source", snap.atStr))
e_schema.Add(snap.TStrTAttrPr("target", snap.atStr)) 

n_schema = snap.Schema()
n_schema.Add(snap.TStrTAttrPr("id", snap.atStr))
n_schema.Add(snap.TStrTAttrPr("followers", snap.atFlt))
n_schema.Add(snap.TStrTAttrPr("following", snap.atFlt))

#define TTable objects of edges and nodes
context = snap.TTableContext()
edgetable = snap.TTable.LoadSS(e_schema, edgefile, context, ",", snap.TBool(True))
nodetable = snap.TTable.LoadSS(n_schema, nodefile, context, ",", snap.TBool(True))

#define (if any) attribute names using SNAP string vectors
edgeattrv = snap.TStrV()

nodeattrv = snap.TStrV()
nodeattrv.Add("id")
nodeattrv.Add("followers")
nodeattrv.Add("following")

#build SNAP network using the two TTable objects
net = snap.ToNetwork(snap.PNEANet, edgetable, "source", "target", edgeattrv, nodetable, "id", nodeattrv, snap.aaFirst)
print '|V| = {}'.format(net.GetNodes())
print '|E| = {}'.format(net.GetEdges()) 
print 'Connected network: {}'.format(snap.IsConnected(net))

networkname = 'social_network_1'
outpath = path+'test-network-features/'

#save network for metadata and visualization
snap.SaveEdgeListNet(net, outpath+networkname+'.csv', 'Social Network using followers')
generateTables(outpath, networkname, net)

#save network for node2vec input
snap.SaveEdgeList(net, outpath+networkname+'.edgelist')

#save network for relaoding and manipulation
#fOut = snap.TFOut(outpath+networkname+'.bin')
#net.Save(fOut)
#fOut.Flush()

