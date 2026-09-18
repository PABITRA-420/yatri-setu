'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallbackTitle?: string;
  fallbackMessage?: string;
  fallbackComponent?: ReactNode;
  onReset?: () => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('[Yatri Setu ErrorBoundary caught]:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallbackComponent) {
        return this.props.fallbackComponent;
      }

      return (
        <div className="w-full p-6 rounded-2xl bg-stone-900/90 border border-stone-800 text-stone-200 flex flex-col items-center justify-center text-center gap-3">
          <AlertTriangle className="w-8 h-8 text-amber-500" />
          <h4 className="font-extrabold text-sm text-white">
            {this.props.fallbackTitle || 'Component Temporarily Unavailable'}
          </h4>
          <p className="text-xs text-stone-400 max-w-md">
            {this.props.fallbackMessage || 'An unexpected rendering error occurred. The remainder of the advisory remains functional.'}
          </p>
          <button
            type="button"
            onClick={this.handleReset}
            className="mt-2 px-3 py-1.5 rounded-xl bg-stone-800 hover:bg-stone-700 text-white text-xs font-bold transition flex items-center gap-1.5 cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Try Again</span>
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
