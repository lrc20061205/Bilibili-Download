from concurrent.futures import ThreadPoolExecutor
from time import sleep
import os
import sys
import requests

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
def progress_bar(finish_tasks_number, tasks_number):
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
    print("\r进度: {}% [{} {}]".format(percentage,finish_size,tasks_size), "-" * (percentage // 2), end="")
    sys.stdout.flush()



def download(url,savef,referer,cookie):
    url = "https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe"
    res = requests.head(url)
    filesize = int(res.headers['Content-Length'])
    divisional_ranges = calc_divisional_range(filesize)
    #save_name = "QQ.exe"

    # 先创建空文件
    with open(save_name, "wb") as f:
        pass

    with ThreadPoolExecutor() as p:
        futures = []
        for s_pos, e_pos in divisional_ranges:
            futures.append(p.submit(range_download, savef, s_pos, e_pos,referer,cookie,url))
        while True:
           # print(format(os.path.getsize(save_name)/(1024 * 1024),'.2f'),"MB")
            progress_bar(os.path.getsize(save_name),filesize)
            sleep(0.5)
            if all(f.done() for f in futures):
                break

# From https://blog.csdn.net/as604049322/article/details/119847193
