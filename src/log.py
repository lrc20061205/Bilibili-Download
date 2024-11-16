from colorama import init,Fore,Back,Style
import datetime

global DebugShow
DebugShow = False

init(autoreset=True)
def error(text):
	print(Fore.RED+"[{}][Error]{}".format(datetime.datetime.now().strftime('%H:%M:%S'),text))
def info(text):
	print(Fore.CYAN+"[{}][Info]{}".format(datetime.datetime.now().strftime('%H:%M:%S'),text))
def debug(text):
	if DebugShow != False:
		print(Fore.MAGENTA+"[{}][Debug]{}".format(datetime.datetime.now().strftime('%H:%M:%S'),text))
def tip(text):
	print(Fore.WHITE+"[{}][Tip]{}".format(datetime.datetime.now().strftime('%H:%M:%S'),text))
def warring(text):
	print(Fore.YELLOW+"[{}][Warring]{}".format(datetime.datetime.now().strftime('%H:%M:%S'),text))
