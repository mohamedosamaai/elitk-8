# syntax=docker/dockerfile:1.7
# ─── Stage 1: Builder ─────────────────────────────────────────────────────────
FROM node:22-alpine AS builder

LABEL stage="builder"

WORKDIR /app

# Install deps before copying source — layer is cached unless package files change
COPY package*.json ./
RUN npm ci --ignore-scripts

COPY . .

# Build args are substituted at image build time only; never persisted in the image
ARG GEMINI_API_KEY=""
ARG GOOGLE_TTS_API_KEY=""
ARG CHAT_LOGGER_URL=""
ARG LOGGER_API_KEY=""

ENV GEMINI_API_KEY=$GEMINI_API_KEY \
    GOOGLE_TTS_API_KEY=$GOOGLE_TTS_API_KEY \
    CHAT_LOGGER_URL=$CHAT_LOGGER_URL \
    LOGGER_API_KEY=$LOGGER_API_KEY

RUN npm run build

# ─── Stage 2: Runner ──────────────────────────────────────────────────────────
FROM node:22-alpine AS runner

LABEL org.opencontainers.image.title="Resonance 8" \
      org.opencontainers.image.description="Real-time 3D particle experience — Gemini AI, MediaPipe, Web Audio" \
      org.opencontainers.image.source="https://github.com/mohamedosamaai/elitk-8" \
      org.opencontainers.image.licenses="MIT"

WORKDIR /app

ENV NODE_ENV=production \
    PORT=8080

# Production deps only — separate copy avoids rebuilding devDeps layer on source changes
COPY package*.json ./
RUN npm ci --omit=dev --ignore-scripts

# Copy compiled output from builder
COPY --from=builder /app/dist ./dist

# Run as non-root for reduced attack surface
USER node

EXPOSE 8080

# SIGTERM handling — node exits cleanly on SIGTERM sent by Docker / orchestrators
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:8080/api/health || exit 1

CMD ["node", "dist/server.cjs"]
