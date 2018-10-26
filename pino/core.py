# encoding: utf8

import os
import time
import string
import languages
import filesystem

import log

from config import project_info

from os.path import splitext

from radix_tree import RadixTree

try:
    import cPickle as pickle
except ImportError:
    import pickle

default_name_chars = string.ascii_letters + string.digits + "_"
default_skip_directories = [".svn", ".git", ]
default_file_black_list = [
    ".o",
    ".pyc",
    ".log",
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

        log.info("new project %s %s", name, self.sources)

        self.inited = False
        if init:
            self.init_or_load()

    def _(self):
        self.file_id = 0
        self.file_pathes = {}
        self.file_contents = {}

        self.bytes = 0

        self.root_levels = {}
        self.root = RadixTree(None, "", ())

        self.definition_levels = {}
        self.definition = RadixTree(None, "", ())

        self.word_length_stat = {}

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def generate_levels(self):
        def f(st, t, lv):
            if not t.list:
                return 
            st.setdefault(lv, set()).add(t)
            for s in t.list:
                f(st, s, lv + 1)
        f(self.root_levels, self.root, 0)
        f(self.definition_levels, self.definition, 0)

    @classmethod
    def new(klass, name, root):
        assert(name not in klass.projects)
        kw = {
            "name": name,
            "sources": [root],
            "init": False, 
            "skip_directories": default_skip_directories,
            "file_white_list": [],
            "file_black_list": default_file_black_list,
        }
        klass.projects[name] = p = Project(**kw)
        return p

    @classmethod
    def get(klass, name):
        return klass.projects.get(name)

    @classmethod
    def find(klass, path):
        # log.info("find_project %s", path)
        project = None
        for p in klass.projects.values():
            # log.info("find_project name %s %s", p.name, path)
            if p.name == path:
                project = p
                break
            for sp in p.sources:
                # log.info("find_project sources %s %s", sp, path)
                if path.startswith(sp):
                    project = p
                    break
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
            self.save()
        end = time.time()
        log.info("%s init_or_load %0.8f" , self, end - begin)

    def init(self):
        log.info("%s init" , self)

        def f(base):
            from os.path import join, isfile, isdir
            for name in os.listdir(base):
                if name[0] == ".":
                    continue
                path = join(base, name)
                path = path.replace("/", "\\")
                if isdir(path):
                    #                                   .svn .git
                    if path in self.skip_directories or os.path.basename(path) in self.skip_directories:
                        continue
                    f(path)

                elif isfile(path):
                    self.on_file_created(path)

        for path in self.sources:
            filesystem.watch(path)
            f(path)

        self.generate_levels()

    def load(self):
        begin = time.time() 
        with open(self.data_file_path, "rb") as f:
            binary = f.read()
            data = pickle.loads(binary)
            self.__dict__.update(data)
        self.generate_levels()
        end = time.time()
        log.info("%s save %0.8f" , self, end - begin)

    def save(self):
        begin = time.time() 
        data = {}
        for name in (
                "file_id", "file_pathes", 
                "bytes", "file_contents",
                "root", "definition", 
                "root_levels", "definition_levels",
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

    def validate_file(self, path):
        _, file_extension = splitext(path)
        if not file_extension:
            file_extension = os.path.basename(path)

        white_list = self.file_white_list
        black_list = self.file_black_list

        if black_list and file_extension in black_list:
            log.debug("%s validate_file black %s %s", self, path, black_list)
        elif not white_list or file_extension in white_list:
            return file_extension

        else:
            log.debug("%s validate_file skip %s", self, path)

    def on_file_created(self, path):
        log.info("%s on_file_created %s", self, path)
        file_extension = self.validate_file(path)
        if not file_extension:
            return 
        if not os.path.isfile(path):
            return 

        old_file_id = self.file_pathes.pop(path, None)
        if old_file_id:
            self.file_pathes.pop(path, None)
            self.file_contents.pop(old_file_id, None)

        self.file_id += 1
        file_id = self.file_id
        self.file_pathes[file_id] = path
        self.file_pathes[path] = file_id
        self.parse_file(path, file_extension, file_id)

    def on_file_deleted(self, path):
        log.info("%s on_file_deleted %s", self, path)
        file_extension = self.validate_file(path)
        if not file_extension:
            return 

        old_file_id = self.file_pathes.pop(path, None)
        if old_file_id:
            self.file_pathes.pop(path, None)
            self.file_contents.pop(old_file_id, None)

    def on_file_modifed(self, path):
        log.info("%s on_file_modify %s", self, path)
        file_extension = self.validate_file(path)
        if not file_extension:
            return 

        old_file_id = self.file_pathes.pop(path, None)
        if old_file_id:
            self.file_pathes.pop(path, None)
            self.file_contents.pop(old_file_id, None)

        self.file_id += 1
        file_id = self.file_id
        self.file_pathes[file_id] = path
        self.file_pathes[path] = file_id
        self.parse_file(path, file_extension, file_id)

    def on_file_moved(self, fpath, tpath):
        log.info("%s on_file_moved %s %s", self, fpath, tpath)
        self.on_file_deleted(fpath)
        self.on_file_created(tpath)

    def parse_file(self, path, type_, file_id):
        log.debug("%s parse_file %s %s %s", self, path, type_, file_id)

        name_chars = languages.name_chars.get(type_, default_name_chars)
        language_keywords = languages.keywords.get(type_, [])
        word_length_stat = self.word_length_stat

        add_definition= self.definition.add_name
        add_word = self.root.add_name

        root_levels = self.root_levels
        definition_levels = self.definition_levels

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
                            if words[0] in ("def", "class") and i == 1:
                                add_definition(t, (file_id, line), definition_levels)
                            if add_word(t, (file_id, line), root_levels):
                                length = len(t)
                                word_length_stat[length] = word_length_stat.get(length, 0) + 1

                        line += 1
                        words = []

    def reinit(self):
        self._()
        self.init()

    def stat(self):
        print("word_length_stat")
        for k, v in sorted(self.word_length_stat.items()):
            print(k, v)

        st = {}
        def f(t, lv):
            if not t.list:
                return 
            st[lv] = st.get(lv, 0) + 1
            for s in t.list:
                f(s, lv + 1)

        f(self.root, 0)
        print "all", self.root.n

        for k, v in sorted(st.items()):
            print k, v

def init_project():
    for name, info in project_info.items():
        root = info.get("root", "")
        # root = root.replace("\\", "/")
        sources = info.get("sources", [])
        if type(sources) is str:
            sources = [sources]
        assert(root or sources)
        if not sources and root not in sources:
            sources.insert(0, root)
        for i, v in enumerate(sources):
            sources[i] = v
            # sources[i] = v.replace("\\", "/")
        skip = info.get("skip_directories", default_skip_directories)
        for t in default_skip_directories[:]:
            if t not in skip:
                skip.append(t)
        kw = {
            "name":name,
            "sources":sources,
            "init":info.get("init", False),
            "skip_directories":skip,
            "file_white_list":info.get("file_white_list", []),
            "file_black_list":info.get("file_black_list", default_file_black_list),
        }
        Project.projects[name] = Project(**kw)

