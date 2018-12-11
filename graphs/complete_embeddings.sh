#!/usr/bin/env bash

# follower + following
declare -a arr=("finance_20" "fashion" "aw" "chess")
for i in "${arr[@]}"
do
	../../veles/examples/veles/veles -i:"$i/random-test/test-network-features/social_network_1_complete.edgelist" -o:"$i/random-test/test-network-features/social_network_1_complete.emb" -d:8 -p:1 -q:0.5 -k:30 -l:20 -v
done