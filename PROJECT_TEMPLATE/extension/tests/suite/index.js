"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.run = run;
var Mocha = require("mocha");
var path = require("path");
function run() {
    var mocha = new Mocha({
        ui: 'tdd',
        color: true,
        timeout: 30000,
    });
    mocha.addFile(path.resolve(__dirname, './extension.test.js'));
    return new Promise(function (resolve, reject) {
        try {
            mocha.run(function (failures) {
                if (failures > 0) {
                    reject(new Error("".concat(failures, " tests failed.")));
                }
                else {
                    resolve();
                }
            });
        }
        catch (err) {
            reject(err);
        }
    });
}
// The @vscode/test-electron runner calls run() automatically.
// This is also kept for direct invocation.
run();
