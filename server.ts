import express from "express";
import { createServer as createViteServer } from "vite";
import path from "path";
import { z } from "zod";
import pino from "pino";
import rateLimit from "express-rate-limit";

const CANONICAL_URL = process.env.APP_URL || "https://8.elitk.com";
const CANONICAL_HOST = new URL(CANONICAL_URL).host;

// Production structured logging using Pino
const logger = pino({
  level: process.env.LOG_LEVEL || "info",
  transport:
    process.env.NODE_ENV !== "production"
      ? {
          target: "pino-pretty",
          options: { colorize: true },
        }
      : undefined,
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
  constructor(message: string, public details?: any) {
    super(message, 400, "VALIDATION_ERROR");
  }
}

export class UpstreamError extends AppError {
  constructor(message: string, statusCode: number = 502) {
    super(message, statusCode, "UPSTREAM_ERROR");
  }
}

// AbortController timeout helper — prevents fetch from hanging indefinitely
function fetchWithTimeout(url: string, init: RequestInit, timeoutMs: number): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  return fetch(url, { ...init, signal: controller.signal }).finally(() => clearTimeout(timer));
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

  app.set("trust proxy", true);
  app.use(express.json({ limit: "16kb" }));

  // Global rate limiter for API endpoints — prevents DoS and brute force attacks
  const apiLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per window
    standardHeaders: true,
    legacyHeaders: false,
    message: { error: "Too many requests from this IP, please try again later." },
  });

  // Strict rate limiter for the TTS generation API — protects Google Cloud billing quotas
  const ttsLimiter = rateLimit({
    windowMs: 60 * 1000, // 1 minute
    max: 20, // Limit each IP to 20 TTS requests per minute
    standardHeaders: true,
    legacyHeaders: false,
    message: { error: "Rate limit exceeded for TTS generation. Please try again in a minute." },
  });

  app.use("/api/", apiLimiter);
  app.use("/api/tts", ttsLimiter);

  app.get("/api/health", (_req, res) => {
    const apiKey = process.env.GEMINI_API_KEY;
    res.json({
      status: "ok",
      canonicalUrl: CANONICAL_URL,
      canonicalHost: CANONICAL_HOST,
      hasKey: !!apiKey,
    });
  });

  app.get("/api/voices", async (_req, res, next) => {
    try {
      const apiKey = process.env.GOOGLE_TTS_API_KEY;
      if (!apiKey) {
        throw new AppError("GOOGLE_TTS_API_KEY not configured", 500, "CONFIG_ERROR");
      }
      const response = await fetchWithTimeout(
        `https://texttospeech.googleapis.com/v1/voices?key=${apiKey}`,
        {},
        8000
      );
      if (!response.ok) {
        throw new UpstreamError("Failed to fetch voices from Google API", response.status);
      }
      const data = await response.json();
      res.json(data);
    } catch (e) {
      next(e);
    }
  });

  // TTS proxy — keeps GOOGLE_TTS_API_KEY server-side, never exposed to the client bundle
  app.post("/api/tts", async (req, res, next) => {
    try {
      const parsed = ttsRequestSchema.safeParse(req.body);
      if (!parsed.success) {
        throw new ValidationError("Invalid request schema payload", parsed.error.flatten());
      }

      const { text, voice } = parsed.data;
      const apiKey = process.env.GOOGLE_TTS_API_KEY;

      if (!apiKey) {
        throw new AppError("GOOGLE_TTS_API_KEY not configured on server", 500, "CONFIG_ERROR");
      }

      const isArabic = /[\u0600-\u06FF]/.test(text);

      const response = await fetchWithTimeout(
        `https://texttospeech.googleapis.com/v1/text:synthesize?key=${apiKey}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            input: { text },
            voice: voice ?? {
              languageCode: isArabic ? "ar-XA" : "en-US",
              name: isArabic ? "ar-XA-Chirp3-HD-Zephyr" : "en-US-Chirp3-HD-Aoede",
            },
            audioConfig: {
              audioEncoding: "MP3",
              speakingRate: isArabic ? 1.0 : 0.95,
            },
          }),
        },
        10000
      );

      if (!response.ok) {
        const error = await response.json().catch(() => ({ message: "Unknown upstream error" }));
        throw new UpstreamError(error.message || "TTS synthesis upstream request failed", response.status);
      }

      const data = await response.json();
      res.json(data);
    } catch (err) {
      next(err);
    }
  });

  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (_req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  // Global Error Handler Middleware
  app.use((err: any, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
    const statusCode = err instanceof AppError ? err.statusCode : 500;
    const errorCode = err instanceof AppError ? err.code : "INTERNAL_SERVER_ERROR";

    logger.error(
      {
        err: {
          message: err.message,
          stack: err.stack,
          code: errorCode,
        },
      },
      "Express request processing error"
    );

    res.status(statusCode).json({
      error: {
        message: err.message || "Internal server error",
        code: errorCode,
        ...(process.env.NODE_ENV !== "production" && { details: err.stack || err }),
      },
    });
  });

  app.listen(PORT, "0.0.0.0", () => {
    logger.info({ port: PORT, appUrl: CANONICAL_URL }, "Server listening on interface 0.0.0.0");
  });
}

startServer();