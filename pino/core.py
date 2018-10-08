# encoding: utf8

import os
import time
import string
import traceback
import languages

import log

from config import project_info
from utils import uri_to_path, path_to_uri
from document import Document

from os.path import splitext

import trie
from trie import Trie

# import cPickle as pickle
import pickle
import fnmatch

# default_name_chars = string.letters + string.digits + "_"
default_name_chars = string.ascii_letters + string.digits + "_"
default_skip_directories = [".svn", ".git", ]
default_file_black_list = [
    ".o",
    ".pyc",
]

class Project(object):

    projects = {}

    def __init__(self, name=None, sources=None, file_white_list=None, file_black_list=None, skip_directories=None, init=False):
        self.name = name
        self.sources = sources
        self.data_file_path = os.path.join(sources[0], ".pino")
        self.file_white_list = file_white_list
        self.file_black_list = file_black_list
        self.skip_directories = skip_directories

        self.encodings = ["utf8", "gbk", "ascii"]
        self._()

        log.info("new project %s %s", name, self.__dict__)

        self.inited = False
        if init:
            self.init_or_load()

    def _(self):
        self.file_id = 0
        self.file_pathes = {}

        self.bytes = 0
        self.file_contents = {}

        self.root_levels = {}
        self.definition_levels = {}
        self.root = Trie(self.root_levels)
        self.definition = Trie(self.definition_levels)

        self.long_words = {}
        self.long_word_definition = {}

        self.word_length_stat = {}

    def is_long_word(self, word):
        return len(word) >= 38

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @classmethod
    def get(klass, name):
        return klass.projects.get(name)

    @classmethod
    def find(klass, path):
        log.info("find_project %s", path)
        project = None
        for p in klass.projects.values():
            log.info("find_project name %s %s", p.name, path)
            if p.name == path:
                project = p
                break
            for sp in p.sources:
                log.info("find_project sources %s %s", sp, path)
                if path.startswith(sp):
                    project = p
                    break
                print(1)
            if project: break
        return project

    def init_or_load(self):
        if self.inited:
            return 
        self.inited = True
        begin = time.time()
        if os.path.isfile(self.data_file_path):
            self.load()
        else:
            self.init()
            # TODO no need this later
            self.save()
        end = time.time()
        log.info("%s init_or_load %0.8f" , self, end - begin)

    def init(self):
        log.info("%s init" , self)
        from os.path import splitext

        white_list = self.file_white_list
        black_list = self.file_black_list

        def f(base):
            from os.path import join, isfile, isdir
            for name in os.listdir(base):
                path = join(base, name)
                path = path.replace("/", "\\")
                if isdir(path) and path not in self.skip_directories:
                    f(path)
                if isfile(path):
                    _, file_extension = splitext(name)
                    if black_list and file_extension in black_list:
                        log.debug("%s init black %s", self, name)
                    elif not white_list or file_extension in white_list:
                        self.parse_file(file_extension, path)
                    else:
                        log.debug("%s init skip %s", self, name)

        for path in self.sources:
            f(path)

    def load(self):
        log.info("%s load %s" , self, self.data_file_path)
        with open(self.data_file_path, "rb") as f:
            binary = f.read()
            data = pickle.loads(binary)
            self.__dict__.update(data)

    def save(self):
        begin = time.time() 
        data = {}
        for name in (
                "file_id", "file_pathes", 
                "bytes", "file_contents",
                "root", "definition", 
                "root_levels", "definition_levels",
                "long_words", "long_word_definition",
                "word_length_stat",
                ):
            data[name] = getattr(self, name)
        with open(self.data_file_path, "wb") as f:
            f.write(pickle.dumps(data))
        end = time.time()
        log.info("%s save %0.8f" , self, end - begin)

    def bytes_to_string(self, source):
        for encoding in self.encodings:
            try:
                return source.decode(encoding)
            except UnicodeDecodeError:
                continue
        return ""

    def parse_file(self, type_, path):
        # if path != r"E:\netease\g58\server\hmt20180716\MobileServer\mobilerpc\TcpClient.py":
        #     return 
        log.debug("%s parse_file %s", self, path)
        try:
            file_id = self.file_pathes[path]
        except KeyError:
            self.file_id += 1
            file_id = self.file_id
            self.file_pathes[file_id] = path
            self.file_pathes[path] = file_id

        name_chars = languages.name_chars.get(type_, default_name_chars)
        language_keywords = languages.keywords.get(type_, [])
        word_length_stat = self.word_length_stat

        add_definition= self.definition.add_name
        add_word = self.root.add_name

        root_levels = self.root_levels
        definition_levels = self.definition_levels

        is_long_word = self.is_long_word

        with open(path, 'rb') as rf:
            binary = rf.read()
            self.bytes += len(binary)
            source = self.bytes_to_string(binary)
            if not source:
                log.debug("%s parse_file encoding error %s", self, path)
                return 
            self.file_contents[file_id] = source

            line = 0
            word = ""
            words = []
            count = 0
            first = ""
            b, e = 0, 0
            for char in source:
                if char in name_chars or ord(char) > 0xff:
                    word += char
                else:
                    if word:
                        words.append(word)
                        if count == 0:
                            first = word
                        word = ""
                        count += 1

                    if char == "\n":
                        # log.debug("%s %s", line, words)
                        for i, t in enumerate(words):
                            if t in language_keywords:
                                continue
                            if is_long_word(t):
                                if first in ("def", "class"):
                                    self.long_word_definition.setdefault(t, {}).setdefault(file_id, set()).add(line)
                                self.long_words.setdefault(t, {}).setdefault(file_id, set()).add(line)
                            else:
                                if words[0] in ("def", "class") and i == 1:
                                    add_definition(t, (file_id, line), definition_levels)
                                if add_word(t, (file_id, line), root_levels):
                                    length = len(t)
                                    word_length_stat[length] = word_length_stat.get(length, 0) + 1

                        count = 0
                        first = ""
                        line += 1
                        words = []
            # print("---", len(word))

    def reinit(self):
        self._()
        self.init()

    def stat(self):
        print("word_length_stat")
        for k, v in sorted(self.word_length_stat.items()):
            print(k, v)

        print("trie", trie.Trie.trie_n)

        s = 0
        n = 0
        from sys import getsizeof
        print(s, n, "bytes", self.bytes)

def init_project():
    for name, info in project_info.items():
        root = info.get("root", "")
        # root = root.replace("\\", "/")
        sources = info.get("sources", [])
        assert(root or sources)
        if not sources and root not in sources:
            sources.insert(0, root)
        for i, v in enumerate(sources):
            sources[i] = v
            # sources[i] = v.replace("\\", "/")
        kw = {
            "name":name,
            "sources":sources,
            "init":info.get("init", False),
            "skip_directories":info.get("skip_directories", default_skip_directories),
            "file_white_list":info.get("file_white_list", []),
            "file_black_list":info.get("file_black_list", default_file_black_list),
        }
        Project.projects[name] = Project(**kw)
