# _*_ coding:utf-8 _*_
# author: lin9e
# 2020-8-20
# based python3

import os
import argparse
import socket
import time
from pymongo import MongoClient
from urllib.parse import urlparse

def _mongo(db_name, src_name):
    '''
    @desc: mongodb连接模块
    @paras: db_name, src_name
    @return: collection
    # 需自行配置MongoDB，并在此修改MongoDB配置项
    '''
    host = '118.118.118.118'
    username = 'user'
    password = 'pass'
    port = '27017'
    mongo_url = 'mongodb://{0}:{1}@{2}:{3}/?authSource={4}&authMechanism=SCRAM-SHA-1'.format(username, password, host, port,db_name)
    client = MongoClient(mongo_url)
    db_target_domain = client[db_name]
    collection = db_target_domain[src_name]
    return collection

def _domainDir(src_name, result, dir_url):
    '''
    @desc: 将格式化的数据写入数据库domainDir, 表名为src_name
    @paras: src_name, result, dir_url
    @no return 
    # 加入之前先根据dir_url去重
    '''
    collection = _mongo('domainDir',src_name)
    # dir_url去重
    if not collection.count_documents({"url": "%s" % dir_url}):
        collection.insert_one(result)

def _getJson(domain, src_name):
    '''
    @desc: 将dirmap产生的结果txt文件内容逐行转换为mongodb格式化文本
    '''
    try:
        with open('output/'+domain+'.txt', 'r') as f:
            # dirmap误报某些站点产生大量不存在的dir, 以30为界限确定是否读取写入mongo
            text = f.readlines()
            if len(text) <= 30:
                for _ in text:
                    # print(_)
                    dic = _.split("][")
                    if len(dic) == 5:
                        http_status = dic[0]
                        content_type = dic[1]
                        title = dic[2]
                        http_length = dic[3]
                        dir_url = dic[4].strip()
                    elif len(dic) == 4:
                        http_status = dic[0]
                        content_type = dic[1]
                        http_length = dic[2]
                        dir_url = dic[3].strip()
                        title = ''
                    result = {"domain":domain,"http_status":http_status,"content_type":content_type,"title":title,"http_length":http_length,"url":dir_url,"time":time.strftime('%Y-%m-%d',time.localtime())}
                    _domainDir(src_name, result, dir_url)
                    # return result,dir_url
    except Exception as e:
        print(e)
        # return ''

def main(src_name):
    print("Start {} Dirbustering...".format(src_name))
    collection = _mongo('domain', src_name)
    for i in collection.find({}):
        domain = i['domain'].strip()
        url = urlparse(i['url'].strip())
        # fix bug#### url = url.scheme+'://'+url.netloc
        url = url.scheme + '://' + domain
        # print(url)
        # os.system("python dirmap.py -t 50 -i {} -lcf".format(url))
        result = _getJson(domain, src_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='domainTodomaindir', usage='%(prog)s [options] [args] usage', description='domainTodomaindir: A tool for')
    parser.add_argument("--src", dest="srcName", type=str, help="--src srcName, eg:asrc | MUST")
    args = parser.parse_args()
    srcName = args.srcName
    banner = """
                        ______                     
                        (, /    ) ,                 
    ___   _____   _   ___ /    /    __ ___   _  __  
    // (_(_) / (_(_/_(_)_/___ /__(_/ (_// (_(_(_/_)_
                .-/   (_/___ /               .-/    
            (_/                          (_/     
                Have fun. MongoDirmap root@ohlinge.cn
    """
    print(banner)
    if not srcName:
        print(parser.format_help())
    else:
        main(srcName)
