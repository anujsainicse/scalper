'use client';

import React, { useState } from 'react';
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
import { Rocket, AlertCircle } from 'lucide-react';
import { useBotStore } from '@/store/botStore';
import { Exchange, OrderSide, BotFormData } from '@/types/bot';
import { validateTicker } from '@/utils/formatters';
import { EXCHANGES, QUANTITIES, TRAILING_PERCENTAGES, POPULAR_TICKERS } from '@/config/bot-config';

export const BotConfiguration: React.FC = () => {
  const addBot = useBotStore((state) => state.addBot);
  const updateBotFromForm = useBotStore((state) => state.updateBotFromForm);
  const setEditingBot = useBotStore((state) => state.setEditingBot);
  const editingBotId = useBotStore((state) => state.editingBotId);
  const bots = useBotStore((state) => state.bots);
  const addLog = useBotStore((state) => state.addLog);

  const [formData, setFormData] = useState<BotFormData>({
    ticker: '',
    exchange: 'CoinDCX F',
    firstOrder: 'BUY',
    quantity: 1,
    customQuantity: undefined,
    buyPrice: 0,
    sellPrice: 0,
    trailingPercent: undefined,
    infiniteLoop: false,
  });

  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [showCustomQuantity, setShowCustomQuantity] = useState(false);

  // Load bot data when editing
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
          infiniteLoop: bot.infiniteLoop,
        });
        setShowCustomQuantity(false);
      }
    }
  }, [editingBotId, bots]);

  const handleInputChange = (
    field: keyof BotFormData,
    value: string | number | boolean
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear errors when user starts typing
    if (validationErrors.length > 0) {
      setValidationErrors([]);
    }
  };

  const handleQuantityChange = (value: string) => {
    const numValue = Number(value);
    if (numValue === 0) {
      setShowCustomQuantity(true);
      setFormData((prev) => ({ ...prev, quantity: 0 }));
    } else {
      setShowCustomQuantity(false);
      setFormData((prev) => ({ ...prev, quantity: numValue, customQuantity: undefined }));
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
    if (showCustomQuantity && (!formData.customQuantity || formData.customQuantity <= 0)) {
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

  const handleSubmit = (e: React.FormEvent) => {
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

    if (editingBotId) {
      // Update existing bot
      updateBotFromForm(editingBotId, formattedData);
      const toastId = toast.success(`Bot updated for ${formattedData.ticker}`, {
        onClick: () => toast.dismiss(toastId),
        style: { cursor: 'pointer' },
      });
      addLog('INFO', `Bot updated successfully for ${formattedData.ticker}`);
    } else {
      // Create new bot
      addBot(formattedData);
      const toastId = toast.success(`Bot created for ${formattedData.ticker}`, {
        onClick: () => toast.dismiss(toastId),
        style: { cursor: 'pointer' },
      });
      addLog('SUCCESS', `Bot configured successfully for ${formattedData.ticker}`);
    }

    // Reset form
    setFormData({
      ticker: '',
      exchange: 'CoinDCX F',
      firstOrder: 'BUY',
      quantity: 1,
      customQuantity: undefined,
      buyPrice: 0,
      sellPrice: 0,
      trailingPercent: undefined,
      infiniteLoop: false,
    });
    setShowCustomQuantity(false);
    setEditingBot(null);
  };

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Bot Configuration</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
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

          <div className="space-y-2">
            <Label htmlFor="quantity">Quantity</Label>
            <Select
              value={formData.quantity.toString()}
              onValueChange={handleQuantityChange}
            >
              <SelectTrigger id="quantity">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {QUANTITIES.map((qty) => (
                  <SelectItem key={qty.value.toString()} value={qty.value.toString()}>
                    {qty.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {showCustomQuantity && (
            <div className="space-y-2">
              <Label htmlFor="customQuantity">Custom Quantity</Label>
              <Input
                id="customQuantity"
                type="number"
                step="0.01"
                placeholder="Enter custom quantity"
                value={formData.customQuantity || ''}
                onChange={(e) => handleInputChange('customQuantity', Number(e.target.value))}
              />
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="buyPrice">Buy Price</Label>
            <Input
              id="buyPrice"
              type="number"
              step="0.01"
              placeholder="Enter buy price"
              value={formData.buyPrice || ''}
              onChange={(e) => handleInputChange('buyPrice', Number(e.target.value))}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="sellPrice">Sell Price</Label>
            <Input
              id="sellPrice"
              type="number"
              step="0.01"
              placeholder="Enter sell price"
              value={formData.sellPrice || ''}
              onChange={(e) => handleInputChange('sellPrice', Number(e.target.value))}
            />
          </div>

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
                    ticker: '',
                    exchange: 'CoinDCX F',
                    firstOrder: 'BUY',
                    quantity: 1,
                    customQuantity: undefined,
                    buyPrice: 0,
                    sellPrice: 0,
                    trailingPercent: undefined,
                    infiniteLoop: false,
                  });
                  setShowCustomQuantity(false);
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
