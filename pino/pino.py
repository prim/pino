
from jsonrpc import JsonRpcProtocol
from core import Project

import log
import core

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
        root = project.root.get_name(keyword, False)
        log.debug("%s completion %s %s %s", self, params, keyword, root)
        if root:
            for v in root.all_children():
                name = v.node_name()
                ret.append(name)
                if len(ret) >= maxn:
                    break
        return "\n".join(ret)

    def search_word(self, params):
        log.debug("%s search_words %s", self, params)
        self._(params)
        ret = []
        keyword = params["args"][0]
        mode = int(params["args"][1])
        project = self.project


        # https://groups.google.com/forum/#!topic/vim_use/qC-S-P5Yr-A
        def f(file_id, lines):
            source = project.file_contents[file_id]
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
        # goto definition 0
        # full match 1
        if mode == 1 or mode == 0:
            if mode == 1:
                v = project.root.get_name(keyword)
            else:
                v = project.definition.get_name(keyword)
            if v:
                todo = {}
                for file_id, line in v.tvalues:
                    todo.setdefault(file_id, set()).add(line)
                for file_id, lines in todo.items():
                    f(file_id, lines)

        # part match 2
        else:
            maxn = 0xffff
            for v in project.root.match_name(keyword, maxn, project.root_levels):
                todo = {}
                for file_id, line in v.tvalues:
                    todo.setdefault(file_id, set()).add(line)
                for file_id, lines in todo.items():
                    f(file_id, lines)

        # ret.insert(0, '[Search results for pattern: "%s"]' % keyword)
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

    def reinit(self, params):
        log.debug("%s reinit %s", self, params)
        self._(params)
        self.project.reinit()

    def stat(self, params):
        log.debug("%s stat %s", self, params)
        self._(params)
        return self.project.stat()

    def save(self, params):
        log.debug("%s save %s", self, params)
        self._(params)
        self.project.save()

class PinoProtocol(JsonRpcProtocol):

    Handler= PinoProtocolHandler
