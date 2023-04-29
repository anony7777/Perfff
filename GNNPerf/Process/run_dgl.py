import sys
import argparse
import time
import numpy as np

import torch
import torch.nn as nn
from dgl.dataloading import NeighborSampler
from dgl.dataloading import DataLoader
from gpu_record import GPURecord
from dgl.dataloading import GraphDataLoader

sys.path.append('Process/datasets')
from data_loader import LoadData_dgl_NodeClassification
from data_loader import LoadData_dgl_GraphClassification

import datetime
from sqlalchemy import null


#############################################################
# node_classification
#############################################################
def task_NodeClassification():
    data = LoadData_dgl_NodeClassification(args.dataset, 1)
    if data == null:
        sys.exit()
    g = data[0]
    feature_dim = len(g.ndata['feat'][0])
    classes = data[1]
    print('[run_dgl]: dataset {}, in_dim = {}, out_dim = {}'.format(args.dataset, feature_dim, classes))

    if args.minibatch == 0:
        print("[run_dgl]: not using minibatch")
    else:
        print("[run_dgl]: minibatch size = {}".format(args.minibatch))

    sys.path.append('Projects/{}'.format(args.project))
    if int(args.minibatch) == 0:
        from gul_dgl import Model
    else:
        from gul_dgl_minibatch import Model
    model = Model(in_dim=feature_dim, out_dim=classes)

    model.cuda(gpu)

    print('[run_dgl]: model structure: ')
    print(model)

    print('[run_dgl]: train starting...')
    model = train_NodeClassification(model, g)
    #print('[run_dgl]: evaluate starting...')
    #accuracy = evaluate_NodeClassification(model, g)
    #print('[run_dgl]: accuracy on the test set is {}'.format(accuracy))


def train_NodeClassification(model, g):
    loss_fcn = nn.CrossEntropyLoss()    #损失函数
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-2)
    dur = []

    if int(args.minibatch) == 0:
        g = g.to(gpu)
    else:
        sampler = NeighborSampler([30]*int(args.layer))
        dataloader = DataLoader(
            g,
            torch.tensor([i for i in range(g.num_nodes())]),
            sampler,
            batch_size=int(args.minibatch),
            shuffle=True,
            drop_last=False)

    #训练时间记录
    global gpu_record
    gpu_record.execute()

    model.train()     #设置训练状态
    #train_mask = g.ndata['train_mask']

    starttime = datetime.datetime.now()
    with torch.profiler.profile(
            activities=[
                torch.profiler.ProfilerActivity.CPU,
                torch.profiler.ProfilerActivity.CUDA,
            ],
            schedule=torch.profiler.schedule(wait=1, warmup=1, active=3, repeat=2),
            #on_trace_ready=torch.profiler.tensorboard_trace_handler('./log_temp/dgl_temp'),
            record_shapes=True,
            profile_memory=True,
            with_stack=True
    ) as prof:
        if int(args.minibatch) == 0:    #不分batch
            for epoch in range(int(args.epoch)):
                if epoch >= 3:
                    t0 = time.time()

                logits = model(g, g.ndata['feat'])
                #loss = loss_fcn(logits[train_mask], g.ndata['label'][train_mask])
                loss = loss_fcn(logits[:], g.ndata['label'][:])
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                if epoch >= 3:
                    dur.append(time.time() - t0)
                print("Epoch {:05d} | Loss {:.4f} | Time(s) {:.4f}".format(
                    epoch, loss.item(), np.mean(dur)))
                prof.step()

        else:   #minibatch
            for epoch in range(int(args.epoch)):
                if epoch >= 3:
                    t0 = time.time()
                
                for input_nodes, output_nodes, blocks in dataloader:
                    blocks = [b.to(gpu) for b in blocks]
                    features = blocks[0].srcdata['feat']
                    labels = blocks[-1].dstdata['label']

                    logits = model(blocks, features)
                    loss = loss_fcn(logits[:], labels[:])
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()

                if epoch >= 3:
                    dur.append(time.time() - t0)
                print("Epoch {:05d} | Loss {:.4f} | Time(s) {:.4f}".format(
                    epoch, loss.item(), np.mean(dur)))
                prof.step()

    #训练时间记录            
    endtime = datetime.datetime.now()
    duration = str(endtime-starttime)               #总运行时间
    gpu_utilization = str(gpu_record.kill())        #每秒GPU利用率
    memory_summary = torch.cuda.memory_summary()    #内存占用

    operator_info = str(prof.key_averages().table(sort_by="self_cuda_time_total"))
    profiler_file_path = './Results/' + args.project + '/dgl_' + args.task + '_' + args.dataset + '_' + args.epoch + '_' + args.minibatch + '_' + args.layer + '.txt'
    with open(profiler_file_path, 'w') as fp:
        fp.write(duration + '\n' + gpu_utilization + '\n' + memory_summary + '\n' + operator_info)
        fp.close()

    return model


def evaluate_NodeClassification(model, g):
    model.eval()  #设置验证状态
    test_mask=g.ndata['test_mask']
    g = g.to(gpu)
    with torch.no_grad():
        logits = model(g, g.ndata['feat'])
        logits = logits[test_mask]
        labels = g.ndata['label'][test_mask]
        _, indices = torch.max(logits, dim=1)
        correct = torch.sum(indices == labels)
        return correct.item() * 1.0 / len(labels)


#############################################################
# graph_classification
#############################################################
def task_GraphClassification():
    data = LoadData_dgl_GraphClassification(args.dataset)
    if data == null:
        sys.exit()
    dataset = data[0]
    print(dataset[0][0])
    feature_dim = len(dataset[0][0].ndata['attr'][0])
    classes = data[1]
    print('[run_dgl]: dataset {}, feature_dim = {}, num_classes = {}'.format(args.dataset, feature_dim, classes))

    dataloader = GraphDataLoader(
        dataset,
        batch_size=int(args.minibatch),
        drop_last=False,
        shuffle=True
    )

    sys.path.append('Projects/{}'.format(args.project))
    from gul_dgl import Model
    model = Model(in_dim=feature_dim, out_dim=classes)
    model.cuda(gpu)

    print('[run_dgl]: model structure: ')
    print(model)

    print('[run_dgl]: train starting...')
    model = train_GraphClassification(model, dataloader)
    #print('[run_dgl]: evaluate starting...')
    #accuracy = evaluate_NodeClassification(model, g)
    #print('[run_dgl]: accuracy on the test set is {}'.format(accuracy))


def train_GraphClassification(model, dataloader):
    loss_fcn = nn.CrossEntropyLoss()    #损失函数
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-2)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=50, gamma=0.5)
    dur = []

    #训练时间记录
    global gpu_record
    gpu_record.execute()

    model.train()     #设置训练状态
    starttime = datetime.datetime.now()
    with torch.profiler.profile(
            activities=[
                torch.profiler.ProfilerActivity.CPU,
                torch.profiler.ProfilerActivity.CUDA,
            ],
            schedule=torch.profiler.schedule(wait=1, warmup=1, active=3, repeat=2),
            #on_trace_ready=torch.profiler.tensorboard_trace_handler('./log_temp/dgl_temp'),
            record_shapes=True,
            profile_memory=True,
            with_stack=True
    ) as prof:
        for epoch in range(int(args.epoch)):
            if epoch >= 3:
                t0 = time.time()
            
            total_loss = 0
            # problem: stack expects each tensor to be equal size, but got [1, 188] at entry 0 and [0, 188] at entry 3
            for batched_graph, labels in dataloader:
                batched_graph = batched_graph.to(gpu)
                labels = labels.to(gpu)
                feat = batched_graph.ndata.pop("attr")
                
                logits = model(batched_graph, feat)
                loss = loss_fcn(logits, labels)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

            scheduler.step()

            if epoch >= 3:
                dur.append(time.time() - t0)
            print("Epoch {:05d} | Loss {:.4f} | Time(s) {:.4f}".format(
                epoch, total_loss, np.mean(dur)))
            prof.step()

    #训练时间记录            
    endtime = datetime.datetime.now()
    duration = str(endtime-starttime)               #总运行时间
    gpu_utilization = str(gpu_record.kill())        #每秒GPU利用率
    memory_summary = torch.cuda.memory_summary()    #内存占用

    operator_info = str(prof.key_averages().table(sort_by="self_cuda_time_total"))
    profiler_file_path = './Results/' + args.project + '/dgl_' + args.task + '_' + args.dataset + '_' + args.epoch + '_' + args.minibatch + '_' + args.layer + '.txt'
    with open(profiler_file_path, 'w') as fp:
        fp.write(duration + '\n' + gpu_utilization + '\n' + memory_summary + '\n' + operator_info)
        fp.close()

    return model


#############################################################
# main
#############################################################
def main():
    print('[run_dgl]: start project ' + args.project + ', task ' + args.task)
    if args.task == 'NodeClassification' or args.task == 'NC':
        task_NodeClassification()
    elif args.task == 'GraphClassification' or args.task == 'GC':
        task_GraphClassification()
    else:
        print('[run_pyg error]: wrong task!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project', help='project name')
    parser.add_argument('-t', '--task', help='task name')       #node_classification graph_classification
    parser.add_argument('-d', '--dataset', help='dataset name')
    parser.add_argument('-e', '--epoch', help='epoch number')
    parser.add_argument('-b', '--minibatch', help='minibatch number')
    parser.add_argument('-l', '--layer', help='layer number')
    args = parser.parse_args()

    # global parameter
    gpu = 0         # GPU设备号

    # gpu utilization record
    gpu_record = GPURecord()

    try:
        main()
    except Exception as e:
        print(e)
    #main()

