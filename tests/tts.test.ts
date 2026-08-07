import { describe, it, expect, beforeEach } from 'vitest';
import { z } from 'zod';

// ─── Zod Schema Validation (mirrors server.ts ttsRequestSchema) ──────────────

const ttsRequestSchema = z.object({
  text: z.string().min(1).max(5000),
  voice: z
    .object({
      languageCode: z.string(),
      name: z.string(),
    })
    .optional(),
});

describe('TTS request schema validation', () => {
  it('accepts a valid text-only payload', () => {
    const result = ttsRequestSchema.safeParse({ text: 'Hello world' });
    expect(result.success).toBe(true);
  });

  it('accepts a payload with a valid voice override', () => {
    const result = ttsRequestSchema.safeParse({
      text: 'مرحبا',
      voice: { languageCode: 'ar-XA', name: 'ar-XA-Chirp3-HD-Zephyr' },
    });
    expect(result.success).toBe(true);
  });

  it('rejects an empty text string', () => {
    const result = ttsRequestSchema.safeParse({ text: '' });
    expect(result.success).toBe(false);
  });

  it('rejects text exceeding 5000 characters', () => {
    const result = ttsRequestSchema.safeParse({ text: 'a'.repeat(5001) });
    expect(result.success).toBe(false);
  });

  it('rejects a missing text field', () => {
    const result = ttsRequestSchema.safeParse({});
    expect(result.success).toBe(false);
  });

  it('rejects a voice object with missing fields', () => {
    const result = ttsRequestSchema.safeParse({
      text: 'Hello',
      voice: { languageCode: 'en-US' },
    });
    expect(result.success).toBe(false);
  });

  it('accepts exactly 5000 characters', () => {
    const result = ttsRequestSchema.safeParse({ text: 'x'.repeat(5000) });
    expect(result.success).toBe(true);
  });
});

// ─── Arabic Detection Logic ───────────────────────────────────────────────────

const isArabicText = (text: string) => /[\u0600-\u06FF]/.test(text);

describe('Arabic text detection', () => {
  it('detects Arabic text correctly', () => {
    expect(isArabicText('مرحبا بالعالم')).toBe(true);
  });

  it('returns false for plain English text', () => {
    expect(isArabicText('Hello world')).toBe(false);
  });

  it('returns true for mixed Arabic-English', () => {
    expect(isArabicText('Hello مرحبا')).toBe(true);
  });

  it('returns false for empty string', () => {
    expect(isArabicText('')).toBe(false);
  });

  it('returns false for numbers and symbols', () => {
    expect(isArabicText('12345 !@#$%')).toBe(false);
  });
});

// ─── AppError Class ───────────────────────────────────────────────────────────

class AppError extends Error {
  constructor(
    public override message: string,
    public statusCode: number,
    public code?: string
  ) {
    super(message);
    this.name = this.constructor.name;
  }
}

class ValidationError extends AppError {
  constructor(message: string, public details?: unknown) {
    super(message, 400, 'VALIDATION_ERROR');
  }
}

class UpstreamError extends AppError {
  constructor(message: string, statusCode = 502) {
    super(message, statusCode, 'UPSTREAM_ERROR');
  }
}

describe('AppError hierarchy', () => {
  it('AppError sets statusCode and code correctly', () => {
    const err = new AppError('Something went wrong', 500, 'INTERNAL');
    expect(err.message).toBe('Something went wrong');
    expect(err.statusCode).toBe(500);
    expect(err.code).toBe('INTERNAL');
    expect(err instanceof Error).toBe(true);
  });

  it('ValidationError defaults to 400 and VALIDATION_ERROR code', () => {
    const err = new ValidationError('Bad input', { field: 'text' });
    expect(err.statusCode).toBe(400);
    expect(err.code).toBe('VALIDATION_ERROR');
    expect(err.details).toEqual({ field: 'text' });
  });

  it('UpstreamError defaults to 502', () => {
    const err = new UpstreamError('Google TTS unreachable');
    expect(err.statusCode).toBe(502);
    expect(err.code).toBe('UPSTREAM_ERROR');
  });

  it('UpstreamError accepts a custom status code', () => {
    const err = new UpstreamError('Unauthorized', 401);
    expect(err.statusCode).toBe(401);
  });
});
