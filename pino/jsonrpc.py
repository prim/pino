
from twisted.internet import protocol
from pprint import pprint

import log
import json
import traceback

class JsonRpcProtocol(protocol.Protocol):

    Handler = None
    JSON_RPC_VERSION = "2.0"

    def connectionMade(self):
        log.info("ProxyServer.connectionMade %s", self)
        self.buffer = bytes()
        self.handler = self.Handler()
        print(self.handler, self.Handler, 999)

    def connectionLost(self, reason):
        log.info("ProxyServer.connectionLost %s %s", self, reason)

    def dataReceived(self, data):
        log.info("ProxyServer.dataReceived %s %s", self, repr(data))
        self.buffer += data
        binary = self.buffer

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

                response = self.handleJsonRpcRequest(binary[b:e])
                log.info("resp %s", response)
                if response: 
                    biny = json.dumps(response).encode("utf8")
                    self.transport.write(
                            b"Content-Length: %d\r\nContent-Type: application/vscode-jsonrpc; charset=utf8\r\n\r\n%s" % (
                                len(biny), biny
                            )
                        )

                begin = e
                self.buffer = binary[e:]
            else:
                break

    def handleJsonRpcRequest(self, data):
        message = json.loads(data)

        json_rpc_version = message.get("jsonrpc", -1)
        if json_rpc_version != self.JSON_RPC_VERSION:
            log.error("wrong rpc version client version %s server version %s", json_rpc_version, self.JSON_RPC_VERSION)
            return 
        method_name = message.get("method")
        if method_name is None:
            log.error("no method_name %s", message)
            return 
        # textDocument/didOpen
        method_name = method_name.replace("/", "_")
        # $/cancelRequest
        method_name = method_name.replace("$", "")
        print(self.handler)
        func = getattr(self.handler, method_name, pprint)

        message_id = message.get("id")
        if message_id is None:
            result = func(message.get("params", {}))
            return 

        try:
            result = func(message.get("params", {}))
        except Exception as e:
            result = traceback.format_exc()
            log.error("handleJsonRpcRequest error %s", result)
        return {"jsonrpc": self.JSON_RPC_VERSION, "id": message_id, "result":result}

