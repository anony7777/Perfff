import torch
import torch.nn as nn
import torch.nn.functional as F

class MLP(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.linear1 = nn.Linear(input_dim, hidden_dim, bias=False)
        self.linear2 = nn.Linear(hidden_dim, output_dim, bias=False)

    def forward(self, x):
        h = x
        h = F.relu(self.linear1(h))
        return self.linear2(h)
    