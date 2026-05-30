"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const path = __importStar(require("path"));
const vscode_1 = require("vscode");
const node_1 = require("vscode-languageclient/node");
let client;
function activate(context) {
    // 1. point to where your build.bat copies your python server
    const serverPath = context.asAbsolutePath(path.join('server', 'server.py'));
    // 2. set up the command to spawn the python process
    // windows uses 'python', mac/linux uses 'python3'
    const serverOptions = {
        command: process.platform === 'win32' ? 'python' : 'python3',
        args: [serverPath]
    };
    // 3. tell vscode to only trigger this server for '.ds' files
    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'dust' }],
        synchronize: {
            fileEvents: vscode_1.workspace.createFileSystemWatcher('**/.clientrc')
        },
        outputChannelName: 'Dust Server',
    };
    // 4. create and start the client pipeline
    client = new node_1.LanguageClient('dustLanguageServer', 'Dust Server', serverOptions, clientOptions);
    client.start();
}
function deactivate() {
    return client ? client.stop() : undefined;
}
//# sourceMappingURL=extension.js.map