"""
E-Mail:rengcheng_luo@outlook.com

2024/03/30 留:有些URL不是同等的 比如这个URL:https://www.bilibili.com/festival/genshin2024?bvid=BV1UC411B7Co 和 https://www.bilibili.com/video/BV1UC411B7Co 不是是同等的，虽然bvid一样
访问后者url回重定向到第一个url，但是JSON大差不差

2024/05/02 留:优化以前写的(不写好都不好意思上传),尽力了,能力有限(。﹏。)
"""
import argparse
import json
import os
import re
import shutil
import sys
import requests

import log
from downloads import download

headers ={}#请求头

def BiliBili_Heads():
    log.debug("Cookie:" + Cookie)
    global headers
    headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/18.19041',
    'Referer':'https://www.bilibili.com',
    'Cookie':Cookie
    }
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
def Get_codcid(codcid):
    description ={
        '7':'7(AVC)',
        '12':'12(HVC1)',
        '13':'13(HEVC)',

        }
    if type(codcid) in (int,float):#判断是数组还是数字
        return description[str(codcid)]
    cod=[]
    for x in range(len(codcid)):
        cod.append(description[str(codcid[x])])
    return cod
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
    if Video_URL is None:
        if quality >= 125:
            log.tip("提示:哔哩哔哩HDR往上的视频只支持HEVC(codecid:12)格式并已自动选择")
            download_bilibili_video(info, 12, quality, pageName, bangumiName)
            return
        log.warring("当前不支持所选的编码格式({}),已自动选择编码格式为7".format(codecid,Get_Quality(quality)))
        download_bilibili_video(info,7,quality,pageName,bangumiName)
        return #不加返回的话,会重复执行下面的代码,上面的函数已经执行下面代码了
    if info['data']['dash']['dolby']['audio'] is not None:
        if audio == None or audio == "d":
            log.tip("当前选中杜比音效")
            Audio_URL = info['data']['dash']['dolby']['audio'][0]['baseUrl']
    elif audio != None:# 如果audio = None表示没有指定音效,也就没有必要弹出错误信息
        log.error("不支持Dollby音效")
    if info['data']['dash']['flac'] is not None:
        if audio == None or audio == "h":  # 当没有指定,和指定此音效时执行
            Audio_URL = info['data']['dash']['flac']['audio']['baseUrl']
            log.tip("当前选中Hi-Res音效")
    elif audio != None:
        log.error("不支持Hi-Res音效")
    if info['data']['dash']['audio'] is not None:
        if audio == None or audio == "n":
            Audio_URL = info['data']['dash']['audio'][0]['baseUrl']
            log.tip("当前选中普通音效")
    else:
        log.tip("所选视频没有声音")

    log.info("下载视频")
    log.debug("Video URL:" + Video_URL)
    download(Video_URL, "./temp/V.m4s", "https://www.bilibili.com", Cookie)

    if info['data']['dash']['audio'] is not None:#判断视频是否有音频
        log.info("下载音频")
        log.debug("Audio URL:" + Audio_URL)
        download(Audio_URL, "./temp/A.m4s", "https://www.bilibili.com", Cookie)
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
def del_temp():
    if os.path.exists("./temp/V.m4s"):
        os.remove("./temp/V.m4s")
    if os.path.exists("./temp/A.m4s"):
        os.remove("./temp/A.m4s")
def AnalysisJson(videoName,v,title = ''):
    #v---Video JSON
    if not os.path.exists(output+"/"+title):#如果文件夹不存在则创建
        os.makedirs(output+"/"+title)
    if not os.path.exists("./temp"):
        os.makedirs("./temp")
    if not os.path.exists(output + "/" + title + "/" + videoName + ".mp4"):#判断指定视频文件是否存在
        qualitys=[]
        for z in range(len(v['data']['dash']['video'])):#获取支持的分辨率
            if v['data']['dash']['video'][z]['id'] in qualitys:#如果当qualitys里面存在当前值，就不会把当前值加入qualitys[]数组。b站不同编码格式都有不同分辨率的视频流，没必要重复加入数组
                continue
            qualitys.append(v['data']['dash']['video'][z]['id'])
        codecids=[]
        for c in range(len(v['data']['dash']['video'])):#获取支持的分辨率
            if v['data']['dash']['video'][c]['codecid'] in codecids:#当qualitys里面存在当前选定的值就不会把当前选定的值加入qualitys[]数组
                continue
            codecids.append(v['data']['dash']['video'][c]['codecid']) 
        log.info("当前集数支持的编码：{}".format(Get_codcid(codecids)))
        log.info("当前集数支持的分辨率：{}".format(Get_Quality(qualitys)))
        quality = sys_quality
        if quality is None:
            quality = max(qualitys)#默认选择最高的分辨率
        elif quality not in qualitys:
            quality = max(qualitys)#默认选择最高的分辨率
            log.warring("当前集数不支持所选分辨率,已自动选择最高的分辨率{}".format(quality))
        log.info("当前选中的分辨率:"+str(quality))
        log.info("当前选中的编码格式:"+ str(codecid))
        log.info("合集名:" + title)
        log.info("视频名:"+videoName)
        download_bilibili_video(v,codecid,quality,videoName,title)
        if not os.path.exists(output + "/" + title + "/" + videoName + ".mp4"):
            log.error(output + "/" + title + "/" + videoName + ".mp4 下载失败")
            del_temp()
            return
        del_temp()
    log.tip(output +"/"+ title + "/" + videoName +".mp4 已经下载")
def bangumi():
    BiliBili_Heads()
    x = requests.get(URL,headers=headers).text

    #webJSON = match(x,r'playurlSSRData = (.*?[\n])')#获取bangumi 列表
    webJSON = match(x, r'__INITIAL_STATE__=(.*?);\(function\(\)')
    if args.json:
        log.debug(x)
        log.debug("Video(Bangumi) Json:" + webJSON)
    bangumiName = match(x,r'<meta property="og:title" content="(.*?)">')#获取bangumi名称 <div class="bilibili-player-pgcinfo-name" data-v-5e8af00f>小林家的龙女仆</div>
    jso= json.loads(webJSON)
    log.info(bangumiName)
    #bangumiList = requests.get("https://api.bilibili.com/pgc/view/web/ep/list?ep_id={}".format(jso['epInfo']['epid']),headers=headers).text
    #ListJSON = json.loads(bangumiList)

    #log.tip("这个Bangumi有 {} 个视频 使用 -p 下载播放列表".format(len(ListJSON['result']['episodes'])))
    log.tip("这个Bangumi有 {} 个视频 使用 -p 下载播放列表".format(len(jso['epList'])))
    log.debug("Type: Bangumi")
    if args.playlist:
        for x in range(len(jso['epList'])):#bangumi数量
            API = "https://api.bilibili.com/x/player/playurl?avid={}&cid={}&qn=0&fnval=4048".format(jso['epList'][x]['aid'],jso['epList'][x]['cid'])
            log.debug("Get API:" + API)
            v=requests.get(API,headers=headers).text
            bangumiInfo = re.sub(r'(\\u[a-zA-Z0-9]{4})',lambda x:x.group(1).encode("utf-8").decode("unicode-escape"),v)#把所有类似/u002F符号还原
            log.info("第" + str(x+1) +"集")
            v=json.loads(bangumiInfo)#把bangumi列表加载为python字典
            if v['code'] == -404 :
                log.error("404")
                log.error("通常是没有加载Cookie或cookie保存的账户没有开通会员")
                continue
            #pageName = ListJSON['result']['episodes'][x]['share_copy']
            pageName = jso['epList'][x]['share_copy']
            pageName = pageName.replace('\t',' ').replace('\r',' ').replace('\n',' ').replace('/',' ').replace('“',' ').replace('”',' ')#把所有转义字符(特殊字符)替换为空格
            '''
            2024/03/24 留言:
            有些bangumi在名称里面会加转义字符
            比如 www.bilibili.com/bangumi/play/ss6400,这个bangumi在json里面是这样写标题的:“第一折\t危险！迷之荒野” 
            www.bilibili.com/bangumi/play/ss2629/,这个bangumi的OVA标题还特喵的带“/”
            系统命名不能带这类的符号
            小破站程序员扣工资(ˉ▽ˉ；)...
            '''
            AnalysisJson(pageName,v,bangumiName)
    else :
        API = "https://api.bilibili.com/x/player/playurl?avid={}&cid={}&qn=0&fnval=4048".format(jso['epInfo']['aid'],jso['epInfo']['cid'])
        log.debug("Get API:" + API)
        v=requests.get(API,headers=headers).text
        bangumiList = re.sub(r'(\\u[a-zA-Z0-9]{4})',lambda x:x.group(1).encode("utf-8").decode("unicode-escape"),v)#把所有类似/u002F符号还原
        log.info("第" + str(jso['epInfo']['title']) +"集")
        v=json.loads(bangumiList)#把bangumi列表加载为python字典
        if v['code'] == -404 :
            log.error("404")
            log.error("通常是没有加载Cookie或cookie保存的账户没有开通会员")
            sys.exit()
        #pageName = ListJSON['result']['episodes'][int(jso['result']['play_view_business_info']['episode_info']['title']) - 1]['share_copy']
        pageName = jso['epInfo']['share_copy']
        pageName = pageName.replace('\t',' ').replace('\r',' ').replace('\n',' ').replace('/',' ')#把所有转义字符替换为空格
        AnalysisJson(pageName,v)
def video():
    BiliBili_Heads()
    x = requests.get(URL,headers=headers)
    log.debug("headers:"+ str(headers))
    x=x.text
    videoiList = match(x,r'__INITIAL_STATE__=(.*?);\(function\(\)')#获取视频 信息
    jso =json.loads(videoiList)
    if args.json:
        log.debug("Video(Bangumi) Json:" + videoiList)
    if args.playlist:
        if 'ugc_season' in jso['videoData']:#ugc_season存在表示这个是合集
            log.debug("Type: ugc_season")
            title = jso['videoData']['ugc_season']['title']
            List = len(jso['videoData']['ugc_season']['sections'][0]['episodes'])
            for x in range(List):
                API = "https://api.bilibili.com/x/player/playurl?avid={}&cid={}&qn=0&fnval=4048".format(jso['videoData']['ugc_season']['sections'][0]['episodes'][x]['aid'],jso['videoData']['ugc_season']['sections'][0]['episodes'][x]['cid'])
                log.debug("Get API:" + API)
                v = requests.get(API,headers=headers).text
                v = re.sub(r'(\\u[a-zA-Z0-9]{4})',lambda x:x.group(1).encode("utf-8").decode("unicode-escape"),v)#把所有类似/u002F符号还原
                v = json.loads(v)
                videoName = jso['videoData']['ugc_season']['sections'][0]['episodes'][x]['title']
                videoName = videoName.replace('\t',' ').replace('\r',' ').replace('\n',' ').replace('/',' ').replace('|',' ')#把所有转义字符替换为空格
                AnalysisJson(videoName,v,title)
        else :
            log.debug("Type: Not ugc_season")
            title = jso['videoData']['title']
            List = len(jso['videoData']['pages'])
            for x in range(List):
                API = "https://api.bilibili.com/x/player/playurl?avid={}&cid={}&qn=0&fnval=4048".format(jso['videoData']['aid'],jso['videoData']['pages'][x]['cid'])
                log.debug("Get API:" + API)
                v = requests.get(API,headers=headers).text
                v = re.sub(r'(\\u[a-zA-Z0-9]{4})',lambda x:x.group(1).encode("utf-8").decode("unicode-escape"),v)#把所有类似/u002F符号还原
                v = json.loads(v)
                videoName = jso['videoData']['pages'][x]['part']
                videoName = videoName.replace('\t',' ').replace('\r',' ').replace('\n',' ').replace('/',' ').replace('|',' ')#把所有转义字符替换为空格
                AnalysisJson(videoName,v,title)
        log.info(output +"/"+ title + videoName+".mp4 已经下载") 
    else:
        if "activityKey" in jso :
            API = "https://api.bilibili.com/x/player/playurl?avid={}&cid={}&qn=0&fnval=4048".format(jso['videoInfo']['aid'],jso['videoInfo']['cid'])
            videoType = "festival"
        else:
            videoPages = jso['videoData']['videos']#获取视频数量，
            pages = jso['p'] - 1#获取当前集数，JSON数组索引从零开始，所以减1
            API = "https://api.bilibili.com/x/player/playurl?avid={}&cid={}&qn=0&fnval=4048".format(jso['videoData']['aid'],jso['videoData']['pages'][pages]['cid'])
            videoType = "video"
            log.debug("Video Pages:" + str(videoPages))
        log.debug("Type: " + videoType)
        log.debug("API:" + API)
        v = requests.get(API,headers=headers).text
        v = re.sub(r'(\\u[a-zA-Z0-9]{4})',lambda x:x.group(1).encode("utf-8").decode("unicode-escape"),v)#把所有类似/u002F符号还原
        v = json.loads(v)
        if videoType == "festival":
            videoName = jso['videoInfo']['title']
        elif videoType == "video":
            if videoPages > 1:#集数大于1则说明这个BVID有多个子视频（选集）。众所周知，B站除了有左上角的标题以外，选集还可以有单独的名称
                videoName = jso['videoData']['title'] + " " + jso['videoData']['pages'][pages]['part']
            else:
                videoName = jso['videoData']['title']

        videoName = videoName.replace('\t',' ').replace('\r',' ').replace('\n',' ').replace('/',' ').replace('|',' ').replace('“',' ').replace('”',' ').replace('"',' ')#把所有转义字符替换为空格
        log.debug("Video Name:"+videoName)
        AnalysisJson(videoName,v)
if __name__ == "__main__":

    if len(sys.argv) ==1:
        print('----bilibili Download----\nData:2024/11/19\nE-Mail:rengcheng_luo@outlook.com\n-------------------------')
    parser = argparse.ArgumentParser(description='BiliBili Download')
    parser.add_argument('url',type=str,help="URL")
    parser.add_argument('-c','--cookief',type=str,metavar='文件路径',help='从文件里导入Cookie设置')
    parser.add_argument('-cod','--codecid',type=int,help='编码格式',default=7)
    parser.add_argument('-qua','--quality',type=int,help='设置分辨率')
    parser.add_argument('-o', '--output',type=str,metavar="输出路径",help='设置输出文件位置 默认./saved',default="./saved")
    parser.add_argument('-a','--audio',type=str, metavar="h,d,n",help='设置音频类型 h(hi-Res无损),d(杜比音效),n(普通音效)',)
    parser.add_argument('-f','--ffmpeg',type=str,metavar="FFmpeg文件夹",help='FFmpeg运行目录 使用绝对路径 默认为 当前目录/_FFmpeg',
                        default= os.path.dirname(os.path.realpath(sys.argv[0])) + r'\_FFmpeg')#使用realpath，使在打包后可以被正确访问。为了美观,这里用"\",而不是"/",但是"\"表示转义字符,直接写会出问题,所以加上"r"忽略转义字符
    parser.add_argument('-p','--playlist', action='store_true', help='下载播放列表')
    parser.add_argument('--debug', action='store_true', help='显示调试信息')
    parser.add_argument('--json', action='store_true', help='显示json信息 需要与 --debug 搭配使用')
    args = parser.parse_args()
    #↓默认参数
    Cookie = ''
    if args.cookief is not None:
        with open(args.cookief,"r",encoding='utf-8') as r:
            Cookie = r.read()
    if args.debug:
        log.DebugShow = True
        log.debug(sys.argv)
    if not os.path.exists(args.ffmpeg + "/ffmpeg.exe"):
        log.error("无法找到ffmpeg环境({})".format(args.ffmpeg + r"\ffmpeg.exe"))
        sys.exit()
    sys_quality = args.quality
    codecid = args.codecid
    audio = args.audio
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