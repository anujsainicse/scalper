'use client';

import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { RadioGroup, RadioGroupItem } from './ui/radio-group';
import { Checkbox } from './ui/checkbox';
import { Button } from './ui/button';
import { Alert, AlertDescription } from './ui/alert';
import { Rocket, AlertCircle, RotateCcw } from 'lucide-react';
import { useBotStore } from '@/store/botStore';
import { Exchange, OrderSide, BotFormData } from '@/types/bot';
import { validateTicker } from '@/utils/formatters';
import { EXCHANGES, TRAILING_PERCENTAGES, LEVERAGE_OPTIONS, POPULAR_TICKERS } from '@/config/bot-config';
import { api } from '@/lib/api';

export const BotConfiguration: React.FC = () => {
  const addBot = useBotStore((state) => state.addBot);
  const updateBotFromForm = useBotStore((state) => state.updateBotFromForm);
  const setEditingBot = useBotStore((state) => state.setEditingBot);
  const editingBotId = useBotStore((state) => state.editingBotId);
  const bots = useBotStore((state) => state.bots);
  const addLog = useBotStore((state) => state.addLog);

  const [formData, setFormData] = useState<BotFormData>({
    ticker: POPULAR_TICKERS[0] || '',
    exchange: 'CoinDCX F',
    firstOrder: 'BUY',
    quantity: 1,
    customQuantity: undefined,
    buyPrice: 0,
    sellPrice: 0,
    trailingPercent: undefined,
    leverage: 3,
    infiniteLoop: true,
  });

  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [priceData, setPriceData] = useState<Record<string, any> | null>(null);
  const [loadingPrice, setLoadingPrice] = useState(false);
  const [decimalPlaces, setDecimalPlaces] = useState<number>(2);

  // Load bot data when editing
  // Only reload when editingBotId changes, not when bots array updates (every 5 seconds)
  // This prevents overwriting user edits during edit mode
  React.useEffect(() => {
    if (editingBotId) {
      const bot = bots.find((b) => b.id === editingBotId);
      if (bot) {
        setFormData({
          ticker: bot.ticker,
          exchange: bot.exchange,
          firstOrder: bot.firstOrder,
          quantity: bot.quantity,
          customQuantity: undefined,
          buyPrice: bot.buyPrice,
          sellPrice: bot.sellPrice,
          trailingPercent: bot.trailingPercent,
          leverage: bot.leverage || 3,
          infiniteLoop: bot.infiniteLoop,
        });
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [editingBotId]);

  // Helper function to calculate decimal places from a number
  const getDecimalPlaces = (value: string | number): number => {
    const strValue = String(value);
    if (strValue.includes('.')) {
      return strValue.split('.')[1].length;
    }
    return 0;
  };

  // Helper function to round to specific decimal places
  const roundToDecimalPlaces = (value: number, places: number): number => {
    const multiplier = Math.pow(10, places);
    return Math.round(value * multiplier) / multiplier;
  };

  // Fetch price data function (extracted for reuse)
  const fetchPriceData = async (ticker?: string, exchange?: Exchange, updatePrices: boolean = true) => {
    const targetTicker = ticker || formData.ticker;
    const targetExchange = exchange || formData.exchange;

    if (!targetTicker || !targetExchange) return;

    setLoadingPrice(true);
    try {
      const response = await api.getLTPData(targetExchange, targetTicker);
      if (response.success && response.data) {
        setPriceData(response.data);
        // Calculate decimal places from LTP
        if (response.data.ltp) {
          const ltpDecimalPlaces = getDecimalPlaces(response.data.ltp);
          setDecimalPlaces(ltpDecimalPlaces);

          // Only update buy/sell prices if updatePrices is true (not in editing mode)
          if (updatePrices) {
            // Set buy price 2% below LTP and sell price 2% above LTP
            const currentPrice = Number(response.data.ltp);
            const buyPrice = roundToDecimalPlaces(currentPrice * 0.98, ltpDecimalPlaces);
            const sellPrice = roundToDecimalPlaces(currentPrice * 1.02, ltpDecimalPlaces);

            setFormData((prev) => ({
              ...prev,
              buyPrice,
              sellPrice,
            }));
          }
        }
      } else {
        setPriceData(null);
      }
    } catch (error) {
      console.error('Failed to fetch price data:', error);
      setPriceData(null);
    } finally {
      setLoadingPrice(false);
    }
  };

  // Fetch price data when ticker or exchange changes
  // Don't auto-update prices when editing a bot
  useEffect(() => {
    const shouldUpdatePrices = !editingBotId;
    fetchPriceData(undefined, undefined, shouldUpdatePrices);
  }, [formData.ticker, formData.exchange, editingBotId]);

  const handleInputChange = (
    field: keyof BotFormData,
    value: string | number | boolean
  ) => {
    // Round numeric values for quantity, buyPrice, and sellPrice based on LTP decimal places
    let processedValue = value;
    if (typeof value === 'number' && (field === 'quantity' || field === 'buyPrice' || field === 'sellPrice')) {
      processedValue = roundToDecimalPlaces(value, decimalPlaces);
    }

    setFormData((prev) => ({ ...prev, [field]: processedValue }));
    // Clear errors when user starts typing
    if (validationErrors.length > 0) {
      setValidationErrors([]);
    }
  };

  const validateForm = (): boolean => {
    const errors: string[] = [];

    // Ticker validation
    if (!formData.ticker) {
      errors.push('Ticker is required');
    } else if (!validateTicker(formData.ticker.toUpperCase())) {
      errors.push('Invalid ticker format. Use format like BTC/USDT');
    }

    // Quantity validation
    if (!formData.quantity || formData.quantity <= 0) {
      errors.push('Quantity must be greater than 0');
    }

    // Price validations
    if (!formData.buyPrice || formData.buyPrice <= 0) {
      errors.push('Buy price must be greater than 0');
    }

    if (!formData.sellPrice || formData.sellPrice <= 0) {
      errors.push('Sell price must be greater than 0');
    }

    if (formData.buyPrice && formData.sellPrice && formData.buyPrice >= formData.sellPrice) {
      errors.push('Sell price must be greater than buy price');
    }

    // Trailing percentage validation
    if (formData.trailingPercent && (formData.trailingPercent < 0.1 || formData.trailingPercent > 3.0)) {
      errors.push('Trailing percentage must be between 0.1% and 3.0%');
    }

    setValidationErrors(errors);
    return errors.length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      addLog('ERROR', 'Bot configuration validation failed');
      return;
    }

    // Format ticker to uppercase
    const formattedData = {
      ...formData,
      ticker: formData.ticker.toUpperCase(),
      trailingPercent: formData.trailingPercent ? Number(formData.trailingPercent) : undefined,
    };

    try {
      if (editingBotId) {
        // Update existing bot
        await updateBotFromForm(editingBotId, formattedData);
        toast.success(`✅ Bot updated for ${formattedData.ticker}`);
      } else {
        // Create new bot
        await addBot(formattedData);
        toast.success(`✅ Bot created for ${formattedData.ticker}`);
      }

      // Calculate default prices if price data is available
      let defaultBuyPrice = 0;
      let defaultSellPrice = 0;

      if (priceData && priceData.ltp) {
        const currentPrice = Number(priceData.ltp);
        const ltpDecimalPlaces = getDecimalPlaces(priceData.ltp);
        defaultBuyPrice = roundToDecimalPlaces(currentPrice * 0.98, ltpDecimalPlaces);
        defaultSellPrice = roundToDecimalPlaces(currentPrice * 1.02, ltpDecimalPlaces);
      }

      // Reset form
      setFormData({
        ticker: POPULAR_TICKERS[0] || '',
        exchange: 'CoinDCX F',
        firstOrder: 'BUY',
        quantity: 1,
        customQuantity: undefined,
        buyPrice: defaultBuyPrice,
        sellPrice: defaultSellPrice,
        trailingPercent: undefined,
        leverage: 3,
        infiniteLoop: true,
      });
      setEditingBot(null);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save bot';
      toast.error(`❌ ${errorMessage}`);
      addLog('ERROR', errorMessage);
    }
  };

  const handleReset = async () => {
    const defaultTicker = POPULAR_TICKERS[0] || '';
    const defaultExchange: Exchange = 'CoinDCX F';

    // Reset to default values first
    setFormData({
      ticker: defaultTicker,
      exchange: defaultExchange,
      firstOrder: 'BUY',
      quantity: 1,
      customQuantity: undefined,
      buyPrice: 0,
      sellPrice: 0,
      trailingPercent: undefined,
      leverage: 3,
      infiniteLoop: true,
    });

    // Clear editing mode
    setEditingBot(null);

    // Clear validation errors
    setValidationErrors([]);

    // Fetch fresh LTP data for the default ticker and exchange
    // This will automatically update buyPrice and sellPrice via the fetchPriceData function
    await fetchPriceData(defaultTicker, defaultExchange);

    toast.success('✅ Form reset to defaults');
  };

  return (
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle>Bot Configuration</CardTitle>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={handleReset}
          className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:text-red-500 dark:hover:text-red-400 dark:hover:bg-red-950"
          title="Reset to default values"
        >
          <RotateCcw className="h-4 w-4" />
          <span className="ml-1 text-sm font-medium">reset</span>
        </Button>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="exchange">Exchange</Label>
            <Select
              value={formData.exchange}
              onValueChange={(value) => handleInputChange('exchange', value as Exchange)}
            >
              <SelectTrigger id="exchange">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {EXCHANGES.map((exchange) => (
                  <SelectItem key={exchange.value.toString()} value={exchange.value.toString()}>
                    {exchange.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="ticker">Ticker</Label>
            <Select
              value={formData.ticker}
              onValueChange={(value) => handleInputChange('ticker', value)}
            >
              <SelectTrigger id="ticker">
                <SelectValue placeholder="Select a ticker" />
              </SelectTrigger>
              <SelectContent>
                {POPULAR_TICKERS.map((ticker) => (
                  <SelectItem key={ticker} value={ticker}>
                    {ticker}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-start justify-between gap-4">
            <div className="space-y-2 flex-1">
              <Label>First Order</Label>
              <RadioGroup
                value={formData.firstOrder}
                onValueChange={(value) => handleInputChange('firstOrder', value as OrderSide)}
                className="flex gap-4"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="BUY" id="buy" />
                  <Label htmlFor="buy" className="font-normal cursor-pointer">Buy</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="SELL" id="sell" />
                  <Label htmlFor="sell" className="font-normal cursor-pointer">Sell</Label>
                </div>
              </RadioGroup>
            </div>

            {/* Price Data Display */}
            <div className="flex items-center justify-center min-w-[120px]">
              {loadingPrice ? (
                <p className="text-sm text-muted-foreground animate-pulse">Loading...</p>
              ) : priceData && priceData.ltp ? (
                <div className="text-center">
                  <p className="text-xs text-muted-foreground">LTP</p>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-500">{priceData.ltp}</p>
                </div>
              ) : (
                <div className="text-center">
                  <p className="text-xs text-muted-foreground">LTP</p>
                  <p className="text-sm text-yellow-600 dark:text-yellow-500">N/A</p>
                </div>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="quantity">Quantity</Label>
            <div className="flex items-center gap-2">
              <div className="flex gap-1">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('quantity', Math.max(0, (formData.quantity || 0) - 10))}
                  className="px-2 text-red-600 dark:text-red-500 hover:text-red-700 dark:hover:text-red-600"
                >
                  -10
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('quantity', Math.max(0, (formData.quantity || 0) - 5))}
                  className="px-2 text-red-600 dark:text-red-500 hover:text-red-700 dark:hover:text-red-600"
                >
                  -5
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('quantity', Math.max(0, (formData.quantity || 0) - 2))}
                  className="px-2 text-red-600 dark:text-red-500 hover:text-red-700 dark:hover:text-red-600"
                >
                  -2
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('quantity', Math.max(0, (formData.quantity || 0) - 1))}
                  className="px-2 text-red-600 dark:text-red-500 hover:text-red-700 dark:hover:text-red-600"
                >
                  -1
                </Button>
              </div>
              <Input
                id="quantity"
                type="number"
                step={decimalPlaces > 0 ? Math.pow(10, -decimalPlaces).toFixed(decimalPlaces) : '1'}
                placeholder="Enter quantity"
                value={formData.quantity || ''}
                onChange={(e) => handleInputChange('quantity', Number(e.target.value))}
                className="flex-1 text-center"
              />
              <div className="flex gap-1">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('quantity', (formData.quantity || 0) + 1)}
                  className="px-2 text-green-600 dark:text-green-500 hover:text-green-700 dark:hover:text-green-600"
                >
                  +1
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('quantity', (formData.quantity || 0) + 2)}
                  className="px-2 text-green-600 dark:text-green-500 hover:text-green-700 dark:hover:text-green-600"
                >
                  +2
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('quantity', (formData.quantity || 0) + 5)}
                  className="px-2 text-green-600 dark:text-green-500 hover:text-green-700 dark:hover:text-green-600"
                >
                  +5
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('quantity', (formData.quantity || 0) + 10)}
                  className="px-2 text-green-600 dark:text-green-500 hover:text-green-700 dark:hover:text-green-600"
                >
                  +10
                </Button>
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="buyPrice">Buy Price</Label>
            <div className="flex items-center gap-2">
              <div className="flex gap-1">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('buyPrice', Math.max(0, (formData.buyPrice || 0) * 0.99))}
                  className="px-2 text-red-600 dark:text-red-500 hover:text-red-700 dark:hover:text-red-600"
                >
                  -1%
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('buyPrice', Math.max(0, (formData.buyPrice || 0) * 0.995))}
                  className="px-2 text-red-600 dark:text-red-500 hover:text-red-700 dark:hover:text-red-600"
                >
                  -0.5%
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('buyPrice', Math.max(0, (formData.buyPrice || 0) * 0.999))}
                  className="px-2 text-red-600 dark:text-red-500 hover:text-red-700 dark:hover:text-red-600"
                >
                  -0.1%
                </Button>
              </div>
              <Input
                id="buyPrice"
                type="number"
                step={decimalPlaces > 0 ? Math.pow(10, -decimalPlaces).toFixed(decimalPlaces) : '1'}
                placeholder="Enter buy price"
                value={formData.buyPrice || ''}
                onChange={(e) => handleInputChange('buyPrice', Number(e.target.value))}
                className="flex-1 text-center"
              />
              <div className="flex gap-1">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('buyPrice', (formData.buyPrice || 0) * 1.001)}
                  className="px-2 text-green-600 dark:text-green-500 hover:text-green-700 dark:hover:text-green-600"
                >
                  +0.1%
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('buyPrice', (formData.buyPrice || 0) * 1.005)}
                  className="px-2 text-green-600 dark:text-green-500 hover:text-green-700 dark:hover:text-green-600"
                >
                  +0.5%
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('buyPrice', (formData.buyPrice || 0) * 1.01)}
                  className="px-2 text-green-600 dark:text-green-500 hover:text-green-700 dark:hover:text-green-600"
                >
                  +1%
                </Button>
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="sellPrice">Sell Price</Label>
            <div className="flex items-center gap-2">
              <div className="flex gap-1">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('sellPrice', Math.max(0, (formData.sellPrice || 0) * 0.99))}
                  className="px-2 text-red-600 dark:text-red-500 hover:text-red-700 dark:hover:text-red-600"
                >
                  -1%
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('sellPrice', Math.max(0, (formData.sellPrice || 0) * 0.995))}
                  className="px-2 text-red-600 dark:text-red-500 hover:text-red-700 dark:hover:text-red-600"
                >
                  -0.5%
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('sellPrice', Math.max(0, (formData.sellPrice || 0) * 0.999))}
                  className="px-2 text-red-600 dark:text-red-500 hover:text-red-700 dark:hover:text-red-600"
                >
                  -0.1%
                </Button>
              </div>
              <Input
                id="sellPrice"
                type="number"
                step={decimalPlaces > 0 ? Math.pow(10, -decimalPlaces).toFixed(decimalPlaces) : '1'}
                placeholder="Enter sell price"
                value={formData.sellPrice || ''}
                onChange={(e) => handleInputChange('sellPrice', Number(e.target.value))}
                className="flex-1 text-center"
              />
              <div className="flex gap-1">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('sellPrice', (formData.sellPrice || 0) * 1.001)}
                  className="px-2 text-green-600 dark:text-green-500 hover:text-green-700 dark:hover:text-green-600"
                >
                  +0.1%
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('sellPrice', (formData.sellPrice || 0) * 1.005)}
                  className="px-2 text-green-600 dark:text-green-500 hover:text-green-700 dark:hover:text-green-600"
                >
                  +0.5%
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange('sellPrice', (formData.sellPrice || 0) * 1.01)}
                  className="px-2 text-green-600 dark:text-green-500 hover:text-green-700 dark:hover:text-green-600"
                >
                  +1%
                </Button>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="trailing">Trailing % (Optional)</Label>
              <Select
                value={formData.trailingPercent?.toString() || 'none'}
                onValueChange={(value) => handleInputChange('trailingPercent', value === 'none' ? undefined : Number(value))}
              >
                <SelectTrigger id="trailing">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {TRAILING_PERCENTAGES.map((trail) => (
                    <SelectItem key={trail.value.toString()} value={trail.value.toString()}>
                      {trail.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="leverage">Leverage</Label>
              <Select
                value={formData.leverage?.toString() || '3'}
                onValueChange={(value) => handleInputChange('leverage', Number(value))}
              >
                <SelectTrigger id="leverage">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {LEVERAGE_OPTIONS.map((lev) => (
                    <SelectItem key={lev.value.toString()} value={lev.value.toString()}>
                      {lev.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="infiniteLoop"
              checked={formData.infiniteLoop}
              onCheckedChange={(checked) => handleInputChange('infiniteLoop', checked)}
            />
            <Label htmlFor="infiniteLoop" className="font-normal cursor-pointer">
              Enable infinite loop
            </Label>
          </div>

          {validationErrors.length > 0 && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                <ul className="list-disc list-inside space-y-1">
                  {validationErrors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </AlertDescription>
            </Alert>
          )}

          <div className="flex gap-2">
            <Button type="submit" className="flex-1 bg-green-600 hover:bg-green-700">
              <Rocket className="mr-2 h-4 w-4" />
              {editingBotId ? 'Update Bot' : 'Start Bot'}
            </Button>
            {editingBotId && (
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setEditingBot(null);
                  setFormData({
                    ticker: POPULAR_TICKERS[0] || '',
                    exchange: 'CoinDCX F',
                    firstOrder: 'BUY',
                    quantity: 1,
                    customQuantity: undefined,
                    buyPrice: 0,
                    sellPrice: 0,
                    trailingPercent: undefined,
                    leverage: 3,
                    infiniteLoop: true,
                  });
                }}
              >
                Cancel
              </Button>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  );
};
