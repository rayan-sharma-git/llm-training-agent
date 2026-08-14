const Mocha = require('mocha');
import * as path from 'path';

export function run(): Promise<void> {
  const mocha = new Mocha({
    ui: 'tdd',
    color: true,
    timeout: 30000,
  });

  mocha.addFile(path.resolve(__dirname, './extension.test.js'));

  return new Promise((resolve, reject) => {
    try {
      mocha.run((failures: number) => {
        if (failures > 0) {
          reject(new Error(failures + ' tests failed.'));
        } else {
          resolve();
        }
      });
    } catch (err) {
      reject(err);
    }
  });
}