# When You Need bitfinex-api-py-postonly

## Perfect Use Cases

### 1. Market Making Bots
**Scenario**: You run a market making bot providing liquidity on both sides
**Risk**: Accidentally taking liquidity and paying fees
**Solution**: This package ensures all your orders are maker orders

```python
# Your market maker always posts orders, never takes
async def place_bid_ask():
    # Both orders guaranteed to be POST_ONLY
    await client.rest.auth.submit_order(
        type="EXCHANGE LIMIT",
        symbol="tBTCUSD",
        amount=0.1,
        price=current_bid - spread
    )
    await client.rest.auth.submit_order(
        type="EXCHANGE LIMIT",
        symbol="tBTCUSD",
        amount=-0.1,
        price=current_ask + spread
    )
```

### 2. Grid Trading Bots
**Scenario**: You have a grid of buy/sell orders at different price levels
**Risk**: During volatility, orders might execute immediately as takers
**Solution**: All grid orders stay on the book until price comes to them

```python
# Grid bot that never market buys/sells
def setup_grid(base_price, grid_size, spacing):
    for i in range(grid_size):
        buy_price = base_price - (spacing * i)
        sell_price = base_price + (spacing * i)
        
        # All orders POST_ONLY - won't execute immediately
        client.rest.auth.submit_order(
            type="EXCHANGE LIMIT",
            symbol="tBTCUSD",
            amount=0.01,
            price=buy_price
        )
```

### 3. DCA (Dollar Cost Averaging) Bots
**Scenario**: You want to accumulate at specific price levels
**Risk**: Market buying at unfavorable prices during spikes
**Solution**: Orders only fill when price comes down to your levels

```python
# DCA bot that only buys at target prices
def place_dca_orders(target_prices):
    for price in target_prices:
        # Will wait for price to come to you
        client.rest.auth.submit_order(
            type="EXCHANGE LIMIT",
            symbol="tBTCUSD",
            amount=0.01,
            price=price
        )
```

### 4. Arbitrage Systems
**Scenario**: You need precise control over execution prices
**Risk**: Slippage from market orders ruins profitability
**Solution**: Orders execute only at your exact prices

### 5. High-Frequency Trading
**Scenario**: You place/cancel many orders per second
**Risk**: Latency causes orders to cross spread accidentally
**Solution**: POST_ONLY prevents any accidental executions

## Real-World Problems Solved

### "I accidentally market bought the top"
```python
# IMPOSSIBLE with this package
# Even if you try to place at current price, it won't cross
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=1.0,
    price=99999  # Won't execute if spread is below this
)
```

### "My bot paid $1000 in taker fees last month"
```python
# This package ensures you ONLY pay maker fees (or earn rebates)
# Maker fee: -0.1% (rebate)
# Taker fee: 0.2% (cost)
# Difference: 0.3% per trade!
```

### "During the flash crash, my orders executed at terrible prices"
```python
# With POST_ONLY enforcement, your orders would have been rejected
# instead of executing at spike prices
```

### "I meant to place at 50,000 but typed 500,000"
```python
# Original API: Instant market buy at any price
# This package: Order sits on book at 500,000 (won't execute)
```

## Who Should Use This

✅ **SHOULD USE**:
- Market makers
- Grid traders
- DCA strategists
- Arbitrage bots
- Anyone who wants to avoid taker fees
- Safety-conscious traders
- Bots running unattended

❌ **SHOULD NOT USE**:
- Traders who need market orders
- Strategies requiring immediate execution
- Stop-loss systems (need market orders)
- Momentum trading bots

## Migration Example

### Before (Risky)
```python
# Risk: Forgetting POST_ONLY flag
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=0.1,
    price=50000
    # OOPS! Forgot flags=4096, might execute as taker
)
```

### After (Safe)
```python
# No risk: POST_ONLY always enforced
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=0.1,
    price=50000
    # POST_ONLY automatically added
)
```

## Cost Savings Example

Trading volume: 100 BTC/month @ $50,000
- Taker fees (0.2%): $10,000/month cost
- Maker fees (-0.1%): $5,000/month EARNED
- **Difference: $15,000/month**

This package ensures you're always on the maker side!