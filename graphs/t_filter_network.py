import numpy as np
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


def rebuildContent(graph, subgraph):
	
	# readd attributes
	subgraph.AddStrAttrN('id')
	subgraph.AddStrAttrN('content')
	subgraph.AddStrAttrN('type')
	subgraph.AddStrAttrE('e_type')
	
	it = subgraph.BegNI()
	for i in range(subgraph.GetNodes()):
		nid = it.GetId()
		id_entity = graph.GetStrAttrDatN(nid, 'id')
		type = graph.GetStrAttrDatN(nid, 'type')
		content = graph.GetStrAttrDatN(nid, 'content')
		
		subgraph.AddStrAttrDatN(nid, id_entity, 'id')
		subgraph.AddStrAttrDatN(nid, content, 'content')	
		subgraph.AddStrAttrDatN(nid, type, 'type')
		
		it.Next()
		
	ite = subgraph.BegEI()
	
	for j in range (subgraph.GetEdges()):
		sourceid = ite.GetSrcNId()
		targetid = ite.GetDstNId()
		eid = graph.GetEI(sourceid, targetid)
		
		subgraph.AddStrAttrDatE(ite.GetId(), graph.GetStrAttrDatE(eid, 'e_type'), 'e_type')
		ite.Next()
		
def buildSubNetwork(net, networktype):
	mention_edges = snap.TIntV()

	it = net.BegEI()
	for i in range(net.GetEdges()):
		eid = it.GetId()
		
		etype = net.GetStrAttrDatE(eid, 'e_type')
		
		# networktype can be 'mention' or 'tag'
		if etype == 'tweet' or etype == networktype:
			mention_edges.Add(eid)
		it.Next()
		
	subnetwork = snap.GetESubGraph(net, mention_edges)
	
	return subnetwork

def getTestNetwork(complete_network, n_test):
	allusers = pd.read_csv('data-random/user.csv', sep='\t')
	test_users = list(allusers[allusers['n_test'] == n_test]['screen_name'].unique())
	seed_users = list(pd.read_csv('data-seed/{}/user.csv'.format(domain), sep='\t')['screen_name'])
	
	testNetworkIds = snap.TIntV()
	V = complete_network.GetNodes()
	it = complete_network.BegNI()
	for i in range(V):
		nid = it.GetId()
		type = complete_network.GetStrAttrDatN(nid, 'type')
		username = complete_network.GetStrAttrDatN(nid, 'id')

		if (username in test_users or username in seed_users):
			# add user node to subnetwork
			testNetworkIds.Add(nid)

			# add posts to subnetwork
			nodeIt = complete_network.GetNI(nid)
			for e in range(nodeIt.GetOutDeg()):
				testNetworkIds.Add(nodeIt.GetOutNId(e))
				
			# add tags to subnetwork
			tags = snap.TIntV()
			snap.GetNodesAtHop(complete_network, nid, 2, tags, True)

			testNetworkIds.AddV(tags)

		it.Next()

	testNetworkIds.Merge() 

	test_graph = snap.GetSubGraph(complete_network, testNetworkIds)
	rebuildContent(complete_network, test_graph)
	
	return test_graph

testtype = sys.argv[1] #can be random or mention
domain = sys.argv[2] # can be finance,finance_20,?
i = int(sys.argv[3]) # test number

testnamesuffix = '' # naming in case of test changes
path = '{}/{}-test/'.format(domain, testtype)

fin = snap.TFIn(path+'c_network.bin')	
network = snap.TNEANet.Load(fin)

# filter complete network keeping only seeds and subset of random (based on test number)
if i is not None:
	path = path+'test-network-features/'
	test_net = getTestNetwork(network, i)
	network = test_net
	testnamesuffix = '_{}'.format(i)

## BUILD HASHTAG NETWORK ##
h_net = buildSubNetwork(network, 'tag')
rebuildContent(network, h_net)

networkname = 'h_network'+testnamesuffix
fOut = snap.TFOut(path+networkname+'.bin')
h_net.Save(fOut)
fOut.Flush()

snap.SaveEdgeListNet(h_net, path+networkname+'.csv', 'Complete Hashtags Network - {} domain'.format(domain))
generateTables(path, networkname, h_net)

#save network for node2vec input
snap.SaveEdgeList(h_net, path+networkname+'.edgelist')

## BUILD MENTION NETWORK ##
# generate also mention network, even if not used
m_net = buildSubNetwork(network, 'mention')
rebuildContent(network, m_net)

networkname = 'm_network'+testnamesuffix
fOut = snap.TFOut(path+networkname+'.bin')
m_net.Save(fOut)
fOut.Flush()

snap.SaveEdgeListNet(m_net, path+networkname+'.csv', 'Complete Mention Network - {} domain'.format(domain))
generateTables(path, networkname, m_net)

#save network for node2vec input
snap.SaveEdgeList(m_net, path+networkname+'.edgelist')


