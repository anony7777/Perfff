//version: 20230417 21:23 

#include<string>
using namespace std;

//meaning of the signials
//%{import __}
//#[origin api]
//## no need to translate 

//basic
//##
class tensor { 
public:
    tensor();
    tensor operator+(tensor &d);
	tensor operator-(tensor &d);
	tensor operator*(tensor &d);
    //##
    tensor flatten(int);
    //##
	tensor mean(int);
	//##Encoderfunc
	tensor sum(int);
};

//##
class Graph {
public:
	Graph();
	tensor node_feat();
	tensor edge_feat();
};

//#[super().__init__()]
void super();

//##
//for GIN
class NodeFunc {};  //example: 澹版槑NodeFunc ApplyNodeFunc();

//#[torch.softmax]
tensor softmax(tensor input, int dim);

//#[complex]
//for graph classification
tensor Readout_nodes(Graph g, tensor h);

//#[nn.init.xavier_uniform_]
void init_xavier_normal_(tensor weight, int gain); 



//activation function
class Activation {
public:
    tensor forward(tensor input);
};

//#[nn.ReLU]
class ReLU : public Activation {};

//#[nn.LeakyReLU]
class LeakyReLU : public Activation {
public:
	LeakyReLU();
    LeakyReLU(double negative_slope);
};

//#[nn.Tanh]
class Tanh : public Activation {};

//#[nn.ELU]
class ELU : public Activation {};



//dropout
//#[nn.Dropout]
class Dropout {
public:
	Dropout();
    Dropout(double dropout);
    Dropout(double dropout, bool inplace);  //p=0.5, inplace=False
    //Dropout(double dropout, bool training);
    tensor forward(tensor input);
};



//Pooling
//#[DGL: sumpool=dgl.nn.pytorch.glob.SumPooling()\n h=sumpool(g, h)]
//#[PyG: h=torch_geometric.nn.global_add_pool(h, g.batch)]
tensor add_pool(Graph g, tensor node_feats);



//##
class nn {
public:
	tensor forward(tensor input);
	//#[weight.data]
	tensor weight();
};

//#[nn.Linear]
class Linear : public nn {
public:
    Linear(int in_dim, int out_dim);
    Linear(int in_dim, int out_dim, bool bias);
};

//#[nn.BatchNorm1d]
class BatchNorm1d : public nn {
public:
	BatchNorm1d(int in_dim, bool affine);
	BatchNorm1d(int in_dim, double eps, double momentum, bool affine, bool track_running_stats);
};


//Conv
class Conv : public nn {
public:
    tensor forward(Graph g);
};

//#[DGL:GraphConv][PyG:GCNConv]
class GCNConv : public Conv {
public:
    GCNConv();
    GCNConv(int in_dim, int out_dim);
    GCNConv(int in_dim, int out_dim, bool bais, bool normalize);
    tensor forward(Graph g, tensor edge_feat);
    //#[forward(g, feat, edge_feat=edge_feat)]
    tensor forward(Graph g, tensor feat, tensor node_feat);
};

//#[DGL:SAGEConv][PyG:SAGEConv]
class SAGEConv : public Conv {
public:
    SAGEConv();
    SAGEConv(int in_dim, int out_dim);
    SAGEConv(int in_dim, int out_dim, string aggregator_type, bool bias);
    //[aggregator_type: "add" / "max" / "mean" / "lstm"]
    tensor forward(Graph g, tensor node_feat);
};

//#[DGL:GATConv][PyG:GATConv]
class GATConv : public Conv {
public:
    GATConv();
    GATConv(int in_dim, int out_dim, int heads, double attn_drop, double negative_slope);
    GATConv(int in_dim, int out_dim, int heads, double attn_drop, double negative_slope, bool bias);
    tensor forward(Graph g, tensor node_feat);
};

//#[DGL:GINConv][PyG:GINConv]
class GINConv : public Conv {
public:
    GINConv();
    GINConv(NodeFunc node_func, double eps, bool train_eps);
    tensor forward(Graph g, tensor node_feat);
};

//#[DGL:TAGConv][PyG:TAGConv]
class TAGConv : public Conv {
public:
    TAGConv();
    TAGConv(int in_dim, int out_dim);
    TAGConv(int in_dim, int out_dim, int k, bool bias);
    tensor forward(Graph g, tensor node_feat);
};
