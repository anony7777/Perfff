#!/bin/bash
source ~/anaconda3/etc/profile.d/conda.sh
conda activate gnn

#变量
epoch_minibatch=16
batch_size=10240

echo -----------------------------------
echo Test GCN minibatch
echo -----------------------------------
project=test_GCN_NC
mkdir Results/$project
rm Results/$project/log_minibatch.txt
./Process/compile.sh $project
#./Process/execute.sh $project NC protein $epoch_minibatch $batch_size 3 >> Results/$project/log_minibatch.txt
#./Process/execute.sh $project NC reddit.dgl $epoch_minibatch $batch_size 3 >> Results/$project/log_minibatch.txt
./Process/execute.sh $project NC ppa $epoch_minibatch $batch_size 3 >> Results/$project/log_minibatch.txt


echo -----------------------------------
echo Test SAGE minibatch
echo -----------------------------------
project=test_SAGE_NC
mkdir Results/$project
rm Results/$project/log_minibatch.txt
./Process/compile.sh $project
#./Process/execute.sh $project NC protein $epoch_minibatch $batch_size 3 >> Results/$project/log_minibatch.txt
#./Process/execute.sh $project NC reddit.dgl $epoch_minibatch $batch_size 3 >> Results/$project/log_minibatch.txt
./Process/execute.sh $project NC ppa $epoch_minibatch $batch_size 3 >> Results/$project/log_minibatch.txt


echo -----------------------------------
echo Test GIN minibatch
echo -----------------------------------
project=test_GIN_NC
mkdir Results/$project
rm Results/$project/log_minibatch.txt
./Process/compile.sh $project
#./Process/execute.sh $project NC protein $epoch_minibatch $batch_size 3 >> Results/$project/log_minibatch.txt
#./Process/execute.sh $project NC reddit.dgl $epoch_minibatch $batch_size 3 >> Results/$project/log_minibatch.txt
./Process/execute.sh $project NC ppa $epoch_minibatch $batch_size 3 >> Results/$project/log_minibatch.txt


echo -----------------------------------
echo Test GAT minibatch
echo -----------------------------------
project=test_GAT_NC
mkdir Results/$project
rm Results/$project/log_minibatch.txt
./Process/compile.sh $project
#./Process/execute.sh $project NC protein $epoch_minibatch $batch_size 3 >> Results/$project/log_minibatch.txt
#./Process/execute.sh $project NC reddit.dgl $epoch_minibatch $batch_size 3 >> Results/$project/log_minibatch.txt
./Process/execute.sh $project NC ppa $epoch_minibatch $batch_size 3 >> Results/$project/log_minibatch.txt


