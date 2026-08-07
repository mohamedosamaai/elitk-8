import express from 'express';
import { createServer as createViteServer } from 'vite';
import path from 'path';
import { z } from 'zod';
import pino from 'pino';
import rateLimit from 'express-rate-limit';
import cors from 'cors';

const CANONICAL_URL = process.env.APP_URL || 'https://8.elitk.com';
const CANONICAL_HOST = new URL(CANONICAL_URL).host;
const IS_PROD = process.env.NODE_ENV === 'production';

// Production structured logging using Pino
const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: IS_PROD
    ? undefined
    : { target: 'pino-pretty', options: { colorize: true } },
});

// Custom structured error classes
export class AppError extends Error {
  constructor(
    public override message: string,
    public statusCode: number,
    public code?: string
  ) {
    super(message);
    this.name = this.constructor.name;
    Error.captureStackTrace(this, this.constructor);
  }
}

export class ValidationError extends AppError {
  constructor(message: string, public details?: unknown) {
    super(message, 400, 'VALIDATION_ERROR');
  }
}

export class UpstreamError extends AppError {
  constructor(message: string, statusCode = 502) {
    super(message, statusCode, 'UPSTREAM_ERROR');
  }
}

// AbortController timeout helper — prevents fetch from hanging indefinitely
function fetchWithTimeout(
  url: string,
  init: RequestInit,
  timeoutMs: number
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  return fetch(url, { ...init, signal: controller.signal }).finally(() =>
    clearTimeout(timer)
  );
}

// Builds a Google TTS API URL without leaking the key in query params.
// Uses the Authorization header pattern instead of ?key= which appears in logs.
function buildTtsHeaders(apiKey: string): HeadersInit {
  return {
    'Content-Type': 'application/json',
    'X-Goog-Api-Key': apiKey,
  };
}

// Input schema for /api/tts — validates before passing to Google TTS API
const ttsRequestSchema = z.object({
  text: z.string().min(1).max(5000),
  voice: z
    .object({
      languageCode: z.string(),
      name: z.string(),
    })
    .optional(),
});

async function startServer() {
  const app = express();
  const PORT = Number(process.env.PORT || 3000);

  // Trust exactly one hop (the immediate reverse proxy) — prevents IP spoofing via X-Forwarded-For
  app.set('trust proxy', 1);
  app.use(express.json({ limit: '16kb' }));

  // CORS — restrict to same origin and known production domain in prod
  const allowedOrigins = IS_PROD
    ? [CANONICAL_URL, `https://${CANONICAL_HOST}`]
    : ['http://localhost:5173', 'http://localhost:3000'];

  app.use(
    cors({
      origin: (origin, cb) => {
        // Allow server-to-server calls (no origin) and listed origins
        if (!origin || allowedOrigins.includes(origin)) {
          cb(null, true);
        } else {
          cb(new AppError(`CORS: origin '${origin}' not allowed`, 403, 'CORS_ERROR'));
        }
      },
      methods: ['GET', 'POST'],
      allowedHeaders: ['Content-Type'],
    })
  );

  // Global rate limiter for API endpoints — prevents DoS and brute force attacks
  const apiLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 100,
    standardHeaders: true,
    legacyHeaders: false,
    message: { error: 'Too many requests from this IP, please try again later.' },
  });

  // Strict rate limiter for TTS — protects Google Cloud billing quotas
  const ttsLimiter = rateLimit({
    windowMs: 60 * 1000,
    max: 20,
    standardHeaders: true,
    legacyHeaders: false,
    message: { error: 'Rate limit exceeded for TTS generation. Please wait a minute.' },
  });

  app.use('/api/', apiLimiter);
  app.use('/api/tts', ttsLimiter);

  // Health endpoint — omit credential hints to avoid information disclosure
  app.get('/api/health', (_req, res) => {
    res.json({ status: 'ok', env: IS_PROD ? 'production' : 'development' });
  });

  app.get('/api/voices', async (_req, res, next) => {
    try {
      const apiKey = process.env.GOOGLE_TTS_API_KEY;
      if (!apiKey) {
        throw new AppError('GOOGLE_TTS_API_KEY not configured', 500, 'CONFIG_ERROR');
      }
      const response = await fetchWithTimeout(
        'https://texttospeech.googleapis.com/v1/voices',
        { headers: buildTtsHeaders(apiKey) },
        8000
      );
      if (!response.ok) {
        throw new UpstreamError('Failed to fetch voices from Google API', response.status);
      }
      res.json(await response.json());
    } catch (e) {
      next(e);
    }
  });

  // TTS proxy — GOOGLE_TTS_API_KEY is never exposed to the client bundle
  app.post('/api/tts', async (req, res, next) => {
    try {
      const parsed = ttsRequestSchema.safeParse(req.body);
      if (!parsed.success) {
        throw new ValidationError('Invalid request payload', parsed.error.flatten());
      }

      const { text, voice } = parsed.data;
      const apiKey = process.env.GOOGLE_TTS_API_KEY;

      if (!apiKey) {
        throw new AppError('GOOGLE_TTS_API_KEY not configured on server', 500, 'CONFIG_ERROR');
      }

      const isArabic = /[\u0600-\u06FF]/.test(text);

      const response = await fetchWithTimeout(
        'https://texttospeech.googleapis.com/v1/text:synthesize',
        {
          method: 'POST',
          headers: buildTtsHeaders(apiKey),
          body: JSON.stringify({
            input: { text },
            voice: voice ?? {
              languageCode: isArabic ? 'ar-XA' : 'en-US',
              name: isArabic ? 'ar-XA-Chirp3-HD-Zephyr' : 'en-US-Chirp3-HD-Aoede',
            },
            audioConfig: {
              audioEncoding: 'MP3',
              speakingRate: isArabic ? 1.0 : 0.95,
            },
          }),
        },
        10000
      );

      if (!response.ok) {
        const error = await response
          .json()
          .catch(() => ({ message: 'Unknown upstream error' }));
        throw new UpstreamError(
          (error as { message?: string }).message || 'TTS synthesis request failed',
          response.status
        );
      }

      res.json(await response.json());
    } catch (err) {
      next(err);
    }
  });

  if (!IS_PROD) {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (_req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  // Global error handler
  app.use(
    (
      err: unknown,
      _req: express.Request,
      res: express.Response,
      _next: express.NextFunction
    ) => {
      const appErr = err instanceof AppError ? err : null;
      const statusCode = appErr?.statusCode ?? 500;
      const errorCode = appErr?.code ?? 'INTERNAL_SERVER_ERROR';
      const message =
        err instanceof Error ? err.message : 'Internal server error';
      const stack = err instanceof Error ? err.stack : undefined;

      logger.error({ err: { message, stack, code: errorCode } }, 'Request error');

      res.status(statusCode).json({
        error: {
          message,
          code: errorCode,
          ...(!IS_PROD && { stack }),
        },
      });
    }
  );

  const server = app.listen(PORT, '0.0.0.0', () => {
    logger.info({ port: PORT, appUrl: CANONICAL_URL }, 'Server listening');
  });

  // Graceful shutdown — allows Docker/K8s to drain connections cleanly
  const shutdown = (signal: string) => {
    logger.info({ signal }, 'Shutdown signal received');
    server.close(() => {
      logger.info('All connections closed. Process exiting.');
      process.exit(0);
    });
    setTimeout(() => {
      logger.error('Shutdown timeout exceeded — forcing exit');
      process.exit(1);
    }, 10_000);
  };

  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT', () => shutdown('SIGINT'));
}

startServer().catch((err) => {
  console.error('Fatal: server failed to start', err);
  process.exit(1);
});