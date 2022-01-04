# -*- coding: utf-8 -*-
# by WangYC_99
# @NWPU changan Dec.31st 2021

import torch
import torchvision
import time

from torch import nn
from torch.utils.data import DataLoader

BATCH_SIZE = 12
LEARNING_RATE = 1e-2
OPTIMIZER = "adagrad"

train_data = torchvision.datasets.CIFAR10(root="dataset", train=True, transform=torchvision.transforms.ToTensor(),
                                          download=True)
test_data = torchvision.datasets.CIFAR10(root="dataset", train=False, transform=torchvision.transforms.ToTensor(),
                                         download=True)

train_data_size = len(train_data)
test_data_size = len(test_data)
print("训练数据集的长度为：{}".format(train_data_size))
print("测试数据集的长度为：{}".format(test_data_size))

train_dataloader = DataLoader(train_data, batch_size=BATCH_SIZE)
test_dataloader = DataLoader(test_data, batch_size=BATCH_SIZE)

class Module_WangYC(nn.Module):
    def __init__(self):
        super(Module_WangYC, self).__init__()
        self.model = nn.Sequential(
            nn.Conv2d(3, 32, 5, 1, 2),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 32, 5, 1, 2),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 5, 1, 2),
            nn.MaxPool2d(2),
            nn.Flatten(),
            nn.Linear(64*4*4, 64),
            nn.Linear(64, 10)
        )

    def forward(self, x):
        x = self.model(x)
        return x

module = Module_WangYC()
if torch.cuda.is_available():
    module = module.cuda()

loss_fn = nn.CrossEntropyLoss()
if torch.cuda.is_available():
    loss_fn = loss_fn.cuda()

learning_rate = LEARNING_RATE
if OPTIMIZER == "sgd":
    optimizer = torch.optim.SGD(module.parameters(), lr=learning_rate)
elif OPTIMIZER == "adam":
    optimizer = torch.optim.Adam(module.parameters(), lr=learning_rate)
elif OPTIMIZER == "asgd":
    optimizer = torch.optim.ASGD(module.parameters(), lr=learning_rate)
else :
    optimizer = torch.optim.SGD(module.parameters(), lr=learning_rate)
# 记录训练的次数
total_train_step = 0
# 记录测试的次数
total_test_step = 0
# 训练的轮数
epoch = 20

start_time = time.time()
for i in range(epoch):
    print("-------第 {} 轮训练开始-------".format(i+1))

    module.train()
    for data in train_dataloader:
        imgs, targets = data
        if torch.cuda.is_available():
            imgs = imgs.cuda()
            targets = targets.cuda()
        outputs = module(imgs)
        loss = loss_fn(outputs, targets)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_train_step = total_train_step + 1
        if total_train_step % 100 == 0:
            print("训练次数:{}, Loss: {}".format(total_train_step, loss.item()))
            # writer.add_scalar("train_loss", loss.item(), total_train_step)

    module.eval()
    total_test_loss = 0
    total_accuracy = 0
    with torch.no_grad():
        for data in test_dataloader:
            imgs, targets = data
            if torch.cuda.is_available():
                imgs = imgs.cuda()
                targets = targets.cuda()
            outputs = module(imgs)
            loss = loss_fn(outputs, targets)
            total_test_loss = total_test_loss + loss.item()
            accuracy = (outputs.argmax(1) == targets).sum()
            total_accuracy = total_accuracy + accuracy

    total_test_step = total_test_step + 1
    print("正确率 ： {}".format(total_accuracy/test_data_size))

end_time = time.time()
print("accuracy = %f" % (total_accuracy/test_data_size))
print("time = %f" % (end_time - start_time))
# print("time = {}".format(endtime - start_time))

torch.save(module, "WangYC_Module.pth")
# print("模型已保存")
