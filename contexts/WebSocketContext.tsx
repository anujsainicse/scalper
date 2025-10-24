'use client';

import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react';

export type WebSocketMessageType =
  | 'bot_update'
  | 'bot_created'
  | 'bot_deleted'
  | 'order_update'
  | 'order_filled'
  | 'price_update'
  | 'log_created'
  | 'pnl_update'
  | 'system'
  | 'ping'
  | 'pong';

export interface WebSocketMessage {
  type: WebSocketMessageType;
  data: any;
  timestamp: string;
}

export type WebSocketSubscriber = (message: WebSocketMessage) => void;

interface WebSocketContextValue {
  connected: boolean;
  reconnecting: boolean;
  subscribe: (type: WebSocketMessageType | WebSocketMessageType[], callback: WebSocketSubscriber) => () => void;
  send: (message: any) => void;
  connectionAttempts: number;
}

const WebSocketContext = createContext<WebSocketContextValue | null>(null);

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/v1/ws/app';
const RECONNECT_DELAY = 3000; // 3 seconds
const MAX_RECONNECT_DELAY = 30000; // 30 seconds
const PING_INTERVAL = 25000; // 25 seconds

interface Props {
  children: React.ReactNode;
}

export const WebSocketProvider: React.FC<Props> = ({ children }) => {
  const [connected, setConnected] = useState(false);
  const [reconnecting, setReconnecting] = useState(false);
  const [connectionAttempts, setConnectionAttempts] = useState(0);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const subscribersRef = useRef<Map<WebSocketMessageType, Set<WebSocketSubscriber>>>(new Map());
  const reconnectDelayRef = useRef(RECONNECT_DELAY);

  // Broadcast message to all subscribers
  const broadcastMessage = useCallback((message: WebSocketMessage) => {
    const subscribers = subscribersRef.current.get(message.type);
    if (subscribers) {
      subscribers.forEach((callback) => {
        try {
          callback(message);
        } catch (error) {
          console.error('Error in WebSocket subscriber:', error);
        }
      });
    }
  }, []);

  // Connect to WebSocket
  const connect = useCallback(() => {
    try {
      // Prevent duplicate connections
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        console.log('[WS] Already connected');
        return;
      }

      // Close existing connection
      if (wsRef.current) {
        wsRef.current.close();
      }

      console.log(`[WS] Connecting to ${WS_URL}...`);
      const ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        console.log('[WS] ✅ Connected');
        setConnected(true);
        setReconnecting(false);
        setConnectionAttempts(0);
        reconnectDelayRef.current = RECONNECT_DELAY; // Reset delay

        // Start ping interval
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, PING_INTERVAL);
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);

          // Skip ping/pong messages
          if (message.type === 'ping' || message.type === 'pong') {
            return;
          }

          console.log('[WS] Message received:', message.type);
          broadcastMessage(message);
        } catch (error) {
          console.error('[WS] Error parsing message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('[WS] ❌ Error:', error);
      };

      ws.onclose = () => {
        console.log('[WS] Disconnected');
        setConnected(false);

        // Clear ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        // Schedule reconnect with exponential backoff
        scheduleReconnect();
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('[WS] Connection error:', error);
      scheduleReconnect();
    }
  }, [broadcastMessage]);

  // Schedule reconnection with exponential backoff
  const scheduleReconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      return; // Already scheduled
    }

    setReconnecting(true);
    setConnectionAttempts((prev) => prev + 1);

    const delay = Math.min(reconnectDelayRef.current, MAX_RECONNECT_DELAY);
    console.log(`[WS] Reconnecting in ${delay / 1000}s...`);

    reconnectTimeoutRef.current = setTimeout(() => {
      reconnectTimeoutRef.current = null;
      reconnectDelayRef.current = Math.min(reconnectDelayRef.current * 1.5, MAX_RECONNECT_DELAY);
      connect();
    }, delay);
  }, [connect]);

  // Subscribe to WebSocket messages
  const subscribe = useCallback((
    types: WebSocketMessageType | WebSocketMessageType[],
    callback: WebSocketSubscriber
  ): (() => void) => {
    const typeArray = Array.isArray(types) ? types : [types];

    typeArray.forEach((type) => {
      if (!subscribersRef.current.has(type)) {
        subscribersRef.current.set(type, new Set());
      }
      subscribersRef.current.get(type)!.add(callback);
    });

    // Return unsubscribe function
    return () => {
      typeArray.forEach((type) => {
        subscribersRef.current.get(type)?.delete(callback);
      });
    };
  }, []);

  // Send message to WebSocket
  const send = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('[WS] Cannot send message - not connected');
    }
  }, []);

  // Connect on mount
  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const value: WebSocketContextValue = {
    connected,
    reconnecting,
    subscribe,
    send,
    connectionAttempts,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = (): WebSocketContextValue => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return context;
};
