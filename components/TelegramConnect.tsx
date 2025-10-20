'use client';

import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card } from './ui/card';
import { Radio, X, Copy, ExternalLink, CheckCircle2, Loader2 } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface TelegramStatus {
  connected: boolean;
  chat_id?: string;
  username?: string;
  connected_at?: string;
}

interface ConnectionCode {
  connection_code: string;
  expires_at: string;
  message: string;
}

export const TelegramConnect: React.FC = () => {
  const [status, setStatus] = useState<TelegramStatus>({ connected: false });
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [connectionCode, setConnectionCode] = useState<ConnectionCode | null>(null);
  const [timeRemaining, setTimeRemaining] = useState<number>(0);

  // Fetch Telegram status on mount
  useEffect(() => {
    fetchStatus();
  }, []);

  // Countdown timer for connection code
  useEffect(() => {
    if (!connectionCode) return;

    const interval = setInterval(() => {
      const expiresAt = new Date(connectionCode.expires_at).getTime();
      const now = Date.now();
      const remaining = Math.max(0, Math.floor((expiresAt - now) / 1000));

      setTimeRemaining(remaining);

      if (remaining === 0) {
        clearInterval(interval);
        toast.error('Connection code expired. Please generate a new one.');
        setShowModal(false);
        setConnectionCode(null);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [connectionCode]);

  // Poll for connection status when modal is open
  useEffect(() => {
    if (!showModal || status.connected) return;

    const interval = setInterval(() => {
      fetchStatus(true);
    }, 3000); // Poll every 3 seconds

    return () => clearInterval(interval);
  }, [showModal, status.connected]);

  const fetchStatus = async (silent = false) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/telegram/status`);
      if (!response.ok) throw new Error('Failed to fetch status');

      const data: TelegramStatus = await response.json();
      setStatus(data);

      // If connected while modal is open, show success and close
      if (data.connected && showModal) {
        toast.success(`✅ Connected to Telegram as @${data.username || 'user'}!`);
        setShowModal(false);
        setConnectionCode(null);
      }
    } catch (error) {
      if (!silent) {
        console.error('Error fetching Telegram status:', error);
      }
    }
  };

  const handleConnect = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/telegram/generate-code`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error('Failed to generate connection code');

      const data: ConnectionCode = await response.json();
      setConnectionCode(data);
      setShowModal(true);

      const expiresAt = new Date(data.expires_at).getTime();
      const now = Date.now();
      setTimeRemaining(Math.floor((expiresAt - now) / 1000));
    } catch (error) {
      console.error('Error generating connection code:', error);
      toast.error('Failed to generate connection code');
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    if (!window.confirm('Are you sure you want to disconnect Telegram notifications?')) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/telegram/disconnect`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error('Failed to disconnect');

      toast.success('Disconnected from Telegram');
      setStatus({ connected: false });
    } catch (error) {
      console.error('Error disconnecting:', error);
      toast.error('Failed to disconnect');
    } finally {
      setLoading(false);
    }
  };

  const copyCode = () => {
    if (connectionCode) {
      navigator.clipboard.writeText(connectionCode.connection_code);
      toast.success('Code copied to clipboard!');
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <>
      {status.connected ? (
        <Button
          variant="outline"
          size="sm"
          onClick={handleDisconnect}
          disabled={loading}
          className="h-8"
          title={`Connected as @${status.username || 'user'}`}
        >
          <Radio className="mr-2 h-4 w-4 text-green-500" />
          <span className="hidden sm:inline">Telegram</span>
          <Badge variant="secondary" className="ml-2 bg-green-600/10 text-green-600 dark:bg-green-600/20 dark:text-green-400">
            Connected
          </Badge>
        </Button>
      ) : (
        <Button
          variant="outline"
          size="sm"
          onClick={handleConnect}
          disabled={loading}
          className="h-8"
        >
          {loading ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Radio className="mr-2 h-4 w-4" />
          )}
          <span className="hidden sm:inline">Connect Telegram</span>
          <span className="inline sm:hidden">Telegram</span>
        </Button>
      )}

      {/* Connection Modal */}
      {showModal && connectionCode && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <Card className="relative w-full max-w-md p-6 m-4">
            {/* Close Button */}
            <button
              onClick={() => {
                setShowModal(false);
                setConnectionCode(null);
              }}
              className="absolute top-4 right-4 text-muted-foreground hover:text-foreground"
            >
              <X className="h-5 w-5" />
            </button>

            {/* Header */}
            <div className="mb-6">
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <Radio className="h-6 w-6 text-blue-500" />
                Connect Telegram
              </h2>
              <p className="text-muted-foreground mt-2">
                Get real-time notifications for your bot activities
              </p>
            </div>

            {/* Connection Code */}
            <div className="mb-6">
              <div className="bg-primary/10 border-2 border-primary rounded-lg p-6 text-center">
                <p className="text-sm text-muted-foreground mb-2">Your Connection Code</p>
                <div className="flex items-center justify-center gap-2 mb-3">
                  <span className="text-4xl font-mono font-bold tracking-wider">
                    {connectionCode.connection_code}
                  </span>
                  <button
                    onClick={copyCode}
                    className="p-2 hover:bg-primary/20 rounded transition-colors"
                    title="Copy code"
                  >
                    <Copy className="h-5 w-5" />
                  </button>
                </div>
                <div className="flex items-center justify-center gap-2 text-sm">
                  <span className="text-muted-foreground">Expires in:</span>
                  <Badge variant={timeRemaining < 60 ? 'destructive' : 'secondary'}>
                    {formatTime(timeRemaining)}
                  </Badge>
                </div>
              </div>
            </div>

            {/* Instructions */}
            <div className="mb-6 space-y-3">
              <h3 className="font-semibold flex items-center gap-2">
                <span className="flex items-center justify-center w-5 h-5 rounded-full bg-primary text-primary-foreground text-xs">
                  1
                </span>
                Open your Telegram bot
              </h3>
              <a
                href={`https://t.me/${process.env.NEXT_PUBLIC_TELEGRAM_BOT_USERNAME || 'YOUR_BOT'}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 p-3 bg-blue-600/10 hover:bg-blue-600/20 dark:bg-blue-600/20 dark:hover:bg-blue-600/30 rounded-lg transition-colors"
              >
                <ExternalLink className="h-4 w-4 text-blue-500" />
                <span className="text-blue-500 font-medium">Open in Telegram</span>
              </a>

              <h3 className="font-semibold flex items-center gap-2 mt-4">
                <span className="flex items-center justify-center w-5 h-5 rounded-full bg-primary text-primary-foreground text-xs">
                  2
                </span>
                Send the code to your bot
              </h3>
              <div className="p-3 bg-muted rounded-lg">
                <p className="text-sm text-muted-foreground mb-2">Send this message:</p>
                <code className="block font-mono text-sm">/start</code>
                <p className="text-sm text-muted-foreground mt-2 mb-1">Then send:</p>
                <code className="block font-mono text-sm">{connectionCode.connection_code}</code>
              </div>

              <h3 className="font-semibold flex items-center gap-2 mt-4">
                <span className="flex items-center justify-center w-5 h-5 rounded-full bg-primary text-primary-foreground text-xs">
                  3
                </span>
                Wait for confirmation
              </h3>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Waiting for your connection...</span>
              </div>
            </div>

            {/* Footer */}
            <div className="pt-4 border-t">
              <p className="text-xs text-muted-foreground text-center">
                Having trouble? Make sure you've started a conversation with your bot first.
              </p>
            </div>
          </Card>
        </div>
      )}
    </>
  );
};
