import sys
import argparse
import time
import numpy as np

import torch
import torch.nn as nn
from torch_geometric.loader import NeighborLoader
from torch_geometric.loader import DataLoader
from gpu_record import GPURecord

sys.path.append('Process/datasets')
from data_loader import LoadData_pyg_NodeClassification
from data_loader import LoadData_pyg_GraphClassification

import datetime
from sqlalchemy import null


#############################################################
# node_classification
#############################################################
def task_NodeClassification():
    data = LoadData_pyg_NodeClassification(args.dataset, 1)
    if data == null:
        sys.exit()
    g = data[0]
    feature_dim = len(g.x[0])
    classes = data[1]
    print('[run_pyg]: dataset {}, feature_dim = {}, num_classes = {}'.format(args.dataset, feature_dim, classes))

    if args.minibatch == 0:
        print("[run_pyg]: not using minibatch")
    else:
        print("[run_pyg]: minibatch size = {}".format(args.minibatch))

    sys.path.append('Projects/{}'.format(args.project))
    from gul_pyg import Model
    model = Model(in_dim=feature_dim, out_dim=classes)
    model.cuda(gpu)

    print('[run_pyg]: model structure:')
    print(model)

    print('[run_pyg]: train starting...')
    model = train_NodeClassification(model, g)
    #print('[run_pyg]: evaluate starting...')
    #accuracy = evaluate_NodeClassification(model, g)
    #print('[run_pyg]: accuracy on the test set is {}'.format(accuracy))


def train_NodeClassification(model, g):
    loss_fcn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-2)
    dur = []

    if int(args.minibatch) == 0:
        g = g.to(gpu)
    else:
        # loader = DataLoader([g], batch_size=int(args.minibatch), shuffle=True)
        loader = NeighborLoader(g, num_neighbors=[30]*int(args.layer), batch_size=int(args.minibatch), shuffle=True)

    global gpu_record
    gpu_record.execute()
    
    model.train()
    train_mask=g.train_mask

    starttime = datetime.datetime.now()
    with torch.profiler.profile(
        schedule=torch.profiler.schedule(wait=1, warmup=1, active=3, repeat=2),
        #on_trace_ready=torch.profiler.tensorboard_trace_handler('./log_temp/pyg_temp/'),
        record_shapes=True,
        profile_memory=True,
        with_stack=True
    ) as prof:
        if int(args.minibatch) == 0:
            for epoch in range(int(args.epoch)):
                if epoch >= 3:
                    t0 = time.time()

                logits = model(g, g.x)
                loss = loss_fcn(logits[train_mask], g.y[train_mask])
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

                for batch in loader:
                    g = batch.to(gpu)
                    logits = model(g, g.x)
                    loss = loss_fcn(logits[:], g.y[:])
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
    duration = str(endtime-starttime)
    gpu_utilization = str(gpu_record.kill())
    memory_summary = torch.cuda.memory_summary()

    operator_info = str(prof.key_averages().table(sort_by="self_cuda_time_total"))
    profiler_file_path = './Results/' + args.project + '/pyg_' + args.task + '_' + args.dataset + '_' + args.epoch + '_' + args.minibatch + '_' + args.layer + '.txt'
    with open(profiler_file_path, 'w') as fp:
        fp.write(duration + '\n' + gpu_utilization + '\n' + memory_summary + '\n' + operator_info)
        fp.close()

    return model


def evaluate_NodeClassification(model, g):
    model.eval()  #设置验证状态
    test_mask=g.test_mask
    g = g.to(gpu)
    with torch.no_grad():
        logits = model(g, g.x)
        logits = logits[test_mask]
        labels = g.y[test_mask]
        _, indices = torch.max(logits, dim=1)
        correct = torch.sum(indices == labels)
        return correct.item() * 1.0 / len(labels)


#############################################################
# graph_classification
#############################################################
def task_GraphClassification():
    dataset = LoadData_pyg_GraphClassification(args.dataset)
    if dataset == null:
        sys.exit()
    feature_dim = dataset.num_features
    classes = dataset.num_classes
    print('[run_pyg]: dataset {}, feature_dim = {}, num_classes = {}'.format(args.dataset, feature_dim, classes))

    dataloader = DataLoader(dataset, batch_size=int(args.minibatch), shuffle=False)

    sys.path.append('Projects/{}'.format(args.project))
    from gul_pyg import Model
    model = Model(in_dim=feature_dim, out_dim=classes)
    model.cuda(gpu)

    print('[run_pyg]: model structure:')
    print(model)

    print('[run_pyg]: train starting...')
    model = train_GraphClassification(model, dataloader)
    #print('[run_pyg]: evaluate starting...')
    #accuracy = evaluate_NodeClassification(model, g)
    #print('[run_pyg]: accuracy on the test set is {}'.format(accuracy))


def train_GraphClassification(model, dataloader):
    loss_fcn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-2)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=50, gamma=0.5)
    dur = []

    global gpu_record
    gpu_record.execute()

    model.train()
    starttime = datetime.datetime.now()
    with torch.profiler.profile(
        schedule=torch.profiler.schedule(wait=1, warmup=1, active=3, repeat=2),
        #on_trace_ready=torch.profiler.tensorboard_trace_handler('./log_temp/pyg_temp/'),
        record_shapes=True,
        profile_memory=True,
        with_stack=True
    ) as prof:
        for epoch in range(int(args.epoch)):
            if epoch >= 3:
                t0 = time.time()

            total_loss = 0
            for data in dataloader:  # Iterate in batches over the training dataset.
                data = data.to(gpu)

                logits = model(data, data.x)  # Perform a single forward pass.
                loss = loss_fcn(logits, data.y)  # Compute the loss.
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
    duration = str(endtime-starttime)
    gpu_utilization = str(gpu_record.kill())
    memory_summary = torch.cuda.memory_summary()

    operator_info = str(prof.key_averages().table(sort_by="self_cuda_time_total"))
    profiler_file_path = './Results/' + args.project + '/pyg_' + args.task + '_' + args.dataset + '_' + args.epoch + '_' + args.minibatch + '_' + args.layer + '.txt'
    with open(profiler_file_path, 'w') as fp:
        fp.write(duration + '\n' + gpu_utilization + '\n' + memory_summary + '\n' + operator_info)
        fp.close()

    return model



#############################################################
# main
#############################################################
def main():
    print('[run_pyg]: start project ' + args.project + ', task ' + args.task)
    if args.task == 'NodeClassification' or args.task == 'NC':
        task_NodeClassification()
    elif args.task == 'GraphClassification' or args.task == 'GC':
        task_GraphClassification()
    else:
        print('[run_pyg error]: wrong task!')


if __name__ == '__main__':
    # starttime = datetime.datetime.now()

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project', help='project name')
    parser.add_argument('-t', '--task', help='task name')       #node_classification graph_classification
    parser.add_argument('-d', '--dataset', help='dataset type')
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

