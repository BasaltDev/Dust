# Copyright (C) 2026 BasaltDev
# SPDX-License-Identifier: GPL-3.0-only


from lsprotocol.types import (
    TEXT_DOCUMENT_DID_CHANGE,
    DidChangeTextDocumentParams,
    LogMessageParams,
    MessageType,
)
from pygls.lsp.server import LanguageServer

server = LanguageServer("dust-lsp", "1.0.0")


@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: LanguageServer, params: DidChangeTextDocumentParams):
    doc = ls.workspace.get_text_document(params.text_document.uri)
    code = doc.source
    ls.window_log_message(
        LogMessageParams(type=MessageType.Info, message=f"Current code: {code}")
    )


if __name__ == "__main__":
    server.start_io()
