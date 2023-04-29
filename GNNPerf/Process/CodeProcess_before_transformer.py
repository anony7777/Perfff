# 使用code_transformer前
# DSL前加必要引用support.h，删除空行
# 为使用code_transformer做准备

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--source', help='source file path')
parser.add_argument('-t', '--target', help='output target path')
args = parser.parse_args()

with open(args.source, 'r') as file1:
    lines = file1.readlines()

file2 = open(args.target, 'w')

#写入cpp头文件引用
file2.write('#include\"../../Process/support.h\"\nint main() { return 0; }\n')

i = 0
# 删除空行
while True:
    line1 = lines[i].lstrip()   #删除左侧空白
    if len(line1) != 0:
        break
    i = i+1

while i < len(lines):
    file2.write(lines[i])
    i = i+1
file2.write('\n')

file2.close()
