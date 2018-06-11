import numpy as np
import pandas as pd
import snap
			
def generateTables(targetpath, netfile, net):
	#split file into node and edge file
	net_file = open(targetpath+netfile+'.csv', 'r') 
	nodes_file = open(targetpath+netfile+'_nodes.csv', 'w')
	nodes_file.write('id\tcontent\ttype\n')
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

domain = 'finance'
path = '10-seed/{}/'.format(domain)

fin = snap.TFIn(path+'c_network.bin')	
network = snap.TNEANet.Load(fin)

## BUILD HASHTAG NETWORK ##
h_net = buildSubNetwork(network, 'tag')
rebuildContent(network, h_net)

fOut = snap.TFOut(path+'h_network.bin')
h_net.Save(fOut)
fOut.Flush()

## BUILD MENTION NETWORK ##
m_net = buildSubNetwork(network, 'mention')
rebuildContent(network, m_net)

fOut = snap.TFOut(path+'m_network.bin')
m_net.Save(fOut)
fOut.Flush()


