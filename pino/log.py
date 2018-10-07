
import time

def debug(fmt, *args):
    if args:
        print(time.asctime(), fmt % args)
    else:
        print(time.asctime(), fmt)

def info(fmt, *args):
    if args:
        print(time.asctime(), fmt % args)
    else:
        print(time.asctime(), fmt)

def error(fmt, *args):
    if args:
        print(time.asctime(), fmt % args)
    else:
        print(time.asctime(), fmt)

