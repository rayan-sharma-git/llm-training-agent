import * as path from 'path';
import { runTests } from '@vscode/test-electron';

async function main() {
  try {
    const extensionDevelopmentPath = path.resolve(__dirname, '../../');
    const extensionTestsPath = path.resolve(__dirname, '../out-test/suite/index.js');

    // Use the extension directory itself as the workspace
    const launchArgs = [extensionDevelopmentPath];

    await runTests({
      extensionDevelopmentPath,
      extensionTestsPath,
      launchArgs,
    });

    console.log('All tests passed!');
  } catch (err) {
    console.error('Test failed:', err);
    process.exit(1);
  }
}

main();