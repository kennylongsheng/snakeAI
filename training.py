import torch
import torch.nn as nn
import torch.nn.functional as F

class Net(nn.Module):
    def __init__(self, inputCount, actionCount):
        super(Net, self).__init__()
        self.inputCount = inputCount
        self.actionCount = actionCount
        #self.network = nn.Sequential(
            #nn.Linear(self.inputCount, 36),
            #nn.ReLU(),
            #nn.Linear(36, self.actionCount)
        #)
        self.fc1 = nn.Linear(inputCount, 20)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(20, actionCount)

    def forward(self, xInput):
        #yOutput = self.network(xInput)
        out = self.fc1(xInput)
        out = self.relu(out)
        out = self.fc2(out)
        yOutput = self.relu(out)
        return yOutput