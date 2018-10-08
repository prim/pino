# encoding: utf8

from twisted.internet import reactor
from twisted.internet import protocol

import sys
import os
import json
import log

class ProxyClient(protocol.Protocol):

    JSON_RPC_VERSION = "2.0"
    
    def connectionMade(self):
        self.recv_buffer = ""
        self.send_buffer = ""
        self.cli()

    # def connectionLost(self, reason):
    #     reactor.stop() 

    def dataReceived(self, data):
        self.recv_buffer += data
        binary = self.recv_buffer

        begin = 0
        end = len(binary)
        header_ending = b"\r\n\r\n"
        header_ending_l = len(header_ending)
        while True:
            index = binary[begin:].find(header_ending)
            if index == -1:
                break
            headers = {}
            headers_list = binary[begin:begin + index].split(b"\r\n")
            for header in headers_list:
                i = header.find(b":")
                if i == -1:
                    continue
                key = header[:i]
                value = header[i+2:]
                headers[key] = value

            for k, v in headers.items():
                if v.isdigit():
                    headers[k] = int(v)

            cl = headers.get(b"Content-Length", 0)
            if begin + index + cl + header_ending_l <= end:
                b = begin + index + header_ending_l
                e = b + cl

                self.handleJsonRpcRequest(binary[b:e])

                begin = e
                self.buffer = binary[e:]
            else:
                break


    def request(self, params):
        binary = json.dumps(params).encode("utf8")
        length = len(binary)
        self.transport.write(
                b"Content-Length: %d\r\nContent-Type: application/vscode-jsonrpc; charset=utf8\r\n\r\n%s" % (
                    length, binary
                )
            )

    def handleJsonRpcRequest(self, data):
        message = json.loads(data)
        json_rpc_version = message.get("jsonrpc", -1)
        if json_rpc_version != self.JSON_RPC_VERSION:
            log.error("wrong rpc version client version %s server version %s", json_rpc_version, LanguageServerProtocol.JSON_RPC_VERSION)
            return 
        print message.get("result", "")
        # sys.exit(0)
        reactor.stop()
        # reactor.callFromThread(reactor.stop)

    def cli(self):
        project = sys.argv[2]
        action = sys.argv[3]
        args = sys.argv[4:]
        params = {
            "jsonrpc": self.JSON_RPC_VERSION,
            "id": 1,
            "method": action,
            "params": {
                "project": project,
                "args": args,
            }
        }
        self.request(params)

class ProxyClientFactory(protocol.ClientFactory):

    protocol = ProxyClient

def main():
    f = ProxyClientFactory()
    reactor.connectTCP("127.0.0.1", 10240, f)
    reactor.run()

