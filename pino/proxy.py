# encoding: utf8

from twisted.internet.stdio import StandardIO
from twisted.internet import reactor
from twisted.internet import protocol

import sys
import os

log_ = open(r"E:\github\pino\proxy.log", "a+")

def log_info(fmt, *args):
    if args:
        msg = fmt % args
    else:
        msg = fmt
    msg += "\n"
    log_.write(msg)
    log_.flush()

stdio = None
client = None

class Stdio(protocol.Protocol):

    def connectionMade(self):
        log_info("Stdio connectionMade")

    def dataReceived(self, data):
        log_info("Stdio dataReceived %s", repr(data))
        client.transport.write(data)

class ProxyClient(protocol.Protocol):
    
    def connectionMade(self):
        log_info("ProxyClient.connectionMade %s %s", self, self.__dict__)
        global client
        client = self
        self.recv_buffer = ""
        self.send_buffer = ""

    def connectionLost(self, reason):
        log_info("ProxyClient.connectionLost %s %s", self, reason)
        reactor.stop() 

    def dataReceived(self, data):
        log_info("ProxyClient.dataReceived %s %s", self, repr(data))
        stdio.transport.write(data)

class ProxyClientFactory(protocol.ClientFactory):

    protocol = ProxyClient

    def startedConnecting(self, connector):
        log_info("startedConnecting %s", connector)

    def clientConnectionFailed(self, connector, reason):
        log_info("clientConnectionFailed %s %s", connector, reason)

    # 不能定义这个函数 否则stop不了
    # def clientConnectionLost(self, connector, reason):
    #     log_info("clientConnectionLost %s %s", connector, reason)
    #     reactor.stop() 

def main():
    log_info("main %s", sys.argv)
    global stdio
    f = ProxyClientFactory()
    reactor.connectTCP("127.0.0.1", 9999, f)
    stdio = Stdio()
    StandardIO(stdio)
    reactor.run()

