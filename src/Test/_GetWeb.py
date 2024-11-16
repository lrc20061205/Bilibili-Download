import urllib.request

# 添加header
opener = urllib.request.build_opener()
opener.addheaders = [
('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/18.19041'),
('Referer',''),
('Cookie','')
]
urllib.request.install_opener(opener)
x = urllib.request.urlopen("https://www.bilibili.com/bangumi/play/ss5800/?spm_id_from=333.999.0.0").read()
#print(x)
with open('video.html','wb') as f:
    f.write(x)
