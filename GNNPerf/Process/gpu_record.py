from asyncio.subprocess import STDOUT
from subprocess import Popen, PIPE, TimeoutExpired


class GPURecord(object):
    def __init__(self):
        self.process = None
        self.outs = ""
        self.errs = ""

    '''
    def waitSecs(self, sec: int = 5):
        try:
            self.outs, self.errs = self.process.communicate(timeout=sec)
        except TimeoutExpired:
            self.process.kill()
            self.outs, self.errs = self.process.communicate()
            return False
        return True
    '''

    # 创建nvidia-smi子进程
    def execute(self):
        # Popen: 创建一个子进程
        # nvidia-smi --query-gpu=utilization.gpu --format=csv --loop=1: 每秒输出GPU利用率
        args = "nvidia-smi --query-gpu=utilization.gpu --format=csv --loop=1"
        self.process = Popen(args=args, shell=True, stdout=PIPE, stderr=PIPE,
                             executable='/bin/bash')
    
    # 结束nvidia-smi子进程，并返回输出信息
    def kill(self):
        self.process.kill() # kill nvidia-smi
        self.outs, self.errs = self.process.communicate()   # 子进程nvidia-smi的输出
        outs = str(self.outs, 'UTF-8')
        outs = outs.split()
        ut_list = []
        k = 0
        for i in range(2, len(outs), 4):
            ut_list.append(int(outs[i]))
            # print(outs[i], end=" ")
            k += 1
        # print(sum / k)
        # print(outs)
        return ut_list
