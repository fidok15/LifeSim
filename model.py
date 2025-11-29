import torch 
import torch.nn as nn
import torch.nn.functional as F
class DQNmodel(nn.Module):
    def __init__(self, input_shape, num_stats, num_actions):
        super(DQNmodel, self).__init__()

        channel, height, width = input_shape
        
        self.conv1 = nn.Conv2d(channel,32,3,padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)

        flatten_dim = 64 * height * width 
        self.fc_conv = nn.Linear(flatten_dim, 128)
        self.fc_stats = nn.Linear(num_stats, 64)
        
        self.fc_combined = nn.Linear(128 + 64, 128)
        self.output = nn.Linear(128, num_actions)
    
    def forward(self, state):
        
        grid, stats = state
        x = F.relu(self.conv1(grid))
        x = F.relu(self.conv2(x))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc_conv(x))

        s = F.relu(self.fc_stats(stats))
        #polaczenie
        combined = torch.cat((x, s), dim=1)
        #output
        out = F.relu(self.fc_combined(combined))

        return self.output(out)