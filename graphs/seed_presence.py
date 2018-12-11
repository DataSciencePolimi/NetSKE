import pandas as pd
import sys

domain = sys.argv[1]
ftype = sys.argv[2]

path = domain + '/random-test/test-network-features/'
input_file = path + ftype + '_network_nodes.csv'

data = pd.read_csv(input_file)
seeds = pd.read_csv('data-seed/' + domain + '/user.csv', sep='\t')

for s in seeds['id_user']:
	print s, s in data['id'].values 
