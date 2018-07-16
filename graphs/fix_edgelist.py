with open('finance_20/random-test/test-network-features/social_network.edgelist', 'w') as edgelistfile:
	for line in open('finance_20/random-test/test-network-features/social_network_1.edgelist'):
		if line[0] != '#':
			edgelistfile.write(line)