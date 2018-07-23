import sys

domain = sys.argv[1]
with open('{}/random-test/test-network-features/temp.edgelist'.format(domain), 'w') as edgelistfile:
	for line in open('finance_20/random-test/test-network-features/social_network_1_follower.edgelist'):
		if line[0] != '#':
			edgelistfile.write(line)