/**
 * AI Client abstraction layer.
 *
 * Wraps the Google Gemini API behind a typed interface so that
 * the rest of the codebase never imports the SDK directly.
 * Swap the underlying provider here without touching call sites.
 */

export interface GenerateTextOptions {
  prompt: string;
  /** Max output tokens. Defaults to 2048. */
  maxTokens?: number;
  /** Temperature 0–1. Defaults to 0.7. */
  temperature?: number;
}

export interface GenerateTextResult {
  text: string;
  /** Estimated input tokens consumed. */
  inputTokens: number;
  /** Estimated output tokens consumed. */
  outputTokens: number;
}

export interface AIClient {
  generateText(options: GenerateTextOptions): Promise<GenerateTextResult>;
}

/**
 * Returns a live Gemini client.
 * Requires GEMINI_API_KEY to be present in the runtime environment.
 */
export function createAIClient(): AIClient {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error(
      'GEMINI_API_KEY is not configured. Set it in .env.local and restart the server.'
    );
  }

  return {
    async generateText({ prompt, maxTokens = 2048, temperature = 0.7 }) {
      // Replace this block with the real SDK call (e.g., @google/generative-ai).
      throw new Error('AI client not yet initialized — wire up the SDK here.');
    },
  };
}
