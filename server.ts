import express from "express";
import { createServer as createViteServer } from "vite";
import path from "path";

const CANONICAL_URL = process.env.APP_URL || "https://8.elitk.com";
const CANONICAL_HOST = new URL(CANONICAL_URL).host;

async function startServer() {
  const app = express();
  const PORT = Number(process.env.PORT || 3000);

  app.set("trust proxy", true);
  app.use(express.json());

  // API Route for Diagnostics
  app.get("/api/health", (req, res) => {
    const apiKey = process.env.GEMINI_API_KEY;
    res.json({
      status: "ok",
      canonicalUrl: CANONICAL_URL,
      canonicalHost: CANONICAL_HOST,
      requestHost: req.get("host") || null,
      hasKey: !!apiKey,
      isPlaceholder: apiKey === "your-gemini-api-key-here"
    });
  });

  app.get("/api/voices", async (_req, res) => {
    try {
      const apiKey = process.env.GOOGLE_TTS_API_KEY;
      if (!apiKey) return res.status(500).json({ error: "Missing API Key" });
      const response = await fetch(`https://texttospeech.googleapis.com/v1/voices?key=${apiKey}`);
      const data = await response.json();
      res.json(data);
    } catch (e) {
      res.status(500).json({ error: String(e) });
    }
  });

  // API Proxy for Google TTS
  app.post("/api/tts", async (req, res) => {
    try {
      let { text } = req.body;
      const { voice } = req.body;
      const apiKey = process.env.GOOGLE_TTS_API_KEY;

      if (!apiKey) {
        return res.status(500).json({ error: "GOOGLE_TTS_API_KEY not configured on server" });
      }

      const isArabic = /[\u0600-\u06FF]/.test(text || "");

      const response = await fetch(`https://texttospeech.googleapis.com/v1/text:synthesize?key=${apiKey}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          input: { text },
          voice: voice || {
            languageCode: isArabic ? "ar-XA" : "en-US",
            name: isArabic ? "ar-XA-Chirp3-HD-Zephyr" : "en-US-Chirp3-HD-Aoede"
          },
          audioConfig: {
            audioEncoding: "MP3",
            speakingRate: isArabic ? 1.0 : 0.95
          }
        })
      });

      if (!response.ok) {
        const error = await response.json();
        return res.status(response.status).json(error);
      }

      const data = await response.json();
      res.json(data);
    } catch (err) {
      console.error("TTS Proxy Error:", err);
      res.status(500).json({ error: "Internal Server Error" });
    }
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (_req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
    console.log(`Canonical URL: ${CANONICAL_URL}`);
  });
}

startServer();