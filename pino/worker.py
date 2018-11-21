# encoding: utf8

from twisted.internet.stdio import StandardIO
from twisted.internet import reactor
from twisted.internet import protocol
from twisted.internet import utils
from jsonrpc import JsonRpc 

from radix_tree import RadixTree

import sys
import os
import log
import languages

try:
    import cPickle as pickle
except ImportError:
    import pickle

# TODO  不同的进程不同日志

path = os.path.join(os.path.dirname(__file__), "woker.log")
log_ = open(path, "a+")

# TODO config
ctags_path = os.path.realpath(os.path.join("bin", "ctags.exe"))

def log_info(fmt, *args):
    if args:
        msg = fmt % args
    else:
        msg = fmt
    msg += "\n"
    log_.write(msg)
    log_.flush()

class Worker(object):

    def __init__(self):
        self.defer_counter = 0

        self.file_id = 0
        self.file_pathes = {}
        self.file_contents = {}

        self.bytes = 0

        self.root_levels = {}
        self.root = RadixTree(None, "", ())

        self.definition_levels = {}
        self.definition = RadixTree(None, "", ())


        # TODO config
        self.encodings = ["utf8", "gbk", "ascii"]

        self.word_length_stat = {}

    def fuck(self, *args, **kw):
        log_info("---------------- %s %s"  % (args, kw))
        log_info("---------------- %s %s"  % (args, kw))
        log_info("---------------- %s %s"  % (args, kw))
        log_info("---------------- %s %s"  % (args, kw))

    def bytes_to_string(self, source):
        for encoding in self.encodings:
            try:
                return source.decode(encoding)
            except UnicodeDecodeError:
                continue
        return ""

    def parse_file(self, params):
        log_info("%s parse_file %s", self, params)
        path, type_, file_id = params["args"]

        import string
        default_name_chars = string.ascii_letters + string.digits + "_"

        name_chars = languages.name_chars.get(type_, default_name_chars)
        language_keywords = languages.keywords.get(type_, [])

        add_definition = self.definition.add_name
        add_word = self.root.add_name

        definition_index = []
        word_index = []

        root_levels = self.root_levels
        definition_levels = self.definition_levels

        binary = ""
        with open(path, 'rb') as rf:
            binary = rf.read()
            self.bytes += len(binary)
            source = self.bytes_to_string(binary)
            self.file_contents[file_id] = source

            line = 0
            word = ""
            words = []
            b, e = 0, 0
            for char in source:
                if char in name_chars or ord(char) > 0xff:
                    word += char
                else:
                    if word:
                        words.append(word)
                        word = ""

                    if char == "\n":
                        # log.debug("%s %s", line, words)
                        for i, t in enumerate(words):
                            if t in language_keywords:
                                continue
                            if type_ == ".py":
                                if words[0] in ("def", "class") and i == 1:
                                    definition_index.append((t, line))
                            word_index.append((t, line))

                        line += 1
                        words = []

        if type_ != ".py":
            self.parse_definition(path, file_id, word_index, definition_index)
        else:
            log_info("done parse %s 1", file_id)
            self.protocol.dosomething("done_parse", file_id, word_index, definition_index)

    def parse_definition(self, path, file_id, word_index, definition_index):
        log_info("%s parse_definition %s", self, path)

        def parse_definition_result(result):
            for line in result.split('\n'):
                # line = line.rstrip()
                ps = line.split()
                if len(ps) >= 2 and ps[2].isdigit():
                    t = ps[0]
                    line = int(ps[2]) - 1
                    definition_index.append((t, line))
            self.defer_counter -= 1
            log_info("done parse %s 3", file_id)
            self.protocol.dosomething("done_parse", file_id, word_index, definition_index)

        def parse_definition_error(error):
            log.info("%s parse_definition_error %s", self, error)
            self.defer_counter -= 1
            log_info("done parse %s 2", file_id)
            self.protocol.dosomething("done_parse", file_id, word_index, definition_index)

        # d = utils.getProcessOutput(r"C:\Python27\python.exe", ["1.py"])
        self.defer_counter += 1
        d = utils.getProcessOutput(ctags_path, ["-xu", path])
        d.addCallback(parse_definition_result)
        d.addErrback(parse_definition_error)

    def exit(self, *args, **kw):
        log_info("exit")
        reactor.stop()

class Stdio(JsonRpc, protocol.Protocol):

    Handler = Worker

    def connectionMade(self):
        JsonRpc.connectionMade(self)
        log_info("Stdio connectionMade")

    def dataReceived(self, data):
        log_info("Stdio dataReceived %s", repr(data))
        JsonRpc.dataReceived(self, data)

def main():
    log_info("main %s", sys.argv)

    stdio = Stdio()
    StandardIO(stdio)

    reactor.run()

# old code

# newcode 

class PinoProtocolHandler(object):

    def fuck(self, *args, **kw):
        log_info("---------------- %s %s"  % (args, kw))
        log_info("---------------- %s %s"  % (args, kw))
        log_info("---------------- %s %s"  % (args, kw))
        log_info("---------------- %s %s"  % (args, kw))

    def bytes_to_string(self, source):
        for encoding in self.encodings:
            try:
                return source.decode(encoding)
            except UnicodeDecodeError:
                continue
        return ""

    def parse_file(self, params):
        log_info("%s parse_file %s", self, params)
        path, type_, file_id = params["args"]

        import string
        default_name_chars = string.ascii_letters + string.digits + "_"

        name_chars = languages.name_chars.get(type_, default_name_chars)
        language_keywords = languages.keywords.get(type_, [])

        add_definition = self.definition.add_name
        add_word = self.root.add_name

        definition_index = []
        word_index = []

        root_levels = self.root_levels
        definition_levels = self.definition_levels

        binary = ""
        with open(path, 'rb') as rf:
            binary = rf.read()
            self.bytes += len(binary)
            source = self.bytes_to_string(binary)
            self.file_contents[file_id] = source

            line = 0
            word = ""
            words = []
            b, e = 0, 0
            for char in source:
                if char in name_chars or ord(char) > 0xff:
                    word += char
                else:
                    if word:
                        words.append(word)
                        word = ""

                    if char == "\n":
                        # log.debug("%s %s", line, words)
                        for i, t in enumerate(words):
                            if t in language_keywords:
                                continue
                            if type_ == ".py":
                                if words[0] in ("def", "class") and i == 1:
                                    definition_index.append((t, line))
                            word_index.append((t, line))

                        line += 1
                        words = []

        if type_ != ".py":
            self.parse_definition(path, file_id, word_index, definition_index)
        else:
            log_info("done parse %s 1", file_id)
            self.protocol.dosomething("done_parse", file_id, word_index, definition_index)

    def parse_definition(self, path, file_id, word_index, definition_index):
        log_info("%s parse_definition %s", self, path)

        def parse_definition_result(result):
            for line in result.split('\n'):
                # line = line.rstrip()
                ps = line.split()
                if len(ps) >= 2 and ps[2].isdigit():
                    t = ps[0]
                    line = int(ps[2]) - 1
                    definition_index.append((t, line))
            self.defer_counter -= 1
            log_info("done parse %s 3", file_id)
            self.protocol.dosomething("done_parse", file_id, word_index, definition_index)

        def parse_definition_error(error):
            log.info("%s parse_definition_error %s", self, error)
            self.defer_counter -= 1
            log_info("done parse %s 2", file_id)
            self.protocol.dosomething("done_parse", file_id, word_index, definition_index)

        # d = utils.getProcessOutput(r"C:\Python27\python.exe", ["1.py"])
        self.defer_counter += 1
        d = utils.getProcessOutput(ctags_path, ["-xu", path])
        d.addCallback(parse_definition_result)
        d.addErrback(parse_definition_error)


class ProxyClient(JsonRpc, protocol.Protocol):

    Handler = PinoProtocolHandler
    
class ProxyClientFactory(protocol.ClientFactory):

    protocol = ProxyClient


def main():
    log_info("main %s", sys.argv)

    f = ProxyClientFactory()
    reactor.connectTCP("127.0.0.1", 10241, f)

    reactor.run()
