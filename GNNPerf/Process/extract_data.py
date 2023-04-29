import csv
import argparse


#读取duration数据(file_path的第1行)
#返回一个float数据，单位为s
def getDuration(file_path):
    try:
        with open(file_path, mode='r') as file:
            line = file.readline()
            duration = 0
            for t in line.split(':'):   #将0:00:14.777304改成14.7s
                duration = duration * 60 + float(t)
            return duration
    except Exception as e:  #文件不存在说明模型训练未顺利结束
        return 'OOM'


#读取平均gpu利用率
#返回一个float数据(百分数)
def getGpuUtilization(file_path):
    try:
        file = open(file_path, mode='r')
        file.readline()
        line = file.readline().strip().strip('[').strip(']').split(',') # a list
    
        ave = 0
        time = 0
        for t in line:
            ave += int(t)
            time += 1
        file.close()
        return (ave / time) / 100, line #平均占用率 占用率列表
    except Exception as e:
        return 'OOM', 'OOM'


#读取内存峰值
#返回一个float数据，单位MB
def getPeakMemory(file_path):
    try:
        with open(file_path, mode='r') as file:
            for line in file:
                if line.find('Allocated memory') > -1:  #找到Allocated memory所在的一行
                    seg = line.split()
                    peak_mem, mem_unit = int(seg[7]), seg[8]
                    if mem_unit == 'KB':
                        peak_mem /= 1024
                    break
        return peak_mem
    except Exception as e:
        return 'OOM'


#读取算子
#源文件中算子已按GPU利用率降序排列
#返回一个字典
def getOprator(file_path):
    op_dic = {}     #算子的字典 算子名:算子占比(%)
    with open(file_path, mode='r') as file:
        lines = file.readlines()
        num_lines = len(lines)

        #找到算子开始行
        i = 0
        while lines[i].lstrip()[0:4] != 'Name':
            i = i+1
        
        #如果没有Self CUDA % 直接返回
        if len(lines[i+1].split()) < 15:
            print('[extra_data]: has no \'Self CUDA %\'')
            return op_dic


        i = i+2

        while i < num_lines and lines[i][0:4] != '----':
            seg = lines[i].split()

            #跳过Name列
            j = 1
            while seg[j].find('%') <= -1:
                j = j+1
            ratio_str = seg[j+6]

            #得到完整的Name
            name = seg[0]
            for k in range(1, j):
                name = name + ' ' + seg[k]

            op_dic[name] = float(ratio_str.replace('%', '')) / 100
            i = i+1
        return op_dic


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--framework', help='dgl or pyg') #extra parameter than run_dgl.py
    parser.add_argument('-p', '--project', help='project name')
    parser.add_argument('-t', '--task', help='task name')       #node_classification graph_classification
    parser.add_argument('-d', '--dataset', help='dataset name')
    parser.add_argument('-e', '--epoch', help='epoch number')
    parser.add_argument('-b', '--minibatch', help='minibatch number')
    parser.add_argument('-l', '--layer', help='layer number')
    args = parser.parse_args()

    csv_file = open('Results/' + args.project + '/' + 'result_' + args.framework + '_' + args.task + '_' + args.dataset + '_' + args.epoch + '_' + args.minibatch + '_' + args.layer + '.csv', 'w', encoding='utf-8', newline='')
    csv_writer = csv.writer(csv_file)
    file_path = 'Results/' + args.project + '/' + args.framework + '_' + args.task + '_' + args.dataset + '_' + args.epoch + '_' + args.minibatch + '_' + args.layer + '.txt'

    #csv_writer.writerow()   写一行csv,参数是list
    #csv_writer.writerow([]) 写入一个空行

    csv_writer.writerow([getDuration(file_path)])             #Duration(s)

    ave_utilization, utilizations = getGpuUtilization(file_path)
    csv_writer.writerow([ave_utilization])                      #AveGpuUtilization(%)
    csv_writer.writerow(utilizations)                         #GpuUtilization(a list of %)

    csv_writer.writerow([getPeakMemory(file_path)])           #PeakMemory(MB)

    #Operators 每行: name + CUDA percent
    op_dic = getOprator(file_path)
    for key, value in op_dic.items():
        csv_writer.writerow([key, value])

    csv_file.close()