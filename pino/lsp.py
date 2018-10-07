
import sys

import json
import log
import traceback
import core

from pprint import pprint, pformat

from core import Project
from utils import uri_to_path, path_to_uri

from jsonrpc import JsonRpcProtocol

class LanguageServerProtocolHandler(object):

    def __init__(self):
        self.project = None

    def __str__(self):
        return "LSP(%s)" % (self.project.name if self.project else "")

    def __repr__(self):
        return "LSP(%s)" % (self.project.name if self.project else "")

    # private
    def _set_project(self, path_or_uri):
        old_project = self.project
        project = Project.find(path_or_uri)
        if project is None:
            project = Project.find_project(uri_to_path(path_or_uri))
        if project is old_project:
            return 
        self.project = project
        log.info("set project old %s new %s", old_project, project)

    def _solveTextDocumentPostionParams(self, params):
        return self.project.get_name(params) if self.project else ""

    # General
    #========================================================
    def initialize(self, params):
        log.info("%s initialize %s", self, params)
        self._set_project(params.get("rootPath", ""))
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
        uri = uri_to_path(params["textDocument"]["uri"])
        self._set_project(uri)

    def textDocument_didChange(self, params):
        log.info("%s textDocument_didChange %s", self, params)
        if self.project:
            self.project.cache_file_content(params)

    def textDocument_willSave(self, params):
        pass

    def textDocument_willSaveWaitUntil(self, params):
        pass

    def textDocument_didSave(self, params):
        pass

    def textDocument_didClose(self, params):
        pass

    # Language Features
    #========================================================
    def textDocument_completion(self, params):
        log.info("%s textDocument_completion %s", self, params)
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
        self.project.reinit("")
        log.info("%s textDocument_completion %s", self, params)
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
        p = self.project
        if not p:
            return 
        p.init_or_load()
        symbol = self._solveTextDocumentPostionParams(params)
        log.info("%s textDocument_references %s", self, symbol)
        if not symbol:
            return 
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

    def textDocument_codeLens(self, params):
        pass

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
            'codeActionProvider': True,
            'codeLensProvider': {
                'resolveProvider': True,
            },
            'completionProvider': {
                'resolveProvider': True,
                'triggerCharacters': ['.']
            },
            'documentFormattingProvider': True,
            'documentHighlightProvider': True,
            'documentRangeFormattingProvider': True,
            'documentSymbolProvider': True,
            'definitionProvider': True,
            'executeCommandProvider': {
            },
            'hoverProvider': True,
            'referencesProvider': True,
            'renameProvider': True,
            'signatureHelpProvider': {
                'triggerCharacters': ['(', ',']
            },
            # 'textDocumentSync': lsp.TextDocumentSyncKind.INCREMENTAL,
            # 'experimental': merge(self._hook('pyls_experimental_capabilities'))
        }
        # log.info('Server capabilities: %s', server_capabilities)
        return server_capabilities

class LanguageServerProtocol(JsonRpcProtocol):

    Handler= LanguageServerProtocolHandler

