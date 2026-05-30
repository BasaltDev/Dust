// Copyright (C) 2026 BasaltDev
// SPDX-License-Identifier: GPL-3.0-only


import * as path from 'path';
import { ExtensionContext, workspace } from 'vscode';  
import { LanguageClient, LanguageClientOptions, ServerOptions } from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: ExtensionContext) {
    const serverPath = context.asAbsolutePath(path.join('server', 'server.py'));

    const serverOptions: ServerOptions = {
        command: process.platform === 'win32' ? 'python' : 'python3',
        args: [serverPath]
    };

    const clientOptions: LanguageClientOptions = {
        documentSelector: [{ scheme: 'file', language: 'dust' }],
        synchronize: {
            fileEvents: workspace.createFileSystemWatcher('**/.clientrc')
        },
        outputChannelName: 'Dust Server',
    };

    client = new LanguageClient('dustLanguageServer', 'Dust Server', serverOptions, clientOptions);
    client.start();
}

export function deactivate(): Thenable<void> | undefined {
    return client ? client.stop() : undefined;
}