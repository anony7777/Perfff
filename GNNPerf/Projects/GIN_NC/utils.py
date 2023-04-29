import torch
import torch.nn as nn
import torch.nn.functional as F


class ApplyNodeFunc(nn.Module):
    def __init__(self, mlp):
        super().__init__()
        self.mlp = mlp
    
    def forward(self, h):
        h = self.mlp(h)
        return h
