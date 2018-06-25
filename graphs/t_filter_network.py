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

testtype = sys.argv[1] #can be random or mention
domain = sys.argv[2] # can be finance,finance_20,?

path = '{}/{}-test/'.format(domain, testtype)

fin = snap.TFIn(path+'c_network.bin')	
network = snap.TNEANet.Load(fin)

## BUILD HASHTAG NETWORK ##
h_net = buildSubNetwork(network, 'tag')
rebuildContent(network, h_net)

networkname = 'h_network'
fOut = snap.TFOut(path+networkname+'.bin')
h_net.Save(fOut)
fOut.Flush()

# use complete network of hashtags because it gives the best results
snap.SaveEdgeListNet(h_net, path+networkname+'.csv', 'Complete Hashtags Network - {} domain'.format(domain))
generateTables(path, networkname, h_net)

#save network for node2vec input
snap.SaveEdgeList(h_net, path+networkname+'.edgelist')

## BUILD MENTION NETWORK ##
# generate also mention network, even if not used
m_net = buildSubNetwork(network, 'mention')
rebuildContent(network, m_net)

fOut = snap.TFOut(path+'m_network.bin')
m_net.Save(fOut)
fOut.Flush()


