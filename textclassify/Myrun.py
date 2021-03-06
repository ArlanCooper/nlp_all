# -*- coding:utf-8 -*-
import time
import torch
import numpy as np
from Mytrain_eval import train,init_network
from  importlib import import_module
import argparse

# 添加参数信息
parser = argparse.ArgumentParser(description='Chinese Text Classification')
parser.add_argument('--model', type=str,required=True, help='choose a model:MyTextCNN')
parser.add_argument('--embedding', default='pre_trained',type=str,help='random or pre_trained')
parser.add_argument('--word', default=False, type= bool, help='True for word, False for char')
args = parser.parse_args()


if __name__ == '__main__':
    dataset = 'THUCNews' # 数据集

    # 搜狗新闻: embedding_SougouNews.npz, 腾讯：embedding_Tencent.npz,随机初始化: random
    embedding = 'embedding_SougouNews.npz'
    if args.embedding == 'random':
        embedding = 'random'
    model_name = args.model
    if model_name == 'FastText':
        from utils_fasttext import build_dataset, build_iterator,get_time_dif
    else:
        from My_utils import build_iterator, build_dataset, get_time_dif

    x = import_module('models.'+ model_name)
    config = x.Config(dataset, embedding)

    # 控制随机种子，保证每次答案一样
    np.random.seed(1)
    torch.manual_seed(1)
    torch.cuda.manual_seed_all(1)
    torch.backends.cudnn.deterministic = True
    start_time = time.time()
    print('Loading data ...')
    vocab, train_data, dev_data, test_data = build_dataset(config, args.word)
    # train_data:[([...],0,32),([...],1,32),...]
    train_iter = build_iterator(train_data, config)
    dev_iter = build_iterator(dev_data, config)
    test_iter = build_iterator(test_data, config)

    time_dif = get_time_dif(start_time)

    print('Time usage:',time_dif)

    # train
    config.n_vocab = len(vocab)
    model = x.Model(config).to(config.device)
    if model_name != 'Transformer':
        init_network(model)
    print(model.parameters)
    train(config, model, train_iter, dev_iter, test_iter)


