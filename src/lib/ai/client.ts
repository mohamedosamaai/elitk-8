/**
 * AI client abstraction layer.
 *
 * All AI interactions in this codebase go through this interface.
 * The underlying provider is configured here via environment variables
 * without touching any call site.
 */

export interface GenerateTextOptions {
  prompt: string;
  systemPrompt?: string;
  /** Max output tokens. Defaults to 2048. */
  maxTokens?: number;
  /** Temperature 0–1. Defaults to 0.7. */
  temperature?: number;
  /** AbortSignal for cancellation. */
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

/**
 * Creates a Gemini-backed AI client.
 *
 * @throws {Error} if GEMINI_API_KEY is absent — fail fast at startup.
 *
 * Usage (server-side only):
 * ```ts
 * import { createAIClient } from '@/src/lib/ai/client';
 * const ai = createAIClient();
 * const { text } = await ai.generateText({ prompt: 'Hello' });
 * ```
 */
export function createAIClient(): AIClient {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error(
      'GEMINI_API_KEY is not set. Configure it in .env.local and restart the server.'
    );
  }

  const MODEL = process.env.GEMINI_MODEL ?? 'gemini-2.0-flash';

  return {
    async generateText({
      prompt,
      systemPrompt,
      maxTokens = 2048,
      temperature = 0.7,
      signal,
    }: GenerateTextOptions): Promise<GenerateTextResult> {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`;

      const body = {
        system_instruction: systemPrompt
          ? { parts: [{ text: systemPrompt }] }
          : undefined,
        contents: [{ role: 'user', parts: [{ text: prompt }] }],
        generationConfig: {
          maxOutputTokens: maxTokens,
          temperature,
        },
      };

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Goog-Api-Key': apiKey,
        },
        body: JSON.stringify(body),
        signal,
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({})) as { error?: { message?: string } };
        throw new Error(
          `Gemini API error ${response.status}: ${err?.error?.message ?? 'Unknown error'}`
        );
      }

      const data = await response.json() as {
        candidates?: Array<{
          content?: { parts?: Array<{ text?: string }> };
          finishReason?: string;
        }>;
        usageMetadata?: { promptTokenCount?: number; candidatesTokenCount?: number };
      };

      const text =
        data.candidates?.[0]?.content?.parts?.map((p) => p.text ?? '').join('') ?? '';
      const finishReason =
        (data.candidates?.[0]?.finishReason?.toLowerCase() as GenerateTextResult['finishReason']) ??
        'stop';

      return {
        text,
        inputTokens: data.usageMetadata?.promptTokenCount ?? 0,
        outputTokens: data.usageMetadata?.candidatesTokenCount ?? 0,
        finishReason,
      };
    },
  };
}
