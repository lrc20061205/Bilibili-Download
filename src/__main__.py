'''
E-Maill:rengcheng_luo@outlook.com

2024/03/30 留:有些URL不是同等的 比如这个URL:https://www.bilibili.com/festival/genshin2024?bvid=BV1UC411B7Co 和 https://www.bilibili.com/video/BV1UC411B7Co 不是是同等的，虽然bvid一样
访问后者url回重定向到第一个url

2024/05/02 留:优化以前写的,尽力了,能力和精力有限(。﹏。)
'''
import downloads
import log
import urllib.request
import re
import json
import os
import shutil
import sys
import argparse
import gzip
from io import BytesIO
#import ssl
#ssl._create_default_https_context = ssl._create_unverified_context
def BiliBili_Heads():
    log.debug("Cookie:" + Cookie)
    opener = urllib.request.build_opener()
    opener.addheaders = [
    ('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/18.19041'),
    ('Referer','https://www.bilibili.com'),
    ('Cookie',Cookie)
    ]
    urllib.request.install_opener(opener)
def Get_Quality(quality):
    description ={
        '16':'16(360P)',
        '32':'32(480P)',
        '48':'48(720P)',
        '64':'64(720P(MP4))',
        '74':'74(720P60帧)',
        '80':'80(1080P)',
        '112':'112(1080P+)',
        '116':'116(1080P60帧)',
        '120':'120(4K)',
        '125':'125(HDR)',
        '126':'126(杜比视界)',
        '127':'127(8K)',
        }
    if type(quality) in (int,float):#判断是数组还是数字
        return description[str(quality)]
    qua=[]
    for x in range(len(quality)):
        qua.append(description[str(quality[x])])
    return qua
def match(text, *patterns):
    """Scans through a string for substrings matched some patterns (first-subgroups only).

    Args:
        text: A string to be scanned.
        patterns: Arbitrary number of regex patterns.

    Returns:
        When only one pattern is given, returns a string (None if no match found).
        When more than one pattern are given, returns a list of strings ([] if no match found).
    """
    if len(patterns) == 1:
        pattern = patterns[0]
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None
    else:
        ret = []
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                ret.append(match.group(1))
        return ret
def download_bilibili_video(info,codecid,quality,pageName,bangumiName = ''):
    Video_URL = None
    Audio_URL = None
    for x in range(len(info['data']['dash']['video'])):
        if info['data']['dash']['video'][x]['codecid'] == codecid :#选择编码格式
            if info['data']['dash']['video'][x]['id'] == quality:#获取指定分辨率
                Video_URL = info['data']['dash']['video'][x]['baseUrl']
    if Video_URL == None :
        if quality >= 125:
            log.warring("提示:哔哩哔哩HDR往上的视频只支持HEVC(codecid:12)格式")
            log.warring("已自动选择编码格式为12")
            download_bilibili_video(info,12,quality,pageName,bangumiName)
            return
        log.warring("当前不支持所选的编码格式({}),已自动选择编码格式为7".format(codecid,Get_Quality(quality)))

        download_bilibili_video(info,7,quality,pageName,bangumiName)
        return #不加返回的话,会重复执行下面的语句,上面的函数已经执行了下面的语句

    if info['data']['dash']['flac'] is not None:
        if audio == None or audio == "h":#当没有指定,和指定此音效时执行
            Audio_URL = info['data']['dash']['flac']['audio']['baseUrl']
            log.info("当前选中Hi-Res音效")
    elif audio != None: #如果=None表示用户没有指定音效,也就没有必要弹出错误信息
        log.error("不支持Hi-Res音效")

    if info['data']['dash']['dolby']['audio'] is not None:
        if audio == None or audio == "d":
            log.info("当前选中杜比音效")
            Audio_URL = info['data']['dash']['dolby']['audio'][0]['baseUrl']
    elif audio != None:
        log.error("不支持Dollby音效")

    if info['data']['dash']['audio'] is not None:
        if  audio == None or audio == "n" :
            Audio_URL = info['data']['dash']['audio'][0]['baseUrl']
            log.info("当前选中普通音效")
    else:
        log.info("所选视频没有声音")

    log.info("下载视频")
    log.debug("Video URL:" + Video_URL)
    downloads.download(Video_URL,"./temp/V.m4s","https://www.bilibili.com",Cookie)
    if info['data']['dash']['audio'] is not None:#判断视频是否有音频
        log.info("下载音频")
        log.debug("Audio URL:" + Audio_URL)
        downloads.download(Audio_URL,"./temp/A.m4s","https://www.bilibili.com",Cookie)
        log.info("合并")
        #假如bangumiName为空,则输出格式为:/{output}//{title}.mp4,它和/{output}/{title}.mp4是同等的,不为则输出格式为:/{output}/{bangumiName}/{title}.mp4
        log.debug("Command: " + args.ffmpeg +"/ffmpeg.exe"+' -i ./Temp/V.m4s -i ./Temp/A.m4s -vcodec copy -acodec copy "{}/{}/{}.mp4" -loglevel error'.format(output,bangumiName,pageName))
        os.system( args.ffmpeg + "/ffmpeg.exe" + ' -i ./Temp/V.m4s -i ./Temp/A.m4s -vcodec copy -acodec copy "{}/{}/{}.mp4" -loglevel error'.format(output,bangumiName,pageName))
    else:
        log.debug("Move:" + '{}/{}/{}.mp4'.format(output,bangumiName,pageName))
        shutil.move("./temp/V.m4s",'{}/{}/{}.mp4'.format(output,bangumiName,pageName))
def Get_Type_From_URL(URL):
    extractors = URL#https://www.bilibili.com/bangumi/play/ss5885
    extractors = extractors.replace("https://","").replace("http://","")#  www.bilibili.com/bangumi/play/ss5885
    extractors = extractors.split("/")#['www.bilibili.com', 'bangumi', 'play', 'ss5885']
    #print(extractors)
    return extractors[1] 
def unGzip(zip_str):
    buff = BytesIO(zip_str)
    f = gzip.GzipFile(fileobj=buff)
    zip_str = f.read()
    return zip_str
def AnalysisJson(videoName,v,title = ''):
    #v---Video JSON
    log.info("合集名:" + title)
    log.info("视频名:"+videoName)
    if not os.path.exists(output+"/"+title):#如果文件夹不存在则创建
        os.makedirs(output+"/"+title)
    if not os.path.exists("./temp"):
        os.makedirs("./temp")
    if os.path.exists(output+"/" + videoName+".mp4") == False:#判断指定bangumi文件是否存在
        qualitys=[]
        for z in range(len(v['data']['dash']['video'])):#获取支持的分辨率
            if v['data']['dash']['video'][z]['id'] in qualitys:#当qualitys里面存在当前选定的值就不会把当前选定的值加入qualitys[]数组
                continue
            qualitys.append(v['data']['dash']['video'][z]['id'])
        codecids=[]
        for c in range(len(v['data']['dash']['video'])):#获取支持的分辨率
            if v['data']['dash']['video'][c]['codecid'] in codecids:#当qualitys里面存在当前选定的值就不会把当前选定的值加入qualitys[]数组
                continue
            codecids.append(v['data']['dash']['video'][c]['codecid']) 
        log.info("当前集数支持的编码：{}".format(codecids))
        log.info("当前集数支持的分辨率：{}".format(Get_Quality(qualitys)))
        quality = sys_quality
        if quality == None:
            quality = max(qualitys)#默认选择最高的分辨率
        elif sys_quality not in qualitys:
            quality = max(qualitys)#默认选择最高的分辨率
            log.warring("当前集数不支持所选分辨率,已自动选择最高的分辨率{}".format(quality))
        log.info("当前选中的分辨率:"+str(quality))
        log.info("当前选中的编码格式:"+ str(codecid))
        download_bilibili_video(v,codecid,quality,videoName,title)
    log.tip(output +"/"+ videoName+".mp4 已经下载")

def bangumi():
    BiliBili_Heads()
    x = urllib.request.urlopen(URL).read()
    bangumiList = match(x.decode('utf-8'),r'__INITIAL_STATE__=(.*?);\(function\(\)')#获取bangumi 列表
    bangumiName = match(x.decode('utf-8'),r'<div class="bilibili-player-pgcinfo-name" data-v-5e8af00f>(.*?)</div>')#获取bangumi名称 <div class="bilibili-player-pgcinfo-name" data-v-5e8af00f>小林家的龙女仆</div>
    bangumiList = re.sub(r'(\\u[a-zA-Z0-9]{4})',lambda x:x.group(1).encode("utf-8").decode("unicode-escape"),bangumiList)#把所有类似/u002F符还原
    jso= json.loads(bangumiList)
    log.tip("这个Bangumi有 {} 个视频 使用 -p 下载播放列表".format(len(jso['epList'])))
    log.debug("Type: Bangumi")
    if args.json:
        log.debug("Video(Bangumi) Json:" + bangumiList)
    if args.playlist == True:
        for x in range(len(jso['epList'])):#bangumi数量
            API = "https://api.bilibili.com/x/player/playurl?avid={}&cid={}&qn=0&fnval=4048".format(jso['epList'][x]['aid'],jso['epList'][x]['cid'])
            log.debug("Get API:" + API)
            v=urllib.request.urlopen(API).read().decode('utf-8')
            bangumiList = re.sub(r'(\\u[a-zA-Z0-9]{4})',lambda x:x.group(1).encode("utf-8").decode("unicode-escape"),v)#把所有类似/u002F符号还原
            
            v=json.loads(bangumiList)#把bangumi列表加载为python字典
            if v['code'] == -404 :
                log.error("404")
                log.tip("通常是由于没有加载Cookie导致的")
                continue
            pageName = jso['epList'][x]['share_copy']
            pageName = pageName.replace('\t',' ').replace('\r',' ').replace('\n',' ').replace('/',' ')#把所有转义字符替换为空格
            '''
            2024/03/24 作者留言:
            有些bangumi在名称里面会加转义字符
            比如 www.bilibili.com/bangumi/play/ss6400,这个bangumi在json里面是这样写标题的:“第一折\t危险！迷之荒野” 
            www.bilibili.com/bangumi/play/ss2629/,这个bangumi的OVA标题还特喵的带“/”
            系统命名不能带这类的符号
            小破站程序员扣工资(ˉ▽ˉ；)...
            '''
            log.info("第" + str(x+1) +"集")
            AnalysisJson(pageName,v,bangumiName)
    else :
        API = "https://api.bilibili.com/x/player/playurl?avid={}&cid={}&qn=0&fnval=4048".format(jso['epInfo']['aid'],jso['epInfo']['cid'])
        log.debug("Get API:" + API)
        v=urllib.request.urlopen(API).read().decode('utf-8')
        bangumiList = re.sub(r'(\\u[a-zA-Z0-9]{4})',lambda x:x.group(1).encode("utf-8").decode("unicode-escape"),v)#把所有类似/u002F符号还原
        v=json.loads(bangumiList)#把bangumi列表加载为python字典
        if v['code'] == -404 :
            log.error("404")
            log.error("通常是由于没有加载Cookie导致的")
            sys.exit()
        pageName = jso['epInfo']['share_copy']
        pageName = pageName.replace('\t',' ').replace('\r',' ').replace('\n',' ').replace('/',' ')#把所有转义字符替换为空格
        log.info("第" + str(jso['epInfo']['title']) +"集")
        AnalysisJson(pageName,v,bangumiName)     

def video():
    BiliBili_Heads()
    x = urllib.request.urlopen(URL)
    if x.info().get("Content-Encoding") == "gzip":#有些页面会压缩,有些不会
        x = unGzip(x.read()).decode("utf-8")
    else:
        x=x.read().decode("utf-8")
    videoiList = match(x,r'__INITIAL_STATE__=(.*?);\(function\(\)')#获取视频 信息
    jso =json.loads(videoiList)
    if args.json:
        log.debug("Video(Bangumi) Json:" + videoiList)
    if args.playlist == True:
        if 'ugc_season' in jso['videoData']:#ugc_season表示是合集,合集和选集的JSON信息不一样
            log.debug("Type: ugc_season")
            title = jso['videoData']['ugc_season']['title']
            List = len(jso['videoData']['ugc_season']['sections'][0]['episodes'])
            for x in range(List):
                API = "https://api.bilibili.com/x/player/playurl?avid={}&cid={}&qn=0&fnval=4048".format(jso['videoData']['ugc_season']['sections'][0]['episodes'][x]['aid'],jso['videoData']['ugc_season']['sections'][0]['episodes'][x]['cid'])
                log.debug("Get API:" + API)
                v = urllib.request.urlopen(API).read().decode("utf-8")
                v = re.sub(r'(\\u[a-zA-Z0-9]{4})',lambda x:x.group(1).encode("utf-8").decode("unicode-escape"),v)#把所有类似/u002F符号还原
                v = json.loads(v)
                videoName = jso['videoData']['ugc_season']['sections'][0]['episodes'][x]['title']
                videoName = videoName.replace('\t',' ').replace('\r',' ').replace('\n',' ').replace('/',' ').replace('|',' ')#把所有转义字符替换为空格
                log.info("第"+str(x + 1)+"集")
                AnalysisJson(videoName,v,title)
        else :
            log.debug("Type: Not ugc_season")
            title = jso['videoData']['title']
            List = len(jso['videoData']['pages'])
            for x in range(List):
                API = "https://api.bilibili.com/x/player/playurl?avid={}&cid={}&qn=0&fnval=4048".format(jso['videoData']['aid'],jso['videoData']['pages'][x]['cid'])
                log.debug("Get API:" + API)
                v = urllib.request.urlopen(API).read().decode("utf-8")
                v = re.sub(r'(\\u[a-zA-Z0-9]{4})',lambda x:x.group(1).encode("utf-8").decode("unicode-escape"),v)#把所有类似/u002F符号还原
                v = json.loads(v)
                videoName = jso['videoData']['pages'][x]['part']
                videoName = videoName.replace('\t',' ').replace('\r',' ').replace('\n',' ').replace('/',' ').replace('|',' ')#把所有转义字符替换为空格
                log.info("第"+str(x + 1)+"集")
                AnalysisJson(videoName,v,title)
        log.info(output +"/"+ title + videoName+".mp4 已经下载") 
    else:
        if "activityKey" in jso : #activityKey存在则表示这个视频为festival类型
            API = "https://api.bilibili.com/x/player/playurl?avid={}&cid={}&qn=0&fnval=4048".format(jso['videoInfo']['aid'],jso['videoInfo']['cid'])
            videoType = "festival"
        else:
            videoPage = jso['p'] - 1
            API = "https://api.bilibili.com/x/player/playurl?avid={}&cid={}&qn=0&fnval=4048".format(jso['videoData']['aid'],jso['videoData']['pages'][videoPage]['cid'])
            videoType = "video"
            log.debug("Video Page:" + str(videoPage))
        log.debug("Type: " + videoType)
        log.debug("API:" + API)
        v = urllib.request.urlopen(API).read().decode("utf-8")
        v = re.sub(r'(\\u[a-zA-Z0-9]{4})',lambda x:x.group(1).encode("utf-8").decode("unicode-escape"),v)#把所有类似/u002F符号还原
        v = json.loads(v)
        if videoType == "festival":
            videoName = jso['videoInfo']['title']
        elif videoType == "video":
            videoName = jso['videoData']['title']
        videoName = videoName.replace('\t',' ').replace('\r',' ').replace('\n',' ').replace('/',' ').replace('|',' ')#把所有转义字符替换为空格
        AnalysisJson(videoName,v)
if __name__ == "__main__":
    if len(sys.argv) ==1:
        print('----bilibili Download----\nVersion:202405011\nAPI Version:20240503\nE-Maill:rengcheng_luo@outlook.com\n-------------------------')
    parser = argparse.ArgumentParser(description='BiliBili Download')
    parser.add_argument('url',type=str,help="URL")
    parser.add_argument('-c','--cookief',type=str,metavar='File Path',help='从文件里导入Cookie设置')
    parser.add_argument('-cod','--codecid',type=int,help='编码格式',default=7)
    parser.add_argument('-qua','--quality',type=int,help='设置分辨率')
    parser.add_argument('-o', '--output',type=str,metavar="output Path",help='设置输出文件位置 默认./saved',default="./saved")
    parser.add_argument('-a','--audio',type=str, metavar="h,d,n",help='设置音频类型 h(hi-Res无损),d(杜比音效),(n普通音效)',)
    parser.add_argument('-f','--ffmpeg',type=str,metavar="FFmpeg Folder",help='FFmpeg运行目录 使用绝对路径 默认为 当前目录/_FFmpeg',default= sys.path[0]+r'\_FFmpeg')#为了美观,这里用"\",而不是"/",但是"\"表示转义字符,直接写会出问题,所以加上"r"忽略转义字符
    parser.add_argument('-p','--playlist', action='store_true', help='下载播放列表')
    parser.add_argument('--debug', action='store_true', help='显示调试信息')
    parser.add_argument('--json', action='store_true', help='显示json信息 需要与 --debug 搭配使用')
    args = parser.parse_args()
    #↓默认参数
    Cookie = ''
    if args.cookief !=None:
        with open(args.cookief,"r",encoding='utf-8') as r:
            Cookie = r.read()
    if args.debug:
        log.DebugShow = True
        log.debug(sys.argv)
    if os.path.exists(args.ffmpeg + "/ffmpeg.exe") == False:
        log.error("无法找到ffmpeg环境({})".format(args.ffmpeg + r"\ffmpeg.exe"))
        sys.exit()
    sys_quality = args.quality
    codecid = args.codecid
    audio = args.audio
    audios =['d','h','n',None]
    if audio not in audios:
        log.error("音频参数错误")
        sys.exit()
    URL = args.url
    output = args.output
    quality = args.quality
    Type = Get_Type_From_URL(URL)
    match Type:
        case "bangumi":
            bangumi()
            sys.exit()
        case "video":
            video()
            sys.exit()
    log.error("暂不支持" + Type + "类型 可使用 [右键视频>复制视频地址] 的链接")