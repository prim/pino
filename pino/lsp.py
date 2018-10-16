
"""
line begin from 0
character begin from 0
"""
import sys

import json
import log
import traceback
import core

from pprint import pprint, pformat

from core import Project
from utils import uri_to_path, path_to_uri

from jsonrpc import JsonRpcProtocol

class TextDocumentSyncKind:

    NONE = 0
    FULL = 1
    INCREMENTAL = 2

def lines(content):
    return content.split('\n')

class Documents(object):

    def __init__(self):
        self.documents = {}

    def get(self, path):
        l = self.documents.get(path.upper())
        if l:
            return l
        with open(path, "rb") as rf:
            content = rf.read()
            content = content.decode("utf8")
            l = lines(content)
            # self.documents[uri] = l
            self.documents[path.upper()] = l
            return l

    def open(self, uri): 
        path = uri_to_path(uri)
        with open(path, "rb") as rf:
            content = rf.read()
            content = content.decode("utf8")
            l = lines(content)
            # TODO
            self.documents[uri] = l
            self.documents[path.upper()] = l

    def close(self, uri): 
        path = uri_to_path(uri)
        self.documents.pop(uri, None)

    def change(self, uri, content):
        path = uri_to_path(uri)
        l = lines(content)
        self.documents[uri] = l
        self.documents[path.upper()] = l

    def _solveTextDocumentPostionParams(self, params):
        uri = params["textDocument"]["uri"]
        linenum = params["position"]["line"]
        character = params["position"]["character"]
        lines = self.documents[uri]
        l = c = 0

        import string
        default_name_chars = string.ascii_letters + string.digits + "_"

        word = ""
        for i, line in enumerate(lines):
            if i == linenum:
                for char in line:
                    print char, word, 888
                    if char in default_name_chars:
                        word += char
                    else:
                        if c >= character:
                            return word
                        word = ""

                    c += 1
        return word

class LanguageServerProtocolHandler(object):

    def __init__(self):
        self.project = None
        self.documents = Documents()

    def __str__(self):
        return "LSP(%s)" % (self.project.name if self.project else "")

    def __repr__(self):
        return "LSP(%s)" % (self.project.name if self.project else "")

    # private
    def _(self, params):
        old_project = self.project
        project = None

        root_path = params.get("rootPath")
        if root_path:
            pass
        root_uri = params.get("rootUri")
        if root_uri:
            pass
        folders = params.get("wordspaceFolders")
        if folders:
            pass

        uri = params.get("textDocument", {}).get("uri")
        if uri:
            path = uri_to_path(uri)
            project = Project.find(path)

        if project is old_project:
            return 
        self.project = project
        project.init_or_load()
        log.info("%s set project old %s new %s", self, old_project, project)

    def _solveTextDocumentPostionParams(self, params):
        return self.documents._solveTextDocumentPostionParams(params)

    # General
    #========================================================
    def initialize(self, params):
        log.info("%s initialize %s", self, params)
        self._(params) 
        return {'capabilities': self._capabilities()}

    def initialized(self, params):
        log.info("%s initialized %s", self, params)

    def shutdown(self, params):
        pass

    def exit(self, params):
        pass

    def cancelRequest(self, params):
        pass

    # Window
    #========================================================
    def showMessage(self):
        pass

    def showMessageRequest(self):
        pass

    def logMessage(self):
        pass

    # Telemetry
    #========================================================
    def event(self):
        pass

    # Client
    #========================================================
    def registerCapability(self):
        pass

    def unregisterCapability(self):
        pass

    # Workspace
    #========================================================
    def workspace_workspaceFolders(self, params):
        pass

    def workspace_didChangeWorkspaceFolders(self, params):
        pass

    def workspace_didChangeConfiguration(self, params):
        pass

    def workspace_configuration(self, params):
        pass

    def workspace_didChangeWatchedFiles(self, params):
        pass

    def workspace_symbol(self, params):
        pass

    def workspace_exetuteCommand(self, params):
        pass

    def workspace_applyEdit(self, params):
        pass

    # Text Synchronizeation
    #========================================================
    def textDocument_didOpen(self, params):
        log.info("%s textDocument_didOpen %s", self, params)
        self._(params)
        self.documents.open(params["textDocument"]["uri"])

    def textDocument_didClose(self, params):
        log.info("%s textDocument_didClose %s", self, params)
        self._(params)
        self.documents.close(params["textDocument"]["uri"])

    def textDocument_didChange(self, params):
        log.info("%s textDocument_didChange %s", self, params)
        self._(params)
        self.documents.change(params["textDocument"]["uri"], params["contentChanges"][0]["text"])

    def textDocument_willSave(self, params):
        self._(params)
        return None

    def textDocument_willSaveWaitUntil(self, params):
        self._(params)
        return []

    def textDocument_didSave(self, params):
        self._(params)
        return []

    # Language Features
    #========================================================
    def textDocument_completion(self, params):
        log.info("%s textDocument_completion %s", self, params)
        self._(params)
        p = self.project
        if not p:
            return 
        symbol = self._solveTextDocumentPostionParams(params)
        log.info("%s textDocument_completion %s", self, symbol)
        if not symbol:
            return 

        l = []
        maxn = 100
        root = p.root.get_name(symbol, False)
        for v in root.all_children():
            name = v.node_name()
            l.append({"label":name})
            if len(l) >= maxn:
                break
        return l

    def textDocument_hover(self, params):
        log.info("%s textDocument_hover %s", self, params)
        return {"contents": "sd"}

        return {"contents":"sdfsdfds\n123123\nasdffd\n1df\nsfasf"}
        p = self.project
        if not p:
            return 
        p.init_or_load()
        symbol = self._solveTextDocumentPostionParams(params)
        log.info("%s textDocument_completion %s", self, symbol)
        if not symbol:
            return 
        l = []
        result = {"isIncomplete": True, "items":l}
        maxn = 100
        root = p.root.get_name(symbol)
        for v in root.all_children():
            name = v.node_name()[::-1]
            l.append({"label":name})
            if len(l) >= maxn:
                break
        return result

    def textDocument_signatureHelp(self, params):
        pass

    def textDocument_definition(self, params):
        log.info("%s textDocument_definition %s", self, params)
        symbol = self._solveTextDocumentPostionParams(params)
        log.info("%s textDocument_definition %s", self, symbol)
        if not symbol:
            return []

        v = self.project.definition.get_name(symbol)

        result = []
        for a, b in v.tvalues:
            path = self.project.file_pathes[a]

            lines = self.documents.get(path)
            for i, line in enumerate(lines):
                if b == i:
                    index = line.find(symbol)
                    result.append({
                        "uri":path_to_uri(path), 
                        "range": {
                            "start": {"line": b, "character": index},
                            "end": {"line": b, "character": index + len(symbol)},
                        },
                    })
        return result

    def textDocument_typeDefinition(self, params):
        pass

    def textDocument_implementation(self, params):
        pass

    def textDocument_references(self, params):
        log.info("%s textDocument_references %s", self, params)
        symbol = self._solveTextDocumentPostionParams(params)
        log.info("%s textDocument_references %s", self, symbol)
        if not symbol:
            return []

        result = []
        for v in [self.project.root.get_name(symbol)]:
            for a, b in v.tvalues:
                path = self.project.file_pathes[a]
                lines = self.documents.get(path)
                for i, line in enumerate(lines):
                    if b == i:
                        index = line.find(symbol)
                        result.append({
                            "uri":path_to_uri(path), 
                            "range": {
                                "start": {"line": b, "character": index},
                                "end": {"line": b, "character": index + len(symbol)},
                            },
                        })
        return result

        locations = []
        for uri, c in self.documents.documents.items():
            locations.append({"uri": uri, "range": {"start": {"line":0, "character": 0}, "end": {"line":0, "character": 3}}})
            locations.append({"uri": uri, "range": {"start": {"line":1, "character": 0}, "end": {"line":1, "character": 3}}})
            locations.append({"uri": uri, "range": {"start": {"line":2, "character": 0}, "end": {"line":2, "character": 3}}})
        return locations

        # TODO

    def textDocument_documentHighlight(self, params):
        pass

    def textDocument_documentSymbol(self, params):
        pass

    def textDocument_codeAction(self, params):
        pass
        return []

    def textDocument_codeLens(self, params):
        log.info("%s textDocument_codeLens %s", self, params)
        return []

    def codeLens_resolve(self, params):
        pass

    def textDocument_documentLink(self, params):
        pass

    def documentLink_resolve(self, params):
        pass

    def textDocument_documentColor(self, params):
        pass

    def textDocument_colorPresentation(self, params):
        pass

    def textDocument_formatting(self, params):
        pass

    def textDocument_rangeFormatting(self, params):
        pass

    def textDocument_onTypeFormatting(self, params):
        pass

    def textDocument_rename(self, params):
        pass

    def textDocument_prepareRename(self, params):
        pass

    def textDocument_foldingRange(self, params):
        pass


    #========================================================
    def _capabilities(self):
        server_capabilities = {
            # 'codeActionProvider': True,
            # 'codeLensProvider': {
            #     'resolveProvider': True,
            # },
            'completionProvider': {
                'resolveProvider': True,
                'triggerCharacters': ['.']
            },
            # 'documentFormattingProvider': True,
            # 'documentHighlightProvider': True,
            # 'documentRangeFormattingProvider': True,
            # 'documentSymbolProvider': True,
            'definitionProvider': True,
            # 'executeCommandProvider': {
            # },
            'hoverProvider': False,
            'referencesProvider': True,
            # 'renameProvider': True,
            # 'signatureHelpProvider': {
            #     'triggerCharacters': ['(', ',']
            # },
            'textDocumentSync': {
                'openClose': True,
                'change': TextDocumentSyncKind.FULL,
                'willSave': True,
                'willSaveWaitUntil': True,
                'save': True,
            }
            # 'experimental': merge(self._hook('pyls_experimental_capabilities'))
        }
        # log.info('Server capabilities: %s', server_capabilities)
        return server_capabilities

class LanguageServerProtocol(JsonRpcProtocol):

    Handler= LanguageServerProtocolHandler

