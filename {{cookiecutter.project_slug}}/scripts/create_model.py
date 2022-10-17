import sys, torch

class MeanNet(torch.nn.Module):
    def forward(self, x):
        return torch.mean(x, dim=(2, 3))

torch.jit.script(MeanNet()).save(sys.argv[1])
