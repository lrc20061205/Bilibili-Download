from colorama import init,Fore,Back,Style
import datetime

global DebugShow
DebugShow = False

init(autoreset=True)
def error(text):
	print("\033[0;31;40m[{}][Error]{}".format(datetime.datetime.now().strftime('%H:%M:%S'),text))
def info(text):
	print("\033[0;37;40m[{}][Info]{}".format(datetime.datetime.now().strftime('%H:%M:%S'),text))
def debug(text):
	if DebugShow != False:
		print("\033[0;34;40m[{}][Debug]{}".format(datetime.datetime.now().strftime('%H:%M:%S'),text))
def tip(text):
	print("\033[0;32;40m[{}][Tip]{}".format(datetime.datetime.now().strftime('%H:%M:%S'),text))
def warring(text):
	print("\033[0;33;40m[{}][Warring]{}".format(datetime.datetime.now().strftime('%H:%M:%S'),text))
