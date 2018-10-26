
from twisted.internet import reactor, protocol

from core import init_project

from pino import PinoProtocol
from lsp import LanguageServerProtocol

import filesystem

def main():
    init_project()

    filesystem.start_watch() 

    lsp_port = 9999
    lsp_factory = protocol.ServerFactory()
    lsp_factory.protocol = LanguageServerProtocol
    reactor.listenTCP(lsp_port, lsp_factory, backlog=1024)

    pino_port = 10240
    pino_factory = protocol.ServerFactory()
    pino_factory.protocol = PinoProtocol
    reactor.listenTCP(pino_port, pino_factory, backlog=1024)

    reactor.run()

