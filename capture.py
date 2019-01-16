# -*- coding: utf-8 -*-
import os
import time
import redis
import requests
import json
import shutil
import uuid
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from similarity import CompareImage


HTTP_ENABLE = True
EXIT_ON_HTTP_ERROR = True
HTTP_TIMEOUT = 5
RESIZE_WIDTH = 1024
RESIZE_HEIGHT = 768
RESIZE_QUALITY = 75


# 修改一
rtsp_src = "rtsp://admin:a1234567@192.168.10.67:554?tcp"
DEV_NO = 'D002'
APP_ID = 'YQ0003C0023'
APP_SECRET = 'idsldsflfsdldfso2s2'


# 修改二
HTTP_PREFIX = 'http://192.168.10.101:8686/om/aimgr/'
FACE_PIC_HTTP_PREFIX = 'http://114.55.75.34:85/'


# 上传图片数据
UPLOAD_INFO_PREFIX = HTTP_PREFIX + 'saveAiFaceQtRecord'
# 上传图片
UPLOAD_FILE_PREFIX = HTTP_PREFIX + 'uploadFile'
# 获取token
DEVICE_INFO_PREFIX = HTTP_PREFIX + 'downAidevice'


HEART_BEAT_TIME = 3600  # 默认一小时重新获取token


# 修改三
REDIS_CLIENT_IP = '192.168.10.229'
REDIS_CLIENT_PORT = 6379
REDIS_CLIENT_DB = 11
PEOPLES_INDEX_SET_NAME = 'p_list'
PEOPLES_INDEX_CONTRAST_NAME = 'c_list'
PEOPLE_INFO_PREFIX = 'p:'


executor = ThreadPoolExecutor(10)    # 同时处理的最大线程数


compare_image = CompareImage()


def setup_redis_client(ip, port, db):
    print('setup redis client %s:%d, db_idx %d' % (ip, port, db))
    pool = redis.ConnectionPool(host=ip, port=port, db=db)
    r = redis.Redis(connection_pool=pool)
    return r


def get_token_from_server(url, dev_no, app_id, app_secret):
    t = 'unkown'
    print('get token from server: dev_no %s, app_id %s, app_secret %s' % (dev_no, app_id, app_secret))
    payload = {'devNo': dev_no, 'appId': app_id, 'appSercert': app_secret, 'isScreenshot': 1}
    try:
        if HTTP_ENABLE:
            res = requests.get(url, params=payload, timeout=HTTP_TIMEOUT)
            if res.status_code == 200:
                json_res = json.loads(res.content)
                print(res.content)
                t = json_res['rows'][0]['token']
                print('got token: %s' % t)
            else:
                if EXIT_ON_HTTP_ERROR:
                    print('http request error, exit!')
                    exit(-1)
        else:
            print('got token error! use default %s' % t)
            raise IOError
    except Exception as e:
        print('get %s error!' % url)
        print(e)
        if EXIT_ON_HTTP_ERROR:
            print('http request error, exit!')
            exit(-1)
    finally:
        pass
    return t


def upload_info_to_server(url, file_url, dev_no, token, people_str, img_path, uu_id):
    ret = False
    payload = {'devNo': dev_no, 'token': token, 'sampleTime': people_str, 'uu_id': uu_id, 'isScreenshot': 1}
    try:
        if HTTP_ENABLE:
            res = requests.get(url, params=payload, timeout=HTTP_TIMEOUT)
            if res.status_code == 200:
                print(res.content)
                json_res = json.loads(res.content)
                upload_file_name = json_res['rows']
                code = json_res['code']
                desc = json_res['desc']
                print('upload_info: got upload_file_name: code %s, desc: %s, name %s' % (code, desc, upload_file_name))

                copy_file(img_path, upload_file_name, RESIZE_WIDTH, RESIZE_HEIGHT, RESIZE_QUALITY)

                payload = {"file": upload_file_name}
                current_path = os.getcwd()
                cache_path = current_path + './cache/'
                files = {
                    "file": open(cache_path+upload_file_name, "rb")
                }
                res = requests.post(file_url, payload, files=files)
                if res.status_code == 200:
                    print(res.content)
                    json_res = json.loads(res.content)
                    upload_file_name = json_res['rows']
                    code = json_res['code']
                    desc = json_res['desc']
                    ret = True
                    print('upload_file: code %s, desc: %s, name %s' % (code, desc, upload_file_name))
                else:
                    print('upload_file failed. %d' % res.status_code)
        else:
            ret = True
    except Exception as e:
        print('get %s error!' % UPLOAD_INFO_PREFIX)
        print(e)
    finally:
        pass
    return ret


def copy_file(src_file, dst_file, width, height, quality):
    if width > 0 and height > 0:
        im = Image.open(src_file)
        current_path = os.getcwd()
        cache_path = current_path + './cache/'
        im.resize((width, height), Image.ANTIALIAS).save(cache_path+dst_file, quality=quality)
    else:
        if os.path.isfile(src_file):
            shutil.copyfile(src_file, dst_file)
        else:
            print('%s not exists!' % src_file)


# setup redis
r = setup_redis_client(REDIS_CLIENT_IP, REDIS_CLIENT_PORT, REDIS_CLIENT_DB)

# 获取token
token = get_token_from_server(DEVICE_INFO_PREFIX, DEV_NO, APP_ID, APP_SECRET)


# 定时截图
def capture():
    flag = True
    while True:
        cp_time = time.time()
        image_name = str(int(cp_time))
        codeStart = "ffmpeg -i "
        input = rtsp_src
        output = " ./data/"
        codeEnd = ".jpg -f image2"
        finishcode = codeStart + input + output + image_name + codeEnd
        print('%s.jpg开始截图' % image_name)
        os.system(finishcode)
        print('截图完成')
        if flag:
            num = r.llen(PEOPLES_INDEX_CONTRAST_NAME)
            if num >= 1:
                for i in range(num):
                    r.lpop(PEOPLES_INDEX_CONTRAST_NAME)
            people_info_str = PEOPLE_INFO_PREFIX + image_name
            full_name = image_name + '.jpg'
            path = "./data/%s" % full_name
            r.lpush(PEOPLES_INDEX_CONTRAST_NAME, image_name)
            r.hmset(people_info_str, {'name': full_name, 'file_path': path})
            uu_id = str(uuid.uuid1())
            ret = upload_info_to_server(UPLOAD_INFO_PREFIX, UPLOAD_FILE_PREFIX, DEV_NO, token, image_name, path, uu_id)
            if ret:
                try:
                    pass
                except Exception as e:
                    print('remove file error!')
                    print(e)
            flag = False
        else:
            executor.submit(input_redis, image_name)
        print('15秒后截图开始...................')
        time.sleep(13)


# 异步缓存到redis
def input_redis(name):
    people_info_str = PEOPLE_INFO_PREFIX + name
    full_name = name + '.jpg'
    path = "./data/%s" % full_name
    r.rpush(PEOPLES_INDEX_SET_NAME, name)
    r.hmset(people_info_str, {'name': full_name, 'file_path': path})
    executor.submit(func)


def func():
    c = r.lindex(PEOPLES_INDEX_CONTRAST_NAME, 0)
    c_str = c.decode('utf-8')
    name = r.blpop(PEOPLES_INDEX_SET_NAME)
    name_str = name[1].decode('utf-8')
    c_info_str = PEOPLE_INFO_PREFIX + c_str
    name_info_str = PEOPLE_INFO_PREFIX + name_str
    c_img_path = r.hget(c_info_str, 'file_path').decode('utf-8')
    name_img_path = r.hget(name_info_str, 'file_path').decode('utf-8')
    # 比较相邻两张图片的相似度
    score = compare_image.compare_image(c_img_path, name_img_path)
    print('****************************')
    print(c_str)
    print(name_str)
    print(score)
    print('****************************')
    if score > 0.7:  # 相似
        os.remove(name_img_path)
        r.delete(name_info_str)
    else:  # 不相似
        r.blpop(PEOPLES_INDEX_CONTRAST_NAME)
        os.remove(c_img_path)
        r.delete(c_info_str)
        r.lpush(PEOPLES_INDEX_CONTRAST_NAME, name_str)
        uu_id = str(uuid.uuid1())
        ret = upload_info_to_server(UPLOAD_INFO_PREFIX, UPLOAD_FILE_PREFIX, DEV_NO, token, name_str, name_img_path, uu_id)
        if ret:
            try:
                pass
            except Exception as e:
                print('remove file error!')
                print(e)


if __name__ == "__main__":
    capture()



