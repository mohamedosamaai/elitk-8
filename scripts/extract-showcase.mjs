import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.join(__dirname, '..');
const outDir = path.join(rootDir, 'showcase-shell');

console.log('🧹 Starting Showcase Extractor...');

// 1. Clean previous output
if (fs.existsSync(outDir)) {
  fs.rmSync(outDir, { recursive: true, force: true });
}
fs.mkdirSync(outDir, { recursive: true });

// 2. Define items to copy
const allowedItems = [
  'public',
  'src',
  'tests',
  'package.json',
  'package-lock.json',
  'tsconfig.json',
  'tsconfig.node.json',
  'vite.config.ts',
  'vitest.config.ts',
  'eslint.config.js',
  '.prettierrc',
  'server.ts',
  'index.html',
  'README.md'
];

// 3. Copy files safely
console.log('📂 Copying safe files...');
allowedItems.forEach((item) => {
  const srcPath = path.join(rootDir, item);
  const destPath = path.join(outDir, item);
  
  if (fs.existsSync(srcPath)) {
    fs.cpSync(srcPath, destPath, { recursive: true });
  }
});

// 4. Mock proprietary AI logic
console.log('🎭 Mocking proprietary AI logic...');
const aiClientPath = path.join(outDir, 'src', 'lib', 'ai', 'client.ts');
const mockAIClientContent = `
/**
 * PUBLIC SHOWCASE MOCK - Proprietary Gemini integration removed.
 * Returns dummy structured response for demo purposes.
 */
export interface GenerateTextOptions {
  prompt: string;
  systemPrompt?: string;
  maxTokens?: number;
  temperature?: number;
  signal?: AbortSignal;
}

export interface GenerateTextResult {
  text: string;
  inputTokens: number;
  outputTokens: number;
  finishReason: 'stop' | 'length' | 'error';
}

export interface AIClient {
  generateText(options: GenerateTextOptions): Promise<GenerateTextResult>;
}

export function createAIClient(): AIClient {
  return {
    async generateText({ prompt, signal }: GenerateTextOptions): Promise<GenerateTextResult> {
      console.log('[Showcase Mode] Mocking AI request for prompt:', prompt.substring(0, 30) + '...');
      
      // Simulate network latency
      await new Promise(resolve => {
        const timeout = setTimeout(resolve, 1200);
        if (signal) {
          signal.addEventListener('abort', () => {
            clearTimeout(timeout);
          });
        }
      });
      
      if (signal?.aborted) {
        throw new Error('AbortError');
      }

      return {
        text: 'This is a mocked showcase response. Proprietary AI models and internal prompts have been stripped from this version to protect IP.',
        inputTokens: 15,
        outputTokens: 25,
        finishReason: 'stop',
      };
    },
  };
}
`;

if (fs.existsSync(aiClientPath)) {
  fs.writeFileSync(aiClientPath, mockAIClientContent.trim(), 'utf8');
} else {
  console.warn('⚠️ Could not find src/lib/ai/client.ts to mock.');
}

// 5. Clean up scripts in package.json
console.log('📦 Scrubbing package.json scripts...');
const pkgPath = path.join(outDir, 'package.json');
if (fs.existsSync(pkgPath)) {
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
  // Remove the showcase script from the public shell so it doesn't loop
  delete pkg.scripts['extract:showcase'];
  fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2), 'utf8');
}

console.log('✅ Showcase Shell successfully generated in ./showcase-shell');
