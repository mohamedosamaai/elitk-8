import type { ErrorInfo, ReactNode } from 'react';
import { Component } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public override state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public override componentDidCatch(error: Error, _errorInfo: ErrorInfo) {
    console.warn('[ErrorBoundary] Uncaught component exception:', error.message);
  }

  public override render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div className="flex flex-col items-center justify-center p-8 text-center bg-black/80 backdrop-blur-3xl border border-red-500/20 rounded-2xl max-w-md mx-auto my-12 shadow-2xl">
          <div className="text-red-500 font-mono text-sm tracking-widest mb-4">
            [NEURAL LINK FAULT]
          </div>
          <p className="text-white/60 font-sans text-xs max-w-sm mb-6 leading-relaxed">
            The 3D WebGL context or system layout encountered an unexpected anomaly. 
            This is usually caused by temporary WebGL context loss or lack of hardware acceleration.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2.5 bg-white/5 border border-white/10 hover:bg-white/10 rounded-xl text-xs font-mono text-white transition-all cursor-pointer"
          >
            RE-INITIALIZE LINK
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
