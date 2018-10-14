
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


class Documents(object):

    def __init__(self):
        self.documents = {}

    def open(self, uri): 
        path = uri_to_path(uri)
        with open(path, "rb") as rf:
            content = rf.read()
            # TODO
            self.documents[uri] = content.decode("utf8")
            print(self.documents[uri], 999)

    def close(self, uri): 
        path = uri_to_path(uri)
        self.documents.pop(uri, None)

    def change(self, uri, content):
        path = uri_to_path(uri)
        self.documents[uri] = content
        print(content, type(content))

    def _solveTextDocumentPostionParams(self, params):
        uri = params["textDocument"]["uri"]
        line = params["position"]["line"]
        character = params["position"]["character"]
        content = self.documents[uri]
        l = c = 0

        word = ""
        for char in content:
            if char == "\n":
                c = 0
                l += 1

            if l == line:
                if char in "abcde":
                    word += char
                else:
                    if c >= character:
                        return word
                    word = ""
            c += 1

class LanguageServerProtocolHandler(object):

    def __init__(self):
        self.project = None
        self.documents = Documents()

    def __str__(self):
        return "LSP(%s)" % (self.project.name if self.project else "")

    def __repr__(self):
        return "LSP(%s)" % (self.project.name if self.project else "")

    # private
    def _set_project(self, path_or_uri):
        return 
        old_project = self.project
        project = Project.find(path_or_uri)
        if project is None:
            project = Project.find_project(uri_to_path(path_or_uri))
        if project is old_project:
            return 
        self.project = project
        log.info("set project old %s new %s", old_project, project)

    def _solveTextDocumentPostionParams(self, params):
        return self.documents._solveTextDocumentPostionParams(params)

    # General
    #========================================================
    def initialize(self, params):
        log.info("%s initialize %s", self, params)
        # self._set_project(params.get("rootPath", ""))
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
        self.documents.open(params["textDocument"]["uri"])

    def textDocument_didClose(self, params):
        log.info("%s textDocument_didClose %s", self, params)
        self.documents.close(params["textDocument"]["uri"])

    def textDocument_didChange(self, params):
        log.info("%s textDocument_didChange %s", self, params)
        self.documents.change(params["textDocument"]["uri"], params["contentChanges"][0]["text"])

    def textDocument_willSave(self, params):
        return None

    def textDocument_willSaveWaitUntil(self, params):
        return []

    def textDocument_didSave(self, params):
        return []

    # Language Features
    #========================================================
    def textDocument_completion(self, params):
        log.info("%s textDocument_completion %s", self, params)
        import time
        time.sleep(3)
        return [
            {"label":"a"},
            {"label":"ab"},
            {"label":"abc"},
            {"label":"abcd"},
            {"label":"abcde"},
        ]

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
        maxn = 10
        root = p.root.get_name(symbol)
        for v in root.all_children():
            name = v.node_name()[::-1]
            l.append({"label":name})
            if len(l) >= maxn:
                break
        return result

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
        pass

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

        locations = []
        for uri, c in self.documents.documents.items():
            locations.append({"uri": uri, "range": {"start": {"line":0, "character": 0}, "end": {"line":0, "character": 3}}})
            locations.append({"uri": uri, "range": {"start": {"line":1, "character": 0}, "end": {"line":1, "character": 3}}})
            locations.append({"uri": uri, "range": {"start": {"line":2, "character": 0}, "end": {"line":2, "character": 3}}})
        return locations

        # TODO
        result = []
        for v in [p.root.get_name(symbol)]:
            for a, b in v.tvalues:
                path = p.file_pathes[a]
                result.append({
                    "uri":path_to_uri(path), 
                    "range": {
                        "start": {"line": b, "character": 0},
                        "end": {"line": b, "character": 10},
                    },
                })
        return result

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
            'hoverProvider': True,
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

