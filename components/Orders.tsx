'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader } from './ui/card';
import { Badge } from './ui/badge';
import { Order, OrderStatus } from '@/types/bot';
import { useBotStore } from '@/store/botStore';
import { formatTime } from '@/utils/formatters';
import { Package, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from './ui/button';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const Orders: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const bots = useBotStore((state) => state.bots);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/v1/orders/?limit=100`);
      if (!response.ok) throw new Error('Failed to fetch orders');

      const data = await response.json();

      // Transform data to match Order interface
      const transformedOrders: Order[] = data.orders.map((order: any) => ({
        id: order.id,
        botId: order.bot_id,
        exchangeOrderId: order.exchange_order_id,
        symbol: order.symbol,
        side: order.side,
        orderType: order.order_type,
        quantity: parseFloat(order.quantity),
        price: order.price ? parseFloat(order.price) : undefined,
        status: order.status,
        filledQuantity: parseFloat(order.filled_quantity),
        filledPrice: order.filled_price ? parseFloat(order.filled_price) : undefined,
        commission: parseFloat(order.commission),
        createdAt: new Date(order.created_at),
        updatedAt: new Date(order.updated_at),
      }));

      setOrders(transformedOrders);
      setLastRefresh(new Date());
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh every 5 seconds
  useEffect(() => {
    fetchOrders();
    const interval = setInterval(fetchOrders, 5000);
    return () => clearInterval(interval);
  }, []);

  // Get bot info for display
  const getBotInfo = (botId: string) => {
    const bot = bots.find((b) => b.id === botId);
    return bot ? `${bot.ticker} (${bot.exchange})` : botId.slice(0, 8);
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold">Orders</h3>
            <Badge variant="secondary" className="px-2 py-0">
              {orders.length}
            </Badge>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              Last updated: {formatTime(lastRefresh)}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchOrders}
              disabled={loading}
              className="h-8"
            >
              <RefreshCw className={cn('h-4 w-4 mr-2', loading && 'animate-spin')} />
              Refresh
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto">
        {orders.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <div className="text-center">
              <Package className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>No orders yet</p>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b">
                <tr className="text-left">
                  <th className="pb-2 font-semibold">Bot</th>
                  <th className="pb-2 font-semibold">Symbol</th>
                  <th className="pb-2 font-semibold">Side</th>
                  <th className="pb-2 font-semibold">Type</th>
                  <th className="pb-2 font-semibold text-right">Quantity</th>
                  <th className="pb-2 font-semibold text-right">Price</th>
                  <th className="pb-2 font-semibold">Status</th>
                  <th className="pb-2 font-semibold text-right">Filled Qty</th>
                  <th className="pb-2 font-semibold">Created At</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <OrderRow key={order.id} order={order} botInfo={getBotInfo(order.botId)} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

interface OrderRowProps {
  order: Order;
  botInfo: string;
}

const OrderRow: React.FC<OrderRowProps> = ({ order, botInfo }) => {
  const statusColors: Record<OrderStatus, string> = {
    PENDING: 'bg-blue-500/10 text-blue-400 border-blue-400/20',
    FILLED: 'bg-green-500/10 text-green-400 border-green-400/20',
    PARTIALLY_FILLED: 'bg-yellow-500/10 text-yellow-400 border-yellow-400/20',
    CANCELLED: 'bg-gray-500/10 text-gray-400 border-gray-400/20',
    FAILED: 'bg-red-500/10 text-red-400 border-red-400/20',
  };

  const sideColors = {
    BUY: 'text-green-400',
    SELL: 'text-red-400',
  };

  return (
    <tr className="border-b border-border/40 hover:bg-accent/50 transition-colors">
      <td className="py-2 font-mono text-xs">{botInfo}</td>
      <td className="py-2 font-mono">{order.symbol}</td>
      <td className="py-2">
        <span className={cn('font-semibold', sideColors[order.side])}>
          {order.side}
        </span>
      </td>
      <td className="py-2 text-muted-foreground">{order.orderType}</td>
      <td className="py-2 text-right font-mono">{order.quantity.toFixed(4)}</td>
      <td className="py-2 text-right font-mono">
        {order.price ? `$${order.price.toFixed(2)}` : '-'}
      </td>
      <td className="py-2">
        <Badge variant="outline" className={cn('text-xs', statusColors[order.status])}>
          {order.status}
        </Badge>
      </td>
      <td className="py-2 text-right font-mono">
        {order.filledQuantity > 0 ? order.filledQuantity.toFixed(4) : '-'}
      </td>
      <td className="py-2 text-muted-foreground font-mono text-xs">
        {formatTime(order.createdAt)}
      </td>
    </tr>
  );
};
