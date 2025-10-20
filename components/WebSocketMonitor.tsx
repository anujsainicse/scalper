'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Radio, WifiOff, RefreshCw, Trash2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { formatTime } from '@/utils/formatters';

interface WebSocketEvent {
  id: string;
  timestamp: Date;
  type: 'order' | 'position' | 'balance';
  data: any;
}

interface OrderUpdate {
  id: string;
  pair: string;
  side: string;
  status: string;
  order_type: string;
  price: number;
  total_quantity: number;
  filled_quantity: number;
  remaining_quantity: number;
  leverage: number;
  display_message?: string;
  created_at: number;
}

interface PositionUpdate {
  id: string;
  pair: string;
  active_pos: number;
  avg_price: number;
  liquidation_price: number;
  locked_margin: number;
  unrealized_pnl?: number;
}

interface BalanceUpdate {
  currency_short_name: string;
  balance: string;
  locked_balance: string;
}

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/v1/ws/coindcx';

// Persistent event storage outside component (survives unmounting)
const eventHistory: WebSocketEvent[] = [];
const seenEventIds = new Set<string>();

export const WebSocketMonitor: React.FC = () => {
  const [events, setEvents] = useState<WebSocketEvent[]>(eventHistory);
  const [connected, setConnected] = useState(false);
  const [reconnecting, setReconnecting] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const connectWebSocket = () => {
    try {
      // Prevent duplicate connections
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        console.log('WebSocket already connected');
        return;
      }

      // Close existing connection if any
      if (wsRef.current) {
        wsRef.current.close();
      }

      // Cancel any pending reconnect
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }

      console.log('Connecting to WebSocket:', WS_URL);

      const ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        console.log('✅ WebSocket connected');
        setConnected(true);
        setReconnecting(false);

        // Start ping interval to keep connection alive
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
          }
        }, 25000);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          // Handle system messages
          if (data.type === 'system') {
            console.log('System message:', data.data.message);
            return;
          }

          // Handle ping/pong
          if (data.type === 'ping' || data.type === 'pong') {
            return;
          }

          // Filter out unnecessary events
          if (data.type === 'position') {
            // Skip position updates with no active position and zero values
            if (
              data.data.active_pos === 0 &&
              data.data.avg_price === 0 &&
              data.data.liquidation_price === 0 &&
              data.data.locked_margin === 0
            ) {
              console.log('📊 Skipping empty position update');
              return;
            }
          }

          // Deduplicate events based on data ID, type, and status (for orders)
          // Include status for orders to allow status updates (initial -> open -> cancelled)
          const eventKey = data.type === 'order'
            ? `${data.type}-${data.data.id}-${data.data.status}`
            : `${data.type}-${data.data.id || data.data.currency_short_name}`;

          if (seenEventIds.has(eventKey)) {
            console.log(`🔄 Skipping duplicate ${data.type} event:`, eventKey);
            return;
          }

          seenEventIds.add(eventKey);

          // Add event to persistent storage
          const newEvent = {
            id: `${data.id}-${Date.now()}`, // Add timestamp to ensure unique keys
            timestamp: new Date(data.timestamp),
            type: data.type,
            data: data.data,
          };

          eventHistory.unshift(newEvent);

          // Update component state
          setEvents([...eventHistory]);

          console.log('📡 Event received:', data.type, data.data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        // Only log errors if we're not already disconnected/reconnecting
        if (ws.readyState !== WebSocket.CLOSING && ws.readyState !== WebSocket.CLOSED) {
          console.error('❌ WebSocket error:', error);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket closed');
        setConnected(false);

        // Clear ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        // Schedule reconnect
        scheduleReconnect();
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('WebSocket connection error:', error);
      setConnected(false);
      scheduleReconnect();
    }
  };

  const scheduleReconnect = () => {
    setReconnecting(true);
    reconnectTimeoutRef.current = setTimeout(() => {
      connectWebSocket();
    }, 5000);
  };

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
    setConnected(false);
    setReconnecting(false);
  };

  const clearEvents = () => {
    eventHistory.length = 0; // Clear persistent storage
    seenEventIds.clear(); // Clear deduplication set
    setEvents([]);
  };

  useEffect(() => {
    connectWebSocket();

    return () => {
      disconnectWebSocket();
    };
  }, []);

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold">WebSocket Monitor</h3>
            <Badge
              variant="outline"
              className={cn(
                'px-2 py-0',
                connected
                  ? 'bg-green-500/10 text-green-400 border-green-400/20'
                  : reconnecting
                  ? 'bg-yellow-500/10 text-yellow-400 border-yellow-400/20'
                  : 'bg-red-500/10 text-red-400 border-red-400/20'
              )}
            >
              <div className="flex items-center gap-1">
                {connected ? (
                  <>
                    <Radio className="h-3 w-3 animate-pulse" />
                    <span>Live</span>
                  </>
                ) : reconnecting ? (
                  <>
                    <RefreshCw className="h-3 w-3 animate-spin" />
                    <span>Reconnecting...</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="h-3 w-3" />
                    <span>Disconnected</span>
                  </>
                )}
              </div>
            </Badge>
            <Badge variant="secondary" className="px-2 py-0">
              {events.length} events
            </Badge>
          </div>
          <div className="flex items-center gap-2">
            {!connected && !reconnecting && (
              <Button
                variant="outline"
                size="sm"
                onClick={connectWebSocket}
                className="h-8"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Reconnect
              </Button>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={clearEvents}
              disabled={events.length === 0}
              className="h-8"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Clear
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto p-4 bg-gradient-to-b from-muted to-background dark:from-zinc-950 dark:to-black">
        {events.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <div className="text-center">
              <Radio className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>Waiting for WebSocket events...</p>
              <p className="text-sm mt-1">
                {connected
                  ? 'Place an order to see real-time updates'
                  : 'Connect to WebSocket to start monitoring'}
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-2 font-mono text-sm">
            {events.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

interface EventCardProps {
  event: WebSocketEvent;
}

const EventCard: React.FC<EventCardProps> = ({ event }) => {
  const eventTypeColors = {
    order: 'text-blue-500 dark:text-blue-400',
    position: 'text-purple-500 dark:text-purple-400',
    balance: 'text-green-500 dark:text-green-400',
  };

  const eventTypeBgColors = {
    order: 'bg-blue-500/10 border-blue-500/20 dark:border-blue-500/20',
    position: 'bg-purple-500/10 border-purple-500/20 dark:border-purple-500/20',
    balance: 'bg-green-500/10 border-green-500/20 dark:border-green-500/20',
  };

  // Format event message based on type
  const getEventMessage = () => {
    if (event.type === 'order') {
      const order = event.data as OrderUpdate;
      return `${order.side.toUpperCase()} ${order.pair} - ${order.status.toUpperCase()} | Price: $${order.price.toFixed(2)} | Qty: ${order.total_quantity}${order.display_message ? ` | ${order.display_message}` : ''}`;
    } else if (event.type === 'position') {
      const position = event.data as PositionUpdate;
      return `Position ${position.pair} | Active: ${position.active_pos} | Avg Price: $${position.avg_price?.toFixed(2) ?? '0.00'}${position.unrealized_pnl !== undefined && position.unrealized_pnl !== null ? ` | PnL: $${position.unrealized_pnl.toFixed(2)}` : ''}`;
    } else if (event.type === 'balance') {
      const balance = event.data as BalanceUpdate;
      const available = parseFloat(balance.balance);
      const locked = parseFloat(balance.locked_balance);
      return `Balance ${balance.currency_short_name} | Available: $${available.toFixed(2)} | Locked: $${locked.toFixed(2)} | Total: $${(available + locked).toFixed(2)}`;
    }
    return 'Unknown event';
  };

  return (
    <div
      className={cn(
        'px-4 py-3 rounded-xl border transition-all duration-200 hover:scale-[1.01]',
        eventTypeBgColors[event.type]
      )}
    >
      <div className="flex items-start gap-3">
        <span className="text-muted-foreground dark:text-zinc-500 whitespace-nowrap text-xs font-semibold">
          {formatTime(event.timestamp)}
        </span>
        <span
          className={cn(
            eventTypeColors[event.type],
            'font-bold uppercase min-w-[80px] whitespace-nowrap text-xs'
          )}
        >
          {event.type}
        </span>
        <span className="text-foreground dark:text-zinc-200 flex-1 text-sm">
          {getEventMessage()}
        </span>
      </div>
    </div>
  );
};

const OrderEventDetails: React.FC<{ data: OrderUpdate }> = ({ data }) => {
  const sideColors = {
    buy: 'text-green-400',
    sell: 'text-red-400',
  };

  return (
    <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm font-mono">
      <div className="text-muted-foreground">Order ID:</div>
      <div className="text-right truncate">{data.id.slice(0, 12)}...</div>

      <div className="text-muted-foreground">Pair:</div>
      <div className="text-right font-semibold">{data.pair}</div>

      <div className="text-muted-foreground">Side:</div>
      <div className={cn('text-right font-semibold uppercase', sideColors[data.side.toLowerCase() as 'buy' | 'sell'])}>
        {data.side}
      </div>

      <div className="text-muted-foreground">Type:</div>
      <div className="text-right">{data.order_type}</div>

      <div className="text-muted-foreground">Price:</div>
      <div className="text-right">${data.price.toFixed(2)}</div>

      <div className="text-muted-foreground">Quantity:</div>
      <div className="text-right">{data.total_quantity}</div>

      <div className="text-muted-foreground">Filled:</div>
      <div className="text-right text-green-400">{data.filled_quantity}</div>

      <div className="text-muted-foreground">Remaining:</div>
      <div className="text-right text-yellow-400">{data.remaining_quantity}</div>

      <div className="text-muted-foreground">Leverage:</div>
      <div className="text-right">{data.leverage}x</div>

      {data.display_message && (
        <>
          <div className="text-muted-foreground col-span-2 mt-1 border-t border-border pt-1">
            {data.display_message}
          </div>
        </>
      )}
    </div>
  );
};

const PositionEventDetails: React.FC<{ data: PositionUpdate }> = ({ data }) => {
  return (
    <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm font-mono">
      <div className="text-muted-foreground">Position ID:</div>
      <div className="text-right truncate">{data.id.slice(0, 12)}...</div>

      <div className="text-muted-foreground">Pair:</div>
      <div className="text-right font-semibold">{data.pair}</div>

      <div className="text-muted-foreground">Active Pos:</div>
      <div className="text-right">{data.active_pos}</div>

      <div className="text-muted-foreground">Avg Price:</div>
      <div className="text-right">${data.avg_price?.toFixed(2) ?? '0.00'}</div>

      <div className="text-muted-foreground">Liq. Price:</div>
      <div className="text-right text-red-400">${data.liquidation_price?.toFixed(2) ?? '0.00'}</div>

      <div className="text-muted-foreground">Locked Margin:</div>
      <div className="text-right">${data.locked_margin?.toFixed(2) ?? '0.00'}</div>

      {data.unrealized_pnl !== undefined && data.unrealized_pnl !== null && (
        <>
          <div className="text-muted-foreground">Unrealized PnL:</div>
          <div
            className={cn(
              'text-right font-semibold',
              data.unrealized_pnl > 0
                ? 'text-green-400'
                : data.unrealized_pnl < 0
                ? 'text-red-400'
                : 'text-gray-400'
            )}
          >
            ${data.unrealized_pnl.toFixed(2)}
          </div>
        </>
      )}
    </div>
  );
};

const BalanceEventDetails: React.FC<{ data: BalanceUpdate }> = ({ data }) => {
  return (
    <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm font-mono">
      <div className="text-muted-foreground">Currency:</div>
      <div className="text-right font-semibold">{data.currency_short_name}</div>

      <div className="text-muted-foreground">Available:</div>
      <div className="text-right text-green-400">
        ${parseFloat(data.balance).toFixed(2)}
      </div>

      <div className="text-muted-foreground">Locked:</div>
      <div className="text-right text-yellow-400">
        ${parseFloat(data.locked_balance).toFixed(2)}
      </div>

      <div className="text-muted-foreground">Total:</div>
      <div className="text-right font-semibold">
        ${(parseFloat(data.balance) + parseFloat(data.locked_balance)).toFixed(2)}
      </div>
    </div>
  );
};
