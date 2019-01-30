# -*- coding: utf-8 -*-
import os
import time

class MyDel(object):

    def __init__(self, dir_name, interval=None):
        self.cache_path = dir_name
        self.interval = interval

    def doWork(self):
        # 获得当前路径下的文件目录
        file_list = os.listdir(self.cache_path)

        for img_file in file_list:
            img_path = os.path.join(self.cache_path, img_file)
            # print(img_path)
            if os.path.isfile(img_path):
                # print(img_file)
                try:
                    os.remove(img_path)
                    print("%s删除成功" % img_path)
                except Exception as e:
                    print(e)
                    continue

    def run(self):
        while True:
            now_path = os.path.abspath('.')
            dir_list = os.listdir(now_path)

            for dir in dir_list:
                if os.path.isdir(dir):
                    path = os.path.join(dir, self.cache_path)

                try:
                    if self.interval:
                        print("删除缓存[%s]中的图片,倒计%d小时中...." % (path, self.interval//3600))
                    else:
                        print("删除缓存[%s]中的图片..." % path)
                    self.doWork()
                except Exception as e:
                    print(e)

            if self.interval is None:
                break

            time_remaining = self.interval - time.time() % self.interval
            print('开始休眠!')
            time.sleep(time_remaining)


if __name__ == "__main__":

    cache_dir = 'cache'
    interval = 60 * 60
    print('每1小时清空cache中图片')
    md = MyDel(cache_dir, interval)
    md.run()
