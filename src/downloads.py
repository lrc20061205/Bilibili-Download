import urllib.request 
import sys
import log
def progress_bar(finish_tasks_number, tasks_number):
    #----From https://blog.csdn.net/TaoismHuang/article/details/120747536
    """
    进度条
     :param finish_tasks_number: int, 已完成的任务数
    :param tasks_number: int, 总的任务数
    :return:
    """
    percentage = round(finish_tasks_number / tasks_number * 100)
    print("\r进度: {}% ".format(percentage), "-" * (percentage // 2), end="")
    sys.stdout.flush()
def percentage(a,b,c):
    '''''
    a:已经下载的数据块
    b:数据块的大小
    c:远程文件的大小
   '''
    per = 100.0 * a * b / c
    if per > 100 :
        per = 100
    progress_bar(per,100)
def download(url,savef,referer='',cookie=''):
    '''
    从URL下载文件
     :url:URL地址
     :savef: 保存文件到指定位置
     :referer:指定请求头中的Referer
     :cookie: 指定请求头中的Cookie

    '''
    # 添加header
    opener = urllib.request.build_opener()
    opener.addheaders = [
    #User-Agent','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36
    ('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'),
    ('Referer',referer), 
    ('Cookie',cookie)
    ]

    
    urllib.request.install_opener(opener)
    try:
        urllib.request.urlretrieve(url, savef,percentage)
    except urllib.error.ContentTooShortError as e:
        log.error(e)
        log.warring("网络错误重新下载")
        download(url,savef,referer,cookie)
        
        
    print("\n")
