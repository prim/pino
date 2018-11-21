
"""
use ctags sub process to generate definitions
"""

from twisted.internet import protocol

import log 

class ProcessProtocol(protocol.ProcessProtocol):

    def connectionMade(self):
        log.info("ProcessProtocol.connectionMade %s", self)
        self.transport.closeStdin()

    def outConnectionLost(self):
        log.info("ProcessProtocol.outConnectionLost %s", self)

    def outReceived(self, data):
        log.info("ProcessProtocol.outReceived %s %s", self, repr(data))

    def errReceived(self, data):
        log.info("ProcessProtocol.errReceived %s %s", self, repr(data))

    def processEnded(self, reason):
        log.info("ProcessProtocol.processEnded %s %s", self, reason)


def main():
    if 1:
        from twisted.internet import reactor, protocol
        import os; print os.getcwd()
        import ctags
        self.p = ctags.ProcessProtocol()
        print path, 2
        # reactor.spawnProcess(p, path, ["-xu", os.path.realpath(__file__)])
        reactor.spawnProcess(self.p, r"C:\Python27\python.exe", ["--version"], {})
        # reactor.spawnProcess(p, r"C:\Python27\python.exe", [r"E:\github\pino\1.py"])
        return 


