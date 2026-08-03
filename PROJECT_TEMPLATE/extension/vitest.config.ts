import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['tests/suite/**/*.test.ts'],
    exclude: ['tests/suite/extension.test.ts', 'tests/suite/treeView.test.ts'],
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    },
  },
});