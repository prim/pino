
# NOTE: dont print anything here

import sys

def main():
    if len(sys.argv) < 2:
        print "python pino proxy"
        print "python pino server"
        print "python pino cli"
        print "python pino test"
        print "python pino worker"
        return 
    modname = sys.argv[1]
    module = __import__(modname)
    module.main()

if __name__ == "__main__":
    main()

