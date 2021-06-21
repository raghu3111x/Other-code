import time
import os

class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
color_list = ['\033[95m','\033[96m','\033[36m','\033[94m','\033[92m','\033[93m','\033[91m'
                    ,'\033[1m','\033[4m','\033[0m'
                    ]
# os.system('clear')
# def realtime(text,t,n):
#     for i in range(len(color_list)):

#         print(color_list[i] + text + color_list[i])
#         time.sleep(t)
#         os.system('clear')

def yprint(x):
    print(color.YELLOW + x + color.END)
def pprint(x):
    print(color.PURPLE + x + color.END)
def cprint(x):
    print(color.CYAN + x + color.END)
def dprint(x):
    print(color.DARKCYAN + x + color.END)
def bprint(x):
    print(color.BLUE + x + color.END)
def gprint(x):
    print(color.GREEN + x + color.END)
def yprint(x):
    print(color.YELLOW + x + color.END)
def rprint(x):
    print(color.RED + x + color.END)
def uprint(x):
    print(color.UNDERLINE + x + color.END)
def bdprint(x):
    print(color.BOLD + x + color.END)
