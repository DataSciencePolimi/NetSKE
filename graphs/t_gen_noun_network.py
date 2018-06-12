import snap
import pandas as pd

def generateTables(targetpath, netfile, net):
	#split file into node and edge file
	net_file = open(targetpath+netfile+'.csv', 'r') 
	nodes_file = open(targetpath+netfile+'_nodes.csv', 'w')
	nodes_file.write('id\ttype\tid_node\n')
	edges_file = open(targetpath+netfile+'_edges.csv', 'w')
	edges_file.write('source\ttarget\tfrequency\n')
	
	n_nodes = net.GetNodes()
	n_edges = net.GetEdges()
	
	line_num = 0 
	for line in net_file:
		if line_num>=4 and line_num < (n_nodes+4) : # 4 headers
			nodes_file.write(line)
		elif line_num >= (n_nodes+6) and line_num < (n_nodes+6+n_edges): #skip #END
			edges_file.write(line)
		line_num = line_num + 1
		

datapath = ['data-seed/','data-candidate/']
domain = 'finance' 
outpath = '{}/'.format(domain)

nodefile = '../../temp/noungraph_nodes.csv'
edgefile = '../../temp/noungraph_edges.csv'

# read edges to extract distinct nodes
# id_entity is the word or the username
nodes = pd.DataFrame(columns=['id_entity','type'])
edges = pd.DataFrame(columns=['screen_name','word','frequency'])
for p in datapath:
	e = pd.read_csv(p+domain+'/noun.csv')
	
	if p == 'data-candidate/':
		n1 = e[['screen_name']]
		n1['type'] = 'candidate'
		n1.columns = ['id_entity', 'type']
	elif p == 'data-seed/':
		n1 = e[['screen_name']]
		n1['type'] = 'seed'
		n1.columns = ['id_entity', 'type']
		
	n2 = e[['word']]
	n2['type'] = 'noun'
	n2.columns = [ 'id_entity', 'type']
	
	nodes = pd.concat([nodes, n1, n2])
	edges = pd.concat([edges, e])
	
nodes.drop_duplicates(inplace=True)
nodes.to_csv(nodefile, index=None)
edges.to_csv(edgefile, index=None)

## NETWORK CONSTRUCTION ##
e_schema = snap.Schema()
e_schema.Add(snap.TStrTAttrPr("screen_name", snap.atStr))
e_schema.Add(snap.TStrTAttrPr("word", snap.atStr))
e_schema.Add(snap.TStrTAttrPr("frequency", snap.atInt)) 

n_schema = snap.Schema()
n_schema.Add(snap.TStrTAttrPr("id_entity", snap.atStr))
n_schema.Add(snap.TStrTAttrPr("type", snap.atStr))

#define TTable objects of edges and nodes
context = snap.TTableContext()
edgetable = snap.TTable.LoadSS(e_schema, edgefile, context, ",", snap.TBool(True))
nodetable = snap.TTable.LoadSS(n_schema, nodefile, context, ",", snap.TBool(True))

#define (if any) attribute names using SNAP string vectors
edgeattrv = snap.TStrV()
edgeattrv.Add("frequency")

nodeattrv = snap.TStrV()
nodeattrv.Add("type")
nodeattrv.Add("id_entity")

#build SNAP network using the two TTable objects
net = snap.ToNetwork(snap.PNEANet, edgetable, "screen_name", "word", edgeattrv, nodetable, "id_entity", nodeattrv, snap.aaFirst)
print '|V| = {}'.format(net.GetNodes())
print '|E| = {}'.format(net.GetEdges()) 
print 'Connected network: {}'.format(snap.IsConnected(net))

networkname = 'noun_network'

#save network for metadata and visualization
snap.SaveEdgeListNet(net, outpath+networkname+'.csv', 'Noun Network - {} domain'.format(domain))
generateTables(outpath, networkname, net)

#save network for node2vec input
#snap.SaveEdgeList(net, outpath+networkname+'.edgelist')

#save network for relaoding and manipulation
fOut = snap.TFOut(outpath+networkname+'.bin')
net.Save(fOut)
fOut.Flush()
