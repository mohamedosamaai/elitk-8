import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['tests/**/*.test.ts', 'src/**/*.test.ts'],
    exclude: ['tests/tts-legacy.test.cjs', 'node_modules/**'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov', 'html'],
      include: ['src/**/*.ts', 'server.ts'],
      exclude: [
        'src/main.tsx',
        'src/**/*.d.ts',
        'node_modules/**',
        'dist/**',
      ],
      thresholds: {
        lines: 30,
        functions: 30,
        branches: 30,
      },
    },
    reporters: ['default'],
    testTimeout: 10_000,
  },
});
