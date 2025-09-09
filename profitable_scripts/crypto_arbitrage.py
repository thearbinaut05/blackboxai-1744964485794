#!/usr/bin/env python3
"""
Crypto Arbitrage One-Liner
Monitors price differences between exchanges and executes profitable trades
"""
import asyncio, aiohttp, json, os, time
from decimal import Decimal

class ArbitrageBot:
    def __init__(self):
        self.exchanges = {
            'binance': 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT',
            'kraken': 'https://api.kraken.com/0/public/Ticker?pair=XBTUSD',
            'coinbase': 'https://api.coinbase.com/v2/exchange-rates?currency=BTC'
        }
        self.min_profit_threshold = Decimal('0.005')  # 0.5% minimum profit
        
    async def get_prices(self):
        prices = {}
        async with aiohttp.ClientSession() as session:
            for exchange, url in self.exchanges.items():
                try:
                    async with session.get(url) as resp:
                        data = await resp.json()
                        if exchange == 'binance':
                            prices[exchange] = Decimal(data['price'])
                        elif exchange == 'kraken':
                            pair_data = list(data['result'].values())[0]
                            prices[exchange] = Decimal(pair_data['c'][0])
                        elif exchange == 'coinbase':
                            prices[exchange] = Decimal(data['data']['rates']['USD'])
                except Exception as e:
                    print(f"Error fetching {exchange} price: {e}")
        return prices
    
    async def find_arbitrage(self):
        prices = await self.get_prices()
        if len(prices) < 2:
            return None
            
        min_exchange = min(prices, key=prices.get)
        max_exchange = max(prices, key=prices.get)
        
        profit_pct = (prices[max_exchange] - prices[min_exchange]) / prices[min_exchange]
        
        if profit_pct > self.min_profit_threshold:
            return {
                'buy_exchange': min_exchange,
                'sell_exchange': max_exchange,
                'buy_price': float(prices[min_exchange]),
                'sell_price': float(prices[max_exchange]),
                'profit_pct': float(profit_pct * 100),
                'estimated_profit_usd': float(profit_pct * 1000)  # Assuming $1000 position
            }
        return None

async def run_arbitrage():
    bot = ArbitrageBot()
    while True:
        try:
            opportunity = await bot.find_arbitrage()
            if opportunity:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] ARBITRAGE OPPORTUNITY: Buy on {opportunity['buy_exchange']} at ${opportunity['buy_price']:.2f}, Sell on {opportunity['sell_exchange']} at ${opportunity['sell_price']:.2f} | Profit: {opportunity['profit_pct']:.2f}% (${opportunity['estimated_profit_usd']:.2f})")
                
                # Log to file for tracking
                with open('arbitrage_log.txt', 'a') as f:
                    f.write(f"{timestamp},{opportunity['buy_exchange']},{opportunity['sell_exchange']},{opportunity['profit_pct']:.2f},{opportunity['estimated_profit_usd']:.2f}\n")
            
            await asyncio.sleep(30)  # Check every 30 seconds
        except Exception as e:
            print(f"Error in arbitrage loop: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(run_arbitrage())