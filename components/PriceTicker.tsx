'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import { cn } from '@/lib/utils'

interface CryptoPrice {
  symbol: string
  price: number | null
  previousPrice?: number | null
  decimals: number
}

const CRYPTO_CONFIG: CryptoPrice[] = [
  { symbol: 'BTC', price: null, decimals: 0 },
  { symbol: 'ETH', price: null, decimals: 0 },
  { symbol: 'SOL', price: null, decimals: 2 },
  { symbol: 'BNB', price: null, decimals: 2 },
  { symbol: 'DOGE', price: null, decimals: 4 },
]

const REFRESH_INTERVAL = 5000 // 5 seconds

export const PriceTicker: React.FC = () => {
  const [cryptoPrices, setCryptoPrices] = useState<CryptoPrice[]>(CRYPTO_CONFIG)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchPrices = async () => {
    try {
      const symbols = CRYPTO_CONFIG.map(c => c.symbol)
      const response = await api.getMultiplePrices(symbols, 'Bybit')

      if (response.success) {
        setCryptoPrices(prevPrices =>
          prevPrices.map(crypto => {
            const priceData = response.prices[crypto.symbol]
            const newPrice = priceData?.price

            return {
              ...crypto,
              previousPrice: crypto.price,
              price: newPrice,
            }
          })
        )
        setError(null)
      } else {
        setError('Failed to fetch prices')
      }
    } catch (err) {
      console.error('Error fetching crypto prices:', err)
      setError('Unable to fetch prices')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // Initial fetch
    fetchPrices()

    // Set up interval for auto-refresh
    const interval = setInterval(fetchPrices, REFRESH_INTERVAL)

    // Cleanup
    return () => clearInterval(interval)
  }, [])

  const formatPrice = (price: number | null, decimals: number): string => {
    if (price === null) return '--'
    return price.toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    })
  }

  const getPriceChangeColor = (current: number | null, previous: number | null): string => {
    if (!current || !previous) return ''
    if (current > previous) return 'text-green-500'
    if (current < previous) return 'text-red-500'
    return ''
  }

  if (error && !loading) {
    return null // Silently fail - don't show error in header
  }

  return (
    <div className="flex items-center gap-2 px-4">
      {cryptoPrices.map((crypto, index) => {
        const priceChangeColor = getPriceChangeColor(crypto.price, crypto.previousPrice)
        const isLoading = loading && crypto.price === null

        return (
          <div
            key={crypto.symbol}
            className={cn(
              'flex flex-col items-center px-3 py-1 rounded-md transition-all duration-200',
              'hover:bg-accent/50',
              index < cryptoPrices.length - 1 && 'border-r border-border/50'
            )}
          >
            {/* Symbol */}
            <span className="text-xs font-medium text-muted-foreground">
              {crypto.symbol}
            </span>

            {/* Price */}
            {isLoading ? (
              <div className="h-5 w-16 bg-muted animate-pulse rounded mt-0.5" />
            ) : (
              <span
                className={cn(
                  'text-sm font-semibold transition-colors duration-300',
                  priceChangeColor || 'text-foreground'
                )}
              >
                ${formatPrice(crypto.price, crypto.decimals)}
              </span>
            )}
          </div>
        )
      })}

      {/* Hidden on mobile - show only BTC, ETH, SOL */}
      <style jsx>{`
        @media (max-width: 768px) {
          .flex.items-center.gap-2 > div:nth-child(n+4) {
            display: none;
          }
        }
      `}</style>
    </div>
  )
}
