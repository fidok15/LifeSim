import torch 
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
class DQNmodel(nn.Module):
    def __init__(self, input_shape, num_stats, num_actions):
        super(DQNmodel, self).__init__()
        #parametry przekazywanego swiata 
        channel, height, width = input_shape
        
        self.conv1 = nn.Conv2d(channel, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 64, kernel_size=3, padding=1)

        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        #wyplaszczenie naszego grida swiata
        conv_out_size = self._get_conv_out((channel, height, width))
        self.fc_stats = nn.Linear(num_stats, 64)
        combined_dim = conv_out_size + 64
        self.fc_combined = nn.Linear(combined_dim, 256)
        self.value_stream = nn.Linear(256, 1)
        self.advantage_stream = nn.Linear(256, num_actions)
    
    def _get_conv_out(self, shape):
        with torch.no_grad():
            input_t = torch.zeros(1, *shape)
            x = self.pool(F.relu(self.conv1(input_t)))
            x = self.pool(F.relu(self.conv2(x)))
            x = F.relu(self.conv3(x))
            return int(np.prod(x.size()))
    
    def forward(self, state):
        
        grid, stats = state
        x = F.relu(self.conv1(grid))
        x = self.pool(x)
        x = F.relu(self.conv2(x))
        x = self.pool(x)
        x = F.relu(self.conv3(x))

        x = x.view(x.size(0), -1)

        s = F.relu(self.fc_stats(stats))
        #polaczenie
        combined = torch.cat((x, s), dim=1)
        features = F.relu(self.fc_combined(combined))

        val = self.value_stream(features)
        adv = self.advantage_stream(features)
        q_values = val + (adv - adv.mean(dim=1, keepdim=True))
        #output
        return q_values