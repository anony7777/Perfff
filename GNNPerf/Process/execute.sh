# usage: ./compile [project] [task] [dataset] [epoch] [minibatch] [layer]

# python -u: 强制其标准输出也同标准错误一样不通过缓存直接打印到屏幕

mkdir ./Results/$1

python -u Process/run_dgl.py -p $1 -t $2 -d $3 -e $4 -b $5 -l $6
python -u Process/run_pyg.py -p $1 -t $2 -d $3 -e $4 -b $5 -l $6

python -u Process/extract_data.py -f dgl -p $1 -t $2 -d $3 -e $4 -b $5 -l $6
python -u Process/extract_data.py -f pyg -p $1 -t $2 -d $3 -e $4 -b $5 -l $6