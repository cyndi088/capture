# -*- coding: utf-8 -*-
import os
import time

cache_dir = 'cache'

def doWork(cache_path):
    # 获得当前路径下的文件目录
    file_list = os.listdir(cache_path)

    for img_file in file_list:
        img_path = os.path.join(cache_path, img_file)
        # print(img_path)
        if os.path.isfile(img_path):
            # print(img_file)
            try:
                os.remove(img_path)
                print("%s删除成功" % img_path)
            except Exception as e:
                print(e)
                continue

def run(interval):
    while True:
        now_path = os.path.abspath('.')
        dir_list = os.listdir(now_path)

        for dir in dir_list:
            if os.path.isdir(dir):
                path = os.path.join(dir, cache_dir)

            try:
                print("删除缓存[%s]中的图片,倒计1小时中...." % path)
                doWork(path)
            except Exception as e:
                print(e)

        time_remaining = interval - time.time() % interval
        print('开始休眠!')
        time.sleep(time_remaining)


if __name__ == "__main__":

    interval = 60 * 60
    print('每1小时清空cache中图片')
    run(interval)
