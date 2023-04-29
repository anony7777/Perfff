#!/bin/bash
source ~/anaconda3/etc/profile.d/conda.sh
conda activate gnn

#变量
epoch_fullgraph=128

echo -----------------------------------
echo Test GCN fullgraph
echo -----------------------------------
project=test_GCN_NC
mkdir Results/$project
rm Results/$project/log_fullgraph.txt
./Process/compile.sh $project
#./Process/execute.sh $project NC pubmed $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC ppi $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC arxiv $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC DD $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC collab $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC ppa $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
./Process/execute.sh $project NC ddi $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt

echo -----------------------------------
echo Test SAGE fullgraph
echo -----------------------------------
project=test_SAGE_NC
mkdir Results/$project
rm Results/$project/log_fullgraph.txt
./Process/compile.sh $project
#./Process/execute.sh $project NC pubmed $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC ppi $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC arxiv $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC DD $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC collab $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC ppa $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
./Process/execute.sh $project NC ddi $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt


echo -----------------------------------
echo Test GIN fullgraph
echo -----------------------------------
project=test_GIN_NC
mkdir Results/$project
rm Results/$project/log_fullgraph.txt
./Process/compile.sh $project
#./Process/execute.sh $project NC pubmed $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC ppi $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC arxiv $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC DD $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC collab $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC ppa $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
./Process/execute.sh $project NC ddi $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt


echo -----------------------------------
echo Test GAT fullgraph
echo -----------------------------------
project=test_GAT_NC
mkdir Results/$project
rm Results/$project/log_fullgraph.txt
./Process/compile.sh $project
#./Process/execute.sh $project NC pubmed $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC ppi $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC arxiv $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC DD $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC collab $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
#./Process/execute.sh $project NC ppa $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt
./Process/execute.sh $project NC ddi $epoch_fullgraph 0 3 >> Results/$project/log_fullgraph.txt