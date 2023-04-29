from itertools import cycle
from lib2to3.pygram import python_grammar_no_print_statement
from statistics import mode

from numpy import double

from django.forms import PasswordInput
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Max

from time import time
from unittest import result
from urllib import request
import datetime
import os
import re
import csv

from distutils.dir_util import copy_tree
import shutil

# Create your views here.

global count
count = 0


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
    else:
        print("such dir exists")


#查询项目名
@require_http_methods(['POST'])
def queryProjectNames(request):
    dir_path = './Projects/'
    names = os.listdir(dir_path)

    projects = {}

    #筛选出文件夹
    for name in names:
        path = os.path.join(dir_path, name)
        if os.path.isdir(path):
            projects[name] = 1

    return JsonResponse(projects, safe=False)


#查询项目代码：GUL+utils
@require_http_methods(['POST'])
def queryProject(request):
    if request.POST['project'].lstrip() == "":
        return JsonResponse({'GUL':"", 'utils':""}, safe=False)
    
    dir_path = './Projects/' + request.POST['project']

    with open(dir_path + '/gul.txt', 'r') as file:
        GUL = file.read()

    with open(dir_path + '/utils.py', 'r') as file:
        utils = file.read()

    return JsonResponse({'GUL':GUL, 'utils':utils}, safe=False)


#创建新项目
@require_http_methods(['POST'])
def newProject(request):
    mkdir('./Projects/new project')
    copy_tree('./Process/sample', './Projects/new project')
    return JsonResponse({'1':1}, safe=False)


#重命名项目
@require_http_methods(['POST'])
def renameProject(request):
    if request.POST['project_old'].lstrip() == "":
        return JsonResponse({'1':"1"}, safe=False)
    
    dir_path_old = './Projects/' + request.POST['project_old']
    dir_path_new = './Projects/' + request.POST['project_new']
    os.rename(dir_path_old, dir_path_new)

    return JsonResponse({'1':'1'}, safe=False)


#保存项目：GUL+utils
@require_http_methods(['POST'])
def saveProject(request):
    if request.POST['project'].lstrip() == "":
        return JsonResponse({'1':'0'}, safe=False)
    
    dir_path = './Projects/' + request.POST['project']

    with open(dir_path + '/gul.txt', 'w') as file:
        file.write(request.POST['GUL'])

    with open(dir_path + '/utils.py', 'w') as file:
        file.write(request.POST['utils'])

    return JsonResponse({'1':'1'}, safe=False)


#删除项目
@require_http_methods(['POST'])
def deleteProject(request):
    if (request.POST['project'].lstrip() != ''):
        dir_path = './Projects/' + request.POST['project']
        shutil.rmtree(dir_path)
    return JsonResponse({'1':1}, safe=False)


#compile
@require_http_methods(['POST'])
def compile(request):
    if (request.POST['project'].lstrip() == ''):
        return JsonResponse({'1':0}, safe=False)
    
    os.system('./Process/compile.sh ' + request.POST['project'])
    dir_path = './Projects/' + request.POST['project']
    with open(dir_path + '/gul_dgl.py') as file:
        dgl = file.read()
    with open(dir_path + '/gul_pyg.py') as file:
        pyg = file.read()

    return JsonResponse({'dgl':dgl, 'pyg':pyg}, safe=False)


#train
@require_http_methods(['POST'])
def train(request):
    if (request.POST['project'].lstrip() == ''):
        return JsonResponse({'1':0}, safe=False)
    
    if request.POST['task'] == 'Node Classification':
        task = 'NC'
    elif request.POST['task'] == 'Graph Classification':
        task = 'GC'
    else:
        task = ''

    # run_dgl / run_pyg / extract_data
    cmd = 'mkdir ./Results/{}'.format(request.POST['project'])
    os.system(cmd)

    cmd_dgl = 'python -u ./Process/run_dgl.py -p {0} -t {1} -d {2} -e {3} -b {4} -l {5} > ./Results/{0}/cmd_dgl_{1}_{2}_{3}_{4}_{5}.txt'.format(request.POST['project'], task, request.POST['dataset'], request.POST['epoch'], request.POST['minibatch'], request.POST['layer'])
    cmd_pyg = 'python -u ./Process/run_pyg.py -p {0} -t {1} -d {2} -e {3} -b {4} -l {5} > ./Results/{0}/cmd_pyg_{1}_{2}_{3}_{4}_{5}.txt'.format(request.POST['project'], task, request.POST['dataset'], request.POST['epoch'], request.POST['minibatch'], request.POST['layer'])
    os.system(cmd_dgl)
    os.system(cmd_pyg)

    cmd_data_dgl = 'python -u Process/extract_data.py -f dgl -p {0} -t {1} -d {2} -e {3} -b {4} -l {5}'.format(request.POST['project'], task, request.POST['dataset'], request.POST['epoch'], request.POST['minibatch'], request.POST['layer'])
    cmd_data_pyg = 'python -u Process/extract_data.py -f pyg -p {0} -t {1} -d {2} -e {3} -b {4} -l {5}'.format(request.POST['project'], task, request.POST['dataset'], request.POST['epoch'], request.POST['minibatch'], request.POST['layer'])
    os.system(cmd_data_dgl)
    os.system(cmd_data_pyg)

    return JsonResponse({'1':1}, safe=False)


#查询结果记录信息
@require_http_methods(['POST'])
def queryResultInfos(request):
    results = {}

    dir_path = './Results/'
    folder_names = os.listdir(dir_path)

    #筛选出文件夹
    for folder_name in folder_names:
        sub_path = os.path.join(dir_path, folder_name)
        if os.path.isdir(sub_path):     #子路径
            records = os.listdir(sub_path)
            for record in records:
                record_split = record.split('.')
                if record_split[1] == 'txt':    #筛选出txt文件
                    #cmd_dgl_NC_arxiv_128_0_3 -> folder_name-NC-arxiv-128-0-3
                    tmp = record_split[0].split('_')
                    if tmp[0] == 'cmd':         #cmd开头的txt文件
                        name = folder_name+'-'+tmp[2]+'-'+tmp[3]+'-'+tmp[4]+'-'+tmp[5]+'-'+tmp[6]

                        #name最后添加一个status 1-已完成训练 0-未完成训练
                        csv_dgl = 'result_dgl_{0}_{1}_{2}_{3}_{4}.csv'.format(tmp[2], tmp[3], tmp[4], tmp[5], tmp[6])
                        csv_pyg = 'result_pyg_{0}_{1}_{2}_{3}_{4}.csv'.format(tmp[2], tmp[3], tmp[4], tmp[5], tmp[6])
                        if csv_dgl in records and csv_pyg in records:
                            flag = '1'
                        else:
                            flag = '0'
                        name = name + '-' + flag

                        results[name] = 1

    return JsonResponse(results, safe=False)


#查询cmd
@require_http_methods(['POST'])
def queryCmd(request):
    name = request.POST['name'].split('-')    #project-task-dataset-epoch-minibatch-layer
    dgl_path = './Results/{0}/cmd_dgl_{1}_{2}_{3}_{4}_{5}.txt'.format(name[0],name[1],name[2],name[3],name[4],name[5])
    pyg_path = './Results/{0}/cmd_pyg_{1}_{2}_{3}_{4}_{5}.txt'.format(name[0],name[1],name[2],name[3],name[4],name[5])
    
    dgl = ''
    pyg = ''

    try:
        with open(dgl_path, 'r') as file:
            dgl = file.read()
    except Exception:
        print(Exception)
    try:
        with open(pyg_path, 'r') as file:
            pyg = file.read()
    except Exception:
        print(Exception)

    #查询是否训练完成
    dir_path='./Results/{}/'.format(name[0])
    records = os.listdir(dir_path)

    csv_dgl = 'result_dgl_{0}_{1}_{2}_{3}_{4}.csv'.format(name[1],name[2],name[3],name[4],name[5])
    csv_pyg = 'result_pyg_{0}_{1}_{2}_{3}_{4}.csv'.format(name[1],name[2],name[3],name[4],name[5])
    if csv_dgl in records and csv_pyg in records:
        flag = '1'
    else:
        flag = '0'
    
    return JsonResponse({'dgl':dgl, 'pyg':pyg, 'status':flag}, safe=False)


#删除Result
@require_http_methods(['POST'])
def deleteResult(request):
    name = request.POST['name'].split('-')    #project-task-dataset-epoch-minibatch-layer
    dir_path = './Results/{0}'.format(name[0])
    dgl_cmd_path = './Results/{0}/cmd_dgl_{1}_{2}_{3}_{4}_{5}.txt'.format(name[0],name[1],name[2],name[3],name[4],name[5])
    pyg_cmd_path = './Results/{0}/cmd_pyg_{1}_{2}_{3}_{4}_{5}.txt'.format(name[0],name[1],name[2],name[3],name[4],name[5])
    dgl_txt_path = './Results/{0}/dgl_{1}_{2}_{3}_{4}_{5}.txt'.format(name[0],name[1],name[2],name[3],name[4],name[5])
    pyg_txt_path = './Results/{0}/pyg_{1}_{2}_{3}_{4}_{5}.txt'.format(name[0],name[1],name[2],name[3],name[4],name[5])
    dgl_csv_path = './Results/{0}/result_dgl_{1}_{2}_{3}_{4}_{5}.csv'.format(name[0],name[1],name[2],name[3],name[4],name[5])
    pyg_csv_path = './Results/{0}/result_pyg_{1}_{2}_{3}_{4}_{5}.csv'.format(name[0],name[1],name[2],name[3],name[4],name[5])
    
    try:
        os.system('rm ' + dgl_cmd_path)
    except Exception:
        print(Exception)
    try:
        os.system('rm ' + pyg_cmd_path)
    except Exception:
        print(Exception)
    try:
        os.system('rm ' + dgl_txt_path)
    except Exception:
        print(Exception)
    try:
        os.system('rm ' + pyg_txt_path)
    except Exception:
        print(Exception)
    try:
        os.system('rm ' + dgl_csv_path)
    except Exception:
        print(Exception)
    try:
        os.system('rm ' + pyg_csv_path)
    except Exception:
        print(Exception)

    #判断文件夹是否为空，若为空则删除
    if not os.listdir(dir_path):
        print("empty dir")
        try:
            os.system('rm -rf ' + dir_path)
        except Exception:
            print(Exception)
        
    return JsonResponse({'1':1}, safe=False)


#for getResult
#每隔25s算一个平均数
def get_gpu_ave_pertensec(gpu_list, step:int):
    gpu_ave_per = {'0':0}
    total = 0
    for i in range(0, len(gpu_list)):
        total += float(gpu_list[i])
        if i > 0 and i % step == 0:
            gpu_ave_per[str(i)] = total / step
            total = 0
    return gpu_ave_per


#Chart调用result
@require_http_methods(['POST'])
def getResult(request):
    name = request.POST['name'].split('-')    #project-task-dataset-epoch-minibatch-layer
    dgl_path = './Results/{0}/result_dgl_{1}_{2}_{3}_{4}_{5}.csv'.format(name[0],name[1],name[2],name[3],name[4],name[5])
    pyg_path = './Results/{0}/result_pyg_{1}_{2}_{3}_{4}_{5}.csv'.format(name[0],name[1],name[2],name[3],name[4],name[5])

    dgl_file = open(dgl_path, 'r')
    pyg_file = open(pyg_path, 'r')

    dgl_op = []
    for i, line in enumerate(dgl_file.readlines()):
        # total time
        if i == 0:      #第1行 训练总时间
            dgl_total_time = float(line)
        # average GPU Utilization
        elif i == 1:    #第2行 GPU平均利用率
            dgl_ave_gpu = float(line) * 100
        # GPU Utilization per sec
        elif i == 2:    #第3行 GPU利用率列表
            dgl_gpu_persec = get_gpu_ave_pertensec(line.split(','), 25)
            print("sb")
            print(dgl_gpu_persec)
        # peak memory
        elif i == 3:    #第4行 峰值内存
            dgl_peak_mem = line
        # operator breakdown (CUDA)
        else:
            if 'void' not in ','.join(line.split(',')[:-1]) and 'Memcpy' not in ','.join(line.split(',')[:-1]) and 'Profiler' not in ','.join(line.split(',')[:-1]) and 'aten::copy_' not in ','.join(line.split(',')[:-1]):
                dgl_op.append([','.join(line.split(',')[:-1]), float(line.split(',')[-1])])
            if 'Memcpy HtoD (Pageable -> Device)' == ','.join(line.split(',')[:-1]):
                dgl_op.append(['Memcpy HtoD', float(line.split(',')[-1])])

    pyg_op = []
    for i, line in enumerate(pyg_file.readlines()):
        # total time
        if i == 0:
            pyg_total_time = float(line)
        # average GPU Utilization
        elif i == 1:
            pyg_ave_gpu = float(line) * 100
        # GPU Utilization per sec
        elif i == 2:
            pyg_gpu_persec = get_gpu_ave_pertensec(line.split(','), 60)
        # peak memory
        elif i == 3:
            pyg_peak_mem = line
        # operator breakdown (CUDA)
        else:
            if 'void' not in ','.join(line.split(',')[:-1]) and 'Memcpy' not in ','.join(line.split(',')[:-1]) and 'Profiler' not in ','.join(line.split(',')[:-1]) and 'aten::copy_' not in ','.join(line.split(',')[:-1]):
                pyg_op.append([','.join(line.split(',')[:-1]), float(line.split(',')[-1])])
            if 'Memcpy HtoD (Pageable -> Device)' == ','.join(line.split(',')[:-1]):
                pyg_op.append(['Memcpy HtoD', float(line.split(',')[-1])])


    dgl_file.close()
    pyg_file.close()

    return JsonResponse({'dgl_op': dgl_op, 'dgl_total_time': dgl_total_time, 'dgl_ave_gpu':dgl_ave_gpu, 'dgl_gpu_persec': dgl_gpu_persec, 'dgl_peak_mem': dgl_peak_mem, 
                         'pyg_op': pyg_op, 'pyg_total_time': pyg_total_time, 'pyg_ave_gpu':pyg_ave_gpu, 'pyg_gpu_persec': pyg_gpu_persec, 'pyg_peak_mem': pyg_peak_mem,}, safe=False)

