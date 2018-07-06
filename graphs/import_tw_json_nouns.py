import pandas as pd

import json

import os
import sys

domain = sys.argv[1]

if domain == 'random':
	path = 'data-random/'
else:
	path = 'data-seed/{}/'.format(domain)
	
header = 'screen_name\tword\tfrequency\n'
nounfilenames = [f for f in os.listdir(path) if 'NOUN' in f]

with open(path+'noun.csv', 'w') as output:
	output.write(header)
	for f in nounfilenames:
		with open(path+f, 'r') as nounfile:
			data = json.load(nounfile)
			
			for u in data:
				vector = data[u]['NOUN']
				for word in vector:
					output.write('{}\t{}\t{}\n'.format(u.lower(),word.encode('utf-8'),vector[word]))