import math
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch

class AdaptiveConcatPool2d(nn.Module):
    def __init__(self, sz=None):
        super().__init__()
        sz = sz or (1,1)
        self.ap = nn.AdaptiveAvgPool2d(sz)
        self.mp = nn.AdaptiveMaxPool2d(sz)
    def forward(self, x): return torch.cat([self.mp(x), self.ap(x)], 1)

class Lambda(nn.Module):
    def __init__(self, f): super().__init__(); self.f=f
    def forward(self, x): return self.f(x)

class Flatten(nn.Module):
    def __init__(self): super().__init__()
    def forward(self, x): return x.view(x.size(0), -1)

def conv_2d(ni, nf, ks, stride): return nn.Conv2d(ni, nf, kernel_size=ks, stride=stride, padding=ks//2, bias=False)

def bn(ni, init_zero=False):
    m = nn.BatchNorm2d(ni)
    m.weight.data.fill_(0 if init_zero else 1)
    m.bias.data.zero_()
    return m

def bn_relu_conv(ni, nf, ks, stride, init_zero=False):
    bn_initzero = bn(ni, init_zero=init_zero)
    return nn.Sequential(bn_initzero, nn.ReLU(inplace=True), conv_2d(ni, nf, ks, stride))

def noop(x): return x

class BasicBlock(nn.Module):
    def __init__(self, ni, nf, stride, drop_p=0.0):
        super().__init__()
        self.bn = nn.BatchNorm2d(ni)
        self.conv1 = conv_2d(ni, nf, 1, stride)
        self.conv2 = bn_relu_conv(nf, nf, 1, 1)
        self.drop = nn.Dropout(drop_p, inplace=True) if drop_p else None
        self.shortcut = conv_2d(ni, nf, 1, stride) if ni != nf else noop

    def forward(self, x):
        x2 = F.relu(self.bn(x), inplace=True)
        r = self.shortcut(x2)
        x = self.conv1(x2)
        if self.drop: x = self.drop(x)
        x = self.conv2(x) ## * 0.2
        return x.add_(r)


def _make_group(N, ni, nf, block, stride, drop_p):
    return [block(ni if i == 0 else nf, nf, stride if i == 0 else 1, drop_p) for i in range(N)]

class WideResNet(nn.Module):
    def __init__(self, num_groups, N, in_channels=3, num_classes=None, k=1, drop_p=0.0, start_nf=16, stride=1):
        super().__init__()
        n_channels = [start_nf]
        for i in range(num_groups): n_channels.append(start_nf*(2**i)*k)

        layers = [conv_2d(in_channels, n_channels[0], 1, 1)]  # conv1
        for i in range(num_groups):
            layers += _make_group(N, n_channels[i], n_channels[i+1], BasicBlock, (1 if i==0 else stride), drop_p)

        if num_classes is not None:
            layers += [nn.AdaptiveAvgPool2d(1), bn_relu_conv(n_channels[-1], num_classes, 1, 1), Flatten()]
        
        self.features = nn.Sequential(*layers)

    def forward(self, x): return self.features(x)


def wrn_22(num_classes=None): return WideResNet(num_groups=3, N=3, num_classes=num_classes, k=6, drop_p=0.)
def wrn_22_k8(): return WideResNet(num_groups=3, N=3, num_classes=10, k=8, drop_p=0.)
def wrn_22_k10(): return WideResNet(num_groups=3, N=3, num_classes=10, k=10, drop_p=0.)
def wrn_22_k8_p2(): return WideResNet(num_groups=3, N=3, num_classes=10, k=8, drop_p=0.)
def wrn_28(): return WideResNet(num_groups=3, N=4, num_classes=10, k=6, drop_p=0.)
def wrn_28_k8(): return WideResNet(num_groups=3, N=4, num_classes=10, k=8, drop_p=0.)
def wrn_28_k8_p2(): return WideResNet(num_groups=3, N=4, num_classes=10, k=8, drop_p=0.2)
def wrn_28_p2(): return WideResNet(num_groups=3, N=4, num_classes=10, k=6, drop_p=0.2)