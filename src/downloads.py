import os
import sys
import requests

from concurrent.futures import ThreadPoolExecutor
from time import sleep

import log

#分片
def calc_divisional_range(filesize, chuck=20):
    step = filesize // chuck
    arr = list(range(0, filesize, step))
    result = []
    for i in range(len(arr) - 1):
        s_pos, e_pos = arr[i], arr[i + 1] - 1
        result.append([s_pos, e_pos])
    result[-1][-1] = filesize - 1
    return result

# 分片下载
def range_download(save_name, s_pos, e_pos,referer,cookie,url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "Range": f"bytes={s_pos}-{e_pos}",
        "Referer": referer,
        "Cookie": cookie
    }
    res = requests.get(url, headers=headers, stream=True)
    with open(save_name, "rb+") as f:
        f.seek(s_pos)
        for chunk in res.iter_content(chunk_size=64 * 1024):
            if chunk:
                f.write(chunk)

#进度条
def progress_bar(finish_tasks_number, tasks_number,speed):
    #----From https://blog.csdn.net/TaoismHuang/article/details/120747536
    """
    进度条
    :param finish_tasks_number: int, 已完成的任务数
    :param tasks_number: int, 总的任务数
    :return:
    """
    percentage = round(finish_tasks_number / tasks_number * 100)
    finish_size = format(finish_tasks_number / (1024 * 1024), '.2f') + "MB"
    tasks_size = format(tasks_number / (1024 * 1024), '.2f') + "MB"
    speed = format(speed / (1024 * 1024), '.2f') + "MB"
    print("\r进度: {}% 速度{}/s".format(percentage,speed), "-" * (percentage // 2), "已下载{} 文件大小{} ".format(finish_size,tasks_size),end="")
    sys.stdout.flush()

def download(url,savef,referer,cookie):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "Referer": referer,
        "Cookie": cookie
    }
    res = requests.head(url,headers=headers)
    if res.status_code != 200:#使用head方法效率高，不知为何有时会404或403。出现404时用urlopen方法来获取响应头
        import urllib.request
        res = urllib.request.Request(url,headers = headers)
        res = urllib.request.urlopen(res)
        log.debug("Get headers using the 'urllib.Request.urlopen' method")
    log.debug("Request Status:" + str(res))

    filesize = int(res.headers['Content-Length'])
    log.debug("File Size:" + str(filesize))
    divisional_ranges = calc_divisional_range(filesize)

    # 先创建空文件
    open(savef, "wb")

    with ThreadPoolExecutor() as p:
        futures = []
        for s_pos, e_pos in divisional_ranges:
            futures.append(p.submit(range_download, savef, s_pos, e_pos,referer,cookie,url))
        new_size_buff = 0
        while True:
            oringin_size_buff = os.path.getsize(savef)
            progress_bar(oringin_size_buff,filesize,new_size_buff)
            sleep(1)
            new_size_buff = os.path.getsize(savef) - oringin_size_buff
            if all(f.done() for f in futures):
                break
    print("\n")

# From https://blog.csdn.net/as604049322/article/details/119847193
