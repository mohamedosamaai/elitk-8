import js from '@eslint/js';
import globals from 'globals';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  // Global ignores
  { ignores: ['dist/**/*', 'node_modules/**/*', 'public/**/*', 'eslint.config.js', 'showcase-shell/**/*', 'scripts/**/*', 'tools/**/*'] },

  // Base JS rules
  js.configs.recommended,

  // Type-aware rules — strict new code only (lib/, types/, ErrorBoundary)
  {
    files: ['src/lib/**/*.{ts,tsx}', 'src/types/**/*.ts', 'src/ErrorBoundary.tsx'],
    extends: [
      ...tseslint.configs.recommendedTypeChecked,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.json', './tsconfig.node.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      globals: { ...globals.browser },
    },
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/consistent-type-imports': ['error', { prefer: 'type-imports' }],
      '@typescript-eslint/no-floating-promises': 'error',
      'eqeqeq': ['error', 'always'],
      'prefer-const': 'error',
    },
  },

  // Relaxed rules — legacy app source (App.tsx, AudioEngine, Resonance3D, etc.)
  {
    files: ['src/**/*.{ts,tsx}'],
    ignores: ['src/lib/**/*', 'src/types/**/*', 'src/ErrorBoundary.tsx'],
    extends: [...tseslint.configs.recommended],
    languageOptions: {
      globals: { ...globals.browser },
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
      // TypeScript — enforce what tsconfig alone cannot
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/consistent-type-imports': ['error', { prefer: 'type-imports' }],
      '@typescript-eslint/no-floating-promises': 'off',
      '@typescript-eslint/no-misused-promises': 'off',
      '@typescript-eslint/prefer-nullish-coalescing': 'off',
      '@typescript-eslint/prefer-optional-chain': 'off',
      '@typescript-eslint/no-unsafe-member-access': 'off',
      '@typescript-eslint/no-unsafe-assignment': 'off',
      '@typescript-eslint/no-unsafe-argument': 'off',

      // General quality
      'no-useless-escape': 'off',
      'no-console': ['warn', { allow: ['warn', 'error', 'info'] }],
      'eqeqeq': ['error', 'always'],
      'no-var': 'error',
      'prefer-const': 'warn',
    },
  },

  // Non-type-checked — server.ts, tests, config files
  {
    files: ['server.ts', 'tests/**/*.ts', 'vitest.config.ts', 'eslint.config.js'],
    extends: [...tseslint.configs.recommended],
    languageOptions: {
      globals: { ...globals.node },
    },
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      'prefer-const': 'error',
      'eqeqeq': ['error', 'always'],
    },
  }
);
