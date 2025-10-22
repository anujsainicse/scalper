// API client for FastAPI backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_V1 = `${API_BASE_URL}/api/v1`;

// Types matching backend schemas
export type BotStatus = 'ACTIVE' | 'STOPPED' | 'ERROR';
export type OrderSide = 'BUY' | 'SELL';
export type Exchange = 'CoinDCX F' | 'Binance';

export interface Bot {
  id: string;
  ticker: string;
  exchange: Exchange;
  first_order: OrderSide;
  quantity: number;
  buy_price: number;
  sell_price: number;
  trailing_percent: number | null;
  infinite_loop: boolean;
  status: BotStatus;
  pnl: number;
  total_trades: number;
  last_fill_time: string | null;
  last_fill_side: OrderSide | null;
  last_fill_price: number | null;
  created_at: string;
  updated_at: string;
  config: Record<string, any> | null;
}

export interface BotCreate {
  ticker: string;
  exchange: Exchange;
  first_order: OrderSide;
  quantity: number;
  buy_price: number;
  sell_price: number;
  trailing_percent?: number | null;
  infinite_loop?: boolean;
}

export interface ActivityLog {
  id: string;
  bot_id: string | null;
  level: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR' | 'TELEGRAM';
  message: string;
  timestamp: string;
  extra_data: Record<string, any> | null;
}

export interface BotStatistics {
  total_bots: number;
  active_bots: number;
  stopped_bots: number;
  total_pnl: number;
  total_trades: number;
}

// API Client
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    console.log(`[API-REQUEST] ${options?.method || 'GET'} ${url}`);

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    console.log(`[API-RESPONSE] Status: ${response.status} ${response.statusText}`);
    console.log(`[API-RESPONSE] Content-Length: ${response.headers.get('content-length')}`);

    if (!response.ok) {
      console.error(`[API-RESPONSE] Request failed with status ${response.status}`);
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      console.error(`[API-RESPONSE] Error details:`, error);
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    // Handle 204 No Content responses (no body to parse)
    if (response.status === 204 || response.headers.get('content-length') === '0') {
      console.log(`[API-RESPONSE] 204 No Content - returning null`);
      return null as T;
    }

    const data = await response.json();
    console.log(`[API-RESPONSE] Response data:`, data);
    return data;
  }

  // Bot endpoints
  async getBots(filters?: { status?: BotStatus; skip?: number; limit?: number }): Promise<Bot[]> {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.skip !== undefined) params.append('skip', filters.skip.toString());
    if (filters?.limit !== undefined) params.append('limit', filters.limit.toString());

    const query = params.toString() ? `?${params.toString()}` : '';
    return this.request<Bot[]>(`/bots/${query}`);
  }

  async getBot(botId: string): Promise<Bot> {
    return this.request<Bot>(`/bots/${botId}`);
  }

  async createBot(data: BotCreate): Promise<Bot> {
    return this.request<Bot>('/bots/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateBot(botId: string, data: Partial<BotCreate>): Promise<Bot> {
    return this.request<Bot>(`/bots/${botId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteBot(botId: string): Promise<void> {
    console.log('[API] deleteBot called with botId:', botId);
    console.log('[API] Making DELETE request to:', `${this.baseUrl}/bots/${botId}`);
    try {
      const result = await this.request<void>(`/bots/${botId}`, {
        method: 'DELETE',
      });
      console.log('[API] DELETE request completed successfully, result:', result);
      return result;
    } catch (error) {
      console.error('[API] DELETE request failed:', error);
      throw error;
    }
  }

  async startBot(botId: string): Promise<Bot> {
    return this.request<Bot>(`/bots/${botId}/start`, {
      method: 'POST',
    });
  }

  async stopBot(botId: string): Promise<Bot> {
    return this.request<Bot>(`/bots/${botId}/stop`, {
      method: 'POST',
    });
  }

  async toggleBot(botId: string): Promise<Bot> {
    return this.request<Bot>(`/bots/${botId}/toggle`, {
      method: 'POST',
    });
  }

  async stopAllBots(): Promise<{ message: string; count: number }> {
    return this.request<{ message: string; count: number }>('/bots/stop-all', {
      method: 'POST',
    });
  }

  async getStatistics(): Promise<BotStatistics> {
    return this.request<BotStatistics>('/bots/statistics/summary');
  }

  // Activity log endpoints
  async getLogs(filters?: {
    bot_id?: string;
    level?: string;
    skip?: number;
    limit?: number
  }): Promise<ActivityLog[]> {
    const params = new URLSearchParams();
    if (filters?.bot_id) params.append('bot_id', filters.bot_id);
    if (filters?.level) params.append('level', filters.level);
    if (filters?.skip !== undefined) params.append('skip', filters.skip.toString());
    if (filters?.limit !== undefined) params.append('limit', filters.limit.toString());

    const query = params.toString() ? `?${params.toString()}` : '';
    return this.request<ActivityLog[]>(`/logs/${query}`);
  }

  async createLog(data: {
    bot_id?: string;
    level: string;
    message: string;
    extra_data?: Record<string, any>;
  }): Promise<ActivityLog> {
    return this.request<ActivityLog>('/logs/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async clearLogs(): Promise<{ message: string }> {
    return this.request<{ message: string }>('/logs/', {
      method: 'DELETE',
    });
  }

  async getLogCounts(): Promise<Record<string, number>> {
    return this.request<Record<string, number>>('/logs/count');
  }

  // Price endpoints
  async getLTPData(exchange: string, ticker: string): Promise<{
    success: boolean;
    redis_key?: string;
    exchange?: string;
    ticker?: string;
    base_symbol?: string;
    data?: Record<string, any>;
    message?: string;
  }> {
    const params = new URLSearchParams();
    params.append('exchange', exchange);
    params.append('ticker', ticker);

    return this.request<any>(`/price/ltp?${params.toString()}`);
  }
}

// Export singleton instance
export const api = new ApiClient(API_V1);
