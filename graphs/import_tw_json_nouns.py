import pandas as pd

import json

import os
import sys

domain = sys.argv[1]

if domain == 'random':
	path = 'data-random/'
else:
	path = 'data-seed/{}/'.format(domain)

nounfilenames = [f for f in os.listdir(path) if 'NOUN' in f]
print nounfilenames

with open(path+'noun.csv', 'w') as output:
	output.write('screen_name\tword\tfrequency\n')
	for f in nounfilenames:	
		with open(path+f, 'r') as nounfile:
			data = json.load(nounfile)
			
			for u in data:
				vector = data[u]['NOUN']
				for word in vector:
					output.write('{}\t{}\t{}\n'.format(u.lower(),word.encode('utf-8'),vector[word]))