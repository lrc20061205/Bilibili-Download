import requests
#import ssl
#ssl._create_default_https_context = ssl._create_unverified_context
url="http://hkg.download.datapacket.com/100mb.bin"
headers = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
	"Referer": "",
	"Cookie": ""

    }
#res = requests.head(url,headers=header)
#urllib.request.build_opener().headers = header#使用head方法有时候会404，不知为何。换成get方法虽然可以用，但是效率低
res = requests.head(url)

if res.status_code == 404:
    import urllib.request
    res = urllib.request.Request(url,headers = headers)
    res = urllib.request.urlopen(res)
print(int(res.headers['Content-Length'])/(1024*1024),"MB")