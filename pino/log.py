
import time

def debug(fmt, *args):
    if args:
        fmt = fmt % args
    # fmt = fmt[:128]
    print fmt
    return 

    if args:
        print(time.asctime(), fmt % args)
    else:
        print(time.asctime(), fmt)

info = debug
error = debug

# def info(fmt, *args):
#     if args:
#         print(time.asctime(), fmt % args)
#     else:
#         print(time.asctime(), fmt)
# 
# def error(fmt, *args):
#     if args:
#         print(time.asctime(), fmt % args)
#     else:
#         print(time.asctime(), fmt)
# 
