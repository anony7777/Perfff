# 使用code_transformer后
# 转换C++风格为Python风格，如删除';','{','}'
# 为代码添加必要的引用，如GCNConv

importing_dgl = {'GraphConv':'from dgl.nn.pytorch.conv import GraphConv',
                 'GINConv':'from dgl.nn.pytorch.conv import GINConv',
                 'SAGEConv':'from dgl.nn.pytorch.conv import SAGEConv',
                 'GATConv':'from dgl.nn.pytorch.conv import GATConv',
                 'TAGConv':'from dgl.nn.pytorch.conv import TAGConv'}
importing_pyg = {'GCNConv':'from torch_geometric.nn import GCNConv',
                 'GINConv':'from torch_geometric.nn import GINConv',
                 'SAGEConv':'from torch_geometric.nn import SAGEConv',
                 'GATConv':'from torch_geometric.nn import GATConv',
                 'TAGConv':'from torch_geometric.nn import TAGConv'}


import argparse
import sys


# C++风格转Python风格
def modifyLine(text):
    text = text.replace(';', '')
    text = text.replace('{', '')
    text = text.replace('}', '')
    text = text.replace('true', 'True')
    text = text.replace('false', 'False')
    return text


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', help='source file path')
    parser.add_argument('-t', '--target', help='output target path')
    parser.add_argument('-m', '--mode', help='dgl or pyg')
    args = parser.parse_args()

    # 打开源文件和目标文件
    with open(args.source, 'r') as file1:
        lines = file1.readlines()
    file2 = open(args.target, 'w')

    # 引用查找
    if args.mode == 'dgl':
        importings = importing_dgl
    else:   #'pyg'
        importings = importing_pyg

    have_importing = set()
    for line in lines:
        for importing in importings:
            if importing not in have_importing and line.find(importing) != -1:
                have_importing.add(importing)
        

    # 添加引用
    file2.write('import torch\n')
    file2.write('import torch.nn as nn\n')
    file2.write('import torch.nn.functional as F\n')
    file2.write('import utils\n')
    if args.mode == 'dgl':
        file2.write('import dgl\n')
    else:   #pyg
        file2.write('import torch_geometric\n')

    for importing in have_importing:
        file2.write(importings[importing])
        file2.write('\n')
    file2.write('\n\n')

    # 0、1行是 #include"../../Process/support.h" 和 int main() { return 0; }
    # 所以从2行开始
    # 寻找 def model(nn.module): 的行
    # 删除该行之前的所有行
    i = 2
    while (i < len(lines)):
        tmp = lines[i].lstrip()     # 删除左空格
        if len(tmp) >=6 and tmp[0:6] == 'class ':
            break;
        i = i+1
    if i == len(lines):
        print('[CodeProcess error]: has no class Model!')
        sys.exit()
    
    decl = False
    add_tab = False

    while (i < len(lines)):
        tmp = lines[i].lstrip()
        if len(tmp) >=6 and tmp[0:6] == 'class ':
            decl = True
            add_tab = False
            file2.write(modifyLine(lines[i]))
        elif len(tmp) >= 6 and tmp[0:4] == 'def ':
            decl = False
            file2.write(modifyLine(lines[i]))
        elif not decl and tmp[0:2] != '//':
            if not add_tab and tmp[0:5] == 'with ':
                add_tab = True
                file2.write(modifyLine(lines[i]))
            else:
                if add_tab:
                    file2.write('    ' + modifyLine(lines[i]))
                else:
                    file2.write(modifyLine(lines[i]))
        
        i = i+1

    file2.close()
