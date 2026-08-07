import {StrictMode} from 'react';
import {createRoot} from 'react-dom/client';
import App from './App.tsx';
import './index.css';

// MediaPipe and TensorFlow Lite emit noisy internal lifecycle logs that surface in browser
// devtools and confuse debugging. Filtering here avoids patching third-party source.
const SUPPRESSED_LOG_PATTERNS = [
  'Created TensorFlow Lite XNNPACK delegate for CPU',
  'GL version:',
  'Graph successfully started running.',
  'Sets FaceBlendshapesGraph acceleration to xnnpack by default',
  'OpenGL error checking is disabled',
  'THREE.Clock',
  'INFO:',
  'W0501',
];

function suppressThirdPartyNoise() {
  const isNoise = (args: unknown[]) =>
    typeof args[0] === 'string' &&
    SUPPRESSED_LOG_PATTERNS.some(p => (args[0] as string).includes(p));

  const originalInfo = console.info;
  const originalLog = // eslint-disable-next-line no-console
  console.log;
  const originalWarn = console.warn;
  const originalError = console.error;
  // eslint-disable-next-line no-console
  const originalDebug = console.debug;

  console.info = (...args) => { if (!isNoise(args)) originalInfo.apply(console, args); };
  // eslint-disable-next-line no-console
console.log = (...args) => { if (!isNoise(args)) originalLog.apply(console, args); };
  console.warn = (...args) => { if (!isNoise(args)) originalWarn.apply(console, args); };
  console.error = (...args) => { if (!isNoise(args)) originalError.apply(console, args); };
  // eslint-disable-next-line no-console
  console.debug = (...args) => { if (!isNoise(args)) originalDebug.apply(console, args); };
}

import { ErrorBoundary } from './ErrorBoundary.tsx';

suppressThirdPartyNoise();

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => undefined);
  });
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
);
