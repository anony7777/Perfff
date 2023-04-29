# usage: ./compile [project_name]
# $1 = project_name

echo [compile]: start compiling...

python Process/CodeProcess_before_transformer.py -s Projects/$1/gul.txt -t Projects/$1/gul_cpp.cpp

# DGL
../llvm-project/build/bin/tran-dgl Projects/$1/gul_cpp.cpp -- > Projects/$1/gul_dgl_draft.py
../llvm-project/build/bin/tran-d-minibatch Projects/$1/gul_cpp.cpp -- > Projects/$1/gul_dgl_minibatch_draft.py
python Process/CodeProcess_after_transformer.py -s Projects/$1/gul_dgl_draft.py -t Projects/$1/gul_dgl.py -m dgl
python Process/CodeProcess_after_transformer.py -s Projects/$1/gul_dgl_minibatch_draft.py -t Projects/$1/gul_dgl_minibatch.py -m dgl

# PyG
../llvm-project/build/bin/tran-pyg Projects/$1/gul_cpp.cpp -- > Projects/$1/gul_pyg_draft.py
python Process/CodeProcess_after_transformer.py -s Projects/$1/gul_pyg_draft.py -t Projects/$1/gul_pyg.py -m pyg

echo [compile]: compile finished.