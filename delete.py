# -*- coding: utf-8 -*-
import os
import time

rootdir = './cache/'


def doWork():
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            file_path = rootdir + filename
            print("%s正在删除......" % filename)
            os.remove(file_path)
            print("%s删除成功" % filename)


def run(interval):
    while True:
        try:
            print("删除缓存图片,倒计1小时中....")
            time_remaining = interval - time.time() % interval
            time.sleep(time_remaining)
            doWork()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    interval = 60 * 60
    print('每1小时清空cache中图片')
    run(interval)
