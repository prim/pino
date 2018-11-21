# encoding: utf8

from jsonrpc import JsonRpc
from core import Project
from twisted.internet import protocol

import log
import core
import os.path
import fnmatch

class PinoProtocolHandler(object):

    """
    for prim/pino.vim

python pino cli py27stdlib test
python pino cli py27stdlib search_file sock
python pino cli py27stdlib completion SOCK 10
python pino cli py27stdlib search_word HTTP 1
python pino cli py27stdlib search_word HTTP 2
python pino cli py27stdlib search_word PinoProtocolHandler 0

    """

    def __init__(self):
        self.project = None

    def __str__(self):
        return "Pino(%s)" % (self.project.name if self.project else "")

    def __repr__(self):
        return "Pino(%s)" % (self.project.name if self.project else "")

    def _(self, params):
        old_project = self.project
        project_name = params.get("project")
        cwd = params.get("cwd")
        cwf = params.get("cwf")
        project = None
        if project_name:
            project = Project.get(project_name)
        if not project and cwd:
            project = Project.find(cwd)
        if not project and cwf:
            project = Project.find(cwf)
        if not project and 0:
            if os.path.isfile(cwf):
                cwd = os.path.dirname(cwf)
                while True:
                    p = os.path.join(cwd, ".git")
                    print(1, cwd, p)
                    if os.path.isdir(p):
                        name = os.path.basename(cwd)
                        log.info("new proejct %s", name)
                        project = Project.new(name, cwd)
                        break
                    new = os.path.dirname(cwd)
                    if new == cwd:
                        break
                    cwd = new
        if project is old_project:
            return 
        self.project = project
        project.init_or_load()
        log.info("%s set project old %s new %s", self, old_project, project)

    def completion(self, params):
        log.debug("%s completion %s", self, params)
        self._(params)
        ret = []
        project = self.project
        keyword = params["args"][0]

        key = ""
        for char in keyword[::-1]:
            if char in core.default_name_chars:
                key += char
            else:
                break
        keyword = key[::-1]
        if not keyword:
            return 

        maxn = int(params["args"][1])
        maxn = 1000000
        root = project.root.prefix(keyword)
        log.debug("%s completion %s %s %s", self, params, keyword, root)
        if root:
            for v in root.all_children():
                name = v.node_name()

                # 删除无效的名字
                for file_id, line in v.tvalues:
                    try:
                        project.file_contents[file_id]
                        break
                    except KeyError:
                        pass
                else:
                    continue

                ret.append(name)
                if len(ret) >= maxn:
                    break

        return "\n".join(ret)

    def search_word(self, params):
        log.debug("%s search_word %s", self, params)
        self._(params)
        ret = []
        keyword = params["args"][0]
        mode = int(params["args"][1])
        project = self.project


        # https://groups.google.com/forum/#!topic/vim_use/qC-S-P5Yr-A
        def f(file_id, lines):
            # 可能file_id已经因为file modify|move|delete 失效了
            try:
                source = project.file_contents[file_id]
            except KeyError:
                return 
            file_path = project.file_pathes[file_id]
            linenum = 0
            begin = 0
            for i, char in enumerate(source):
                if char == '\n':
                    if linenum in lines:
                        # ret.append("%s:%d:%s" % (file_path, linenum + 1, source[begin:i].rstrip()))
                        ret.append({"filename":file_path, "lnum": linenum + 1, "text": source[begin:i].rstrip()})
                    begin = i + 1

                    linenum += 1

        # TODO: part match definition
        if mode == 1 or mode == 0:
            # full match 1
            if mode == 1:
                v = project.root.get_name(keyword)
                if v:
                    todo = {}
                    for file_id, line in v.tvalues:
                        todo.setdefault(file_id, set()).add(line)
                    for file_id, lines in todo.items():
                        f(file_id, lines)
            # goto definition 0
            else:
                # v = project.definition.get_name(keyword)
                maxn = 0xffff
                print 1, keyword, mode, maxn
                for v in project.definition.match(keyword, maxn, project.definition_levels):
                    print 2, v
                    todo = {}
                    for file_id, line in v.tvalues:
                        todo.setdefault(file_id, set()).add(line)
                    for file_id, lines in todo.items():
                        f(file_id, lines)

        # part match 2
        else:
            maxn = 0xffff
            for v in project.root.match(keyword, maxn, project.root_levels):
                todo = {}
                for file_id, line in v.tvalues:
                    todo.setdefault(file_id, set()).add(line)
                for file_id, lines in todo.items():
                    f(file_id, lines)

        ret.sort(key = lambda item: (item["filename"], item["lnum"]))
        return ret
        # return "\n".join(ret)

    def search_file(self, params):
        log.debug("%s search_file %s", self, params)
        self._(params)
        ret = []
        pattern = params["args"][0]
        fnm = "*" in pattern
        project = self.project
        for _, path in project.file_pathes.items():
            if not isinstance(path, str):
                continue
            if fnm:
                if fnmatch.fnmatch(path, pattern):
                    ret.append({"filename":path, "lnum": 1, "text": ""})
                    # ret.append("%s:1:freedom" % path)
            elif pattern in path:
                ret.append({"filename":path, "lnum": 1, "text": ""})
                # ret.append("%s:1:freedom" % path)

        # ret.insert(0, '[Search results for pattern: "%s"]' % pattern)
        # quickfix = "\n".join(ret)
        # return quickfix
        return ret

    def init(self, params):
        log.debug("%s init %s", self, params)
        self._(params)
        self.project.init()

    def reinit(self, params):
        log.debug("%s reinit %s", self, params)
        self._(params)
        self.project.reinit()

    def stat(self, params):
        log.debug("%s stat %s", self, params)
        self._(params)
        return self.project.stat()

    def load(self, params):
        log.debug("%s load %s", self, params)
        self._(params)
        self.project.load()

    def save(self, params):
        log.debug("%s save %s", self, params)
        self._(params)
        self.project.save()

class PinoProtocol(JsonRpc, protocol.Protocol):

    Handler = PinoProtocolHandler

