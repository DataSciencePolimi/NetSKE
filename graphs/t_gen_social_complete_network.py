import pandas as pd
import snap
import sys

def generateTables(targetpath, netfile, net):
	#split file into node and edge file
	net_file = open(targetpath+netfile+'.csv', 'r') 
	nodes_file = open(targetpath+netfile+'_nodes.csv', 'w')
	nodes_file.write('id\tfollowers\tfollowing\tid_user\n')
	edges_file = open(targetpath+netfile+'_edges.csv', 'w')
	edges_file.write('source\ttarget\n')
	
	n_nodes = net.GetNodes()
	n_edges = net.GetEdges()
	
	line_num = 0 
	for line in net_file:
		if line_num>=4 and line_num < (n_nodes+4) : # 4 headers
			nodes_file.write(line)
		elif line_num >= (n_nodes+6) and line_num < (n_nodes+6+n_edges): #skip #END
			edges_file.write(line)
		line_num = line_num + 1

domain = sys.argv[2] # can be finance, finance_20,...

path = '{}/random-test/test-network-features/'.format(domain)

nodefile = 'temp/nodes.csv'
edgefile = 'temp/edges.csv'

# merge followers of seeds and test 1
allnodes = pd.DataFrame()
alledges = pd.DataFrame()
for relationship in ['followers', 'following']:
    seed_f_nodes = pd.read_csv(path+relationship+'_network_nodes.csv')
    seed_f_edges = pd.read_csv(path+relationship+'_network_edges.csv')
    test_f_nodes = pd.read_csv('data-random/{}_network_nodes_1.csv'.format(relationship))
    test_f_edges = pd.read_csv('data-random/{}_network_edges_1.csv'.format(relationship))

    allnodes = pd.concat([allnodes, seed_f_nodes, test_f_nodes])
    alledges = pd.concat([alledges, seed_f_edges, test_f_edges])
    
allnodes.drop_duplicates(inplace=True)
allnodes.to_csv(nodefile, index=None)
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

networkname = 'social_network_1_complete'

#save network for metadata and visualization
snap.SaveEdgeListNet(net, path+networkname+'.csv', 'Social Network using both relationships')
generateTables(path, networkname, net)

#save network for node2vec input
snap.SaveEdgeList(net, path+networkname+'.edgelist')


