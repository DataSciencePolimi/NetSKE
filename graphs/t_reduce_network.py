import numpy as np
import pandas as pd
import snap

import sys
import itertools
import time

def getLen2Paths(net, sourceid, targetid):
	nodeIt = net.GetNI(sourceid)
	
	NbrV = snap.TIntV()
	NbrV.Reserve(nodeIt.GetOutDeg())
	
	for e in range(nodeIt.GetOutDeg()):
		MidNI = net.GetNI(nodeIt.GetOutNId(e))
		if MidNI.IsOutNId(targetid):
			NbrV.Add(MidNI.GetId())

	return NbrV.Len()
			
def generateTables(targetpath, netfile, net, type):
	#split file into node and edge file
	net_file = open(netfile, 'r') 
	nodes_file = open(targetpath+type+'_reduced_nodes.csv', 'w')
	nodes_file.write('id\tusername\tid_user\tusertype\n')
	edges_file = open(targetpath+type+'_reduced_edges.csv', 'w')
	edges_file.write('source\ttarget\tweight\n')
	edgelist_file = open(targetpath+type+'_network_reduced.edgelist', 'w')
	
	n_nodes = net.GetNodes()
	n_edges = net.GetEdges()
	
	line_num = 0 
	for line in net_file:
		if line_num>=4 and line_num < (n_nodes+4) : # 4 headers
			nodes_file.write(line)
		elif line_num >= (n_nodes+6) and line_num < (n_nodes+6+n_edges): #skip #END
			edges_file.write(line)
			edgelist_file.write(line)
		line_num = line_num + 1

# generate temporary files for hashtag network		
def reduceHashtagNetwork(net):
	it = net.BegNI()
	V = net.GetNodes()

	usedtags = {}	
	with open(tempnodefile, 'w') as nodefile:
		nodefile.write('id,username,usertype\n')	
		for i in range(V):
			nid = it.GetId()
			type = net.GetStrAttrDatN(nid, 'type')
			id_user = net.GetStrAttrDatN(nid, 'id')
			username = net.GetStrAttrDatN(nid, 'content')
			
			if type == 'user' or type == 'seed' or type == 'candidate':
				nodefile.write('{},{},{}\n'.format(id_user, username, type))
				
				tags = snap.TIntV()
				snap.GetNodesAtHop(net, nid, 2, tags, True)
				
				tags.Merge()
				usedtags[id_user] = tags
			it.Next()
			
	with open(tempedgefile, 'w') as edgefile:
		edgefile.write('source,target,weight\n')
		
		for usertuple in list(itertools.combinations(usedtags.keys(), 2)):
			u0 = usertuple[0]
			u1 = usertuple[1]
			
			tags0 = usedtags[u0]
			tags1 = usedtags[u1]
		
			commonT = snap.TIntV()
			tags0.Intrs(tags1, commonT)
			Ntags = commonT.Len()

			if Ntags > 0:
				edgefile.write('{},{},{}\n'.format(u0,u1,Ntags))
				
# generate temporary files for mention network		
def reduceMentionNetwork(net):
	it = net.BegNI()
	with open(tempnodefile, 'w') as nodefile:
		with open(tempedgefile, 'w') as edgefile:
			nodefile.write('id,username,usertype\n')
			edgefile.write('source,target,weight\n')
			
			for i in range(net.GetNodes()):
				nid = it.GetId()
				type = net.GetStrAttrDatN(nid, 'type')
				username = net.GetStrAttrDatN(nid, 'content')
				sourcestringid = net.GetStrAttrDatN(nid, 'id')
				
				if type == 'user' or type == 'seed' or type == 'candidate':
					nodefile.write('{},{},{}\n'.format(sourcestringid, username, type))
					users = snap.TIntV()
					snap.GetNodesAtHop(net, nid, 2, users, True)
					
					for u in users:
						stringid = net.GetStrAttrDatN(u, 'id')
						uname = net.GetStrAttrDatN(u, 'content')
						utype = net.GetStrAttrDatN(u, 'type')
						count = getLen2Paths(net, nid, u)
						nodefile.write('{},{},{}\n'.format(stringid, uname, utype))
						edgefile.write('{},{},{}\n'.format(sourcestringid, stringid, count))
				it.Next()
				
	nodes = pd.read_csv(tempnodefile).drop_duplicates()
	edges = pd.read_csv(tempedgefile)
		
	nodes.to_csv(tempnodefile, index=None)
	edges.to_csv(tempedgefile, index=None)

# generate temporary files for hashtag network		
def reduceNounNetwork(net):
	it = net.BegNI()
	V = net.GetNodes()

	usedtags = {}	
	with open(tempnodefile, 'w') as nodefile:
		nodefile.write('id,username,usertype\n')	
		for i in range(V):
			nid = it.GetId()
			id_user = net.GetStrAttrDatN(nid, 'id')
			type = net.GetStrAttrDatN(nid, 'type')
			username = net.GetStrAttrDatN(nid, 'content')
			
			if type == 'seed' or type == 'candidate':
				nodefile.write('{},{},{}\n'.format(id_user, username, type))
				
				tags = snap.TIntV()
				snap.GetNodesAtHop(net, nid, 1, tags, True)
				
				tags.Merge()
				usedtags[id_user] = tags
			it.Next()
			
	with open(tempedgefile, 'w') as edgefile:
		edgefile.write('source,target,weight\n')
		
		for usertuple in list(itertools.combinations(usedtags.keys(), 2)):
			u0 = usertuple[0]
			u1 = usertuple[1]
			
			tags0 = usedtags[u0]
			tags1 = usedtags[u1]
		
			commonT = snap.TIntV()
			tags0.Intrs(tags1, commonT)
			Ntags = commonT.Len()

			if Ntags > 0:
				edgefile.write('{},{},{}\n'.format(u0,u1,Ntags))
	
def buildReducedNet():
	context = snap.TTableContext()

	#define schema using columns of the files
	e_schema = snap.Schema()
	e_schema.Add(snap.TStrTAttrPr("source", snap.atStr))
	e_schema.Add(snap.TStrTAttrPr("target", snap.atStr)) 
	e_schema.Add(snap.TStrTAttrPr("weight", snap.atInt))

	n_schema = snap.Schema()
	n_schema.Add(snap.TStrTAttrPr("id", snap.atStr))
	n_schema.Add(snap.TStrTAttrPr("username", snap.atStr))
	n_schema.Add(snap.TStrTAttrPr("usertype", snap.atStr))

	#define TTable objects of edges and nodes
	edgetable = snap.TTable.LoadSS(e_schema, tempedgefile, context, ",", snap.TBool(True))
	nodetable = snap.TTable.LoadSS(n_schema, tempnodefile, context, ",", snap.TBool(True))

	#define (if any) attribute names using SNAP string vectors
	edgeattrv = snap.TStrV()
	edgeattrv.Add("weight")

	nodeattrv = snap.TStrV()
	nodeattrv.Add("id")
	nodeattrv.Add("username")
	nodeattrv.Add("usertype")


	#build SNAP network using the two TTable objects
	reduced_net = snap.ToNetwork(snap.PNEANet, edgetable, "source", "target", edgeattrv, nodetable, "id", nodeattrv, snap.aaFirst)
	
	return reduced_net

networktype = sys.argv[1]
testtype = sys.argv[2]
domain = sys.argv[3]

outpath = '{}/{}-test/'.format(domain, testtype)
temppath = 'temp/'

tempedgefile = temppath+'reduced_edges.csv'
tempnodefile = temppath+'reduced_nodes.csv'

if networktype == 'mention':
	fin = snap.TFIn(outpath+'m_network.bin')
	network = snap.TNEANet.Load(fin)

	start = time.time()
	print 'Mention network reduction...'
	print 'Starting |V|: {}'.format(network.GetNodes())
	print 'Starting |E|: {}'.format(network.GetEdges())

	reduceMentionNetwork(network)
	r_net = buildReducedNet()
	snap.SaveEdgeListNet(r_net, outpath+'m_network_reduced.csv', 'Reduced Mention Network - {}'.format(domain))
	generateTables(outpath, outpath+'m_network_reduced.csv', r_net, 'm')
	print 'Time needed: {} s'.format(time.time()-start)	
	
elif networktype == 'tag':
	fin = snap.TFIn(outpath+'h_network.bin')
	network = snap.TNEANet.Load(fin)
	
	start = time.time()
	print '{} network reduction...'.format(networktype)
	print 'Starting |V|: {}'.format(network.GetNodes())
	print 'Starting |E|: {}'.format(network.GetEdges())

	reduceHashtagNetwork(network)
	r_net = buildReducedNet()
	snap.SaveEdgeListNet(r_net, outpath+'h_network_reduced.csv', 'Reduced Hashtag Network - {}'.format(domain))
	generateTables(outpath, outpath+'h_network_reduced.csv', r_net, 'h')
	print 'Time needed: {} s'.format(time.time()-start)
	
elif networktype == 'noun':
	fin = snap.TFIn(outpath+'noun_network.bin')
	network = snap.TNEANet.Load(fin)
	
	start = time.time()
	print '{} network reduction...'.format(networktype)
	print 'Starting |V|: {}'.format(network.GetNodes())
	print 'Starting |E|: {}'.format(network.GetEdges())

	reduceNounNetwork(network)
	r_net = buildReducedNet()
	snap.SaveEdgeListNet(r_net, outpath+'noun_network_reduced.csv', 'Reduced Noun Network - {}'.format(domain))
	generateTables(outpath, outpath+'noun_network_reduced.csv', r_net, 'noun')
	print 'Time needed: {} s'.format(time.time()-start)


