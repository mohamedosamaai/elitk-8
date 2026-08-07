# syntax=docker/dockerfile:1.7
# ─── Stage 1: Builder ─────────────────────────────────────────────────────────
FROM node:22-alpine AS builder

LABEL stage="builder"

WORKDIR /app

# Install deps before copying source — layer is cached unless package files change
COPY package*.json ./
RUN npm ci --ignore-scripts

COPY . .

# Build the Vite frontend + Express server bundle.
# No secrets are injected at build time — all API keys are passed as runtime
# environment variables via docker-compose or the orchestrator's secret manager.
RUN npm run build

# ─── Stage 2: Runner ──────────────────────────────────────────────────────────
FROM node:22-alpine AS runner

LABEL org.opencontainers.image.title="ELITK-8" \
      org.opencontainers.image.description="AI-native business orchestration platform — Gemini, MediaPipe, Web Audio" \
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

# Health check — lightweight wget call against the /api/health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:8080/api/health || exit 1

CMD ["node", "dist/server.cjs"]
