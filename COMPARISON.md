# Comparison: Original vs POST_ONLY Fork

## Quick Comparison Table

| Feature | Original `bitfinex-api-py` | `bitfinex-api-py-postonly` |
|---------|---------------------------|----------------------------|
| **POST_ONLY default** | ❌ No | ✅ Yes (forced) |
| **Can place market orders** | ✅ Yes | ❌ No |
| **Can cross spread** | ✅ Yes | ❌ No |
| **Taker orders possible** | ✅ Yes | ❌ No |
| **Requires flag management** | ✅ Yes | ❌ No (automatic) |
| **Risk of accidental market orders** | ⚠️ High | ✅ Zero |
| **API compatibility** | - | 💯 100% |
| **Drop-in replacement** | - | ✅ Yes |
| **Safety enforcement** | Manual | Automatic |
| **Heartbeat events** | ❌ No | ✅ Yes |

## Code Comparison

### Placing a Safe Order

#### Original (Manual Safety)
```python
from bfxapi import Client

client = Client(api_key="...", api_secret="...")

# Must remember POST_ONLY flag value (4096)
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=0.01,
    price=50000,
    flags=4096  # ⚠️ Easy to forget!
)

# Forgot flag? Order might execute as taker!
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=0.01,
    price=50000
    # 💥 NO FLAGS = RISKY!
)
```

#### This Fork (Automatic Safety)
```python
from bfxapi import Client

client = Client(api_key="...", api_secret="...")

# POST_ONLY always enforced
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=0.01,
    price=50000
    # ✅ POST_ONLY added automatically!
)

# Even with flags=0, still safe
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=0.01,
    price=50000,
    flags=0  # ✅ Becomes 4096 internally!
)
```

## Behavioral Differences

### Scenario 1: Order at Current Market Price

**Original Behavior:**
- Order executes immediately as taker
- Pay 0.2% taker fee
- Immediate fill

**Fork Behavior:**
- Order rejected if would cross spread
- Placed on book as maker
- Earn potential maker rebate (-0.1%)

### Scenario 2: Volatile Market Conditions

**Original Behavior:**
```python
# During a spike to $100,000
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=1.0,
    price=55000  # You think price is still 50k
)
# Result: IMMEDIATE MARKET BUY at any price up to $55k!
```

**Fork Behavior:**
```python
# During a spike to $100,000
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=1.0,
    price=55000
)
# Result: Order sits on book at $55k (won't chase price)
```

### Scenario 3: Fat Finger Protection

**Original Behavior:**
```python
# Meant $50,000, typed $500,000
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=1.0,
    price=500000  # Extra zero!
)
# Result: INSTANT MARKET BUY! 💸
```

**Fork Behavior:**
```python
# Meant $50,000, typed $500,000
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=1.0,
    price=500000
)
# Result: Order sits safely on book at $500k (no execution)
```

## Fee Comparison

### Monthly Trading: 100 BTC @ $50,000

**Using Original:**
- 50% maker, 50% taker (typical)
- Taker fees (50 BTC): $5,000 cost
- Maker fees (50 BTC): $2,500 earned
- **Net cost: $2,500/month**

**Using Fork:**
- 100% maker (enforced)
- Maker fees (100 BTC): $5,000 earned
- **Net earnings: $5,000/month**

**Difference: $7,500/month saved!**

## Migration Guide

### Package Installation

```bash
# Uninstall original
pip uninstall bitfinex-api-py

# Install fork
pip install bitfinex-api-py-postonly
```

### Code Changes Required

**None!** The fork is a drop-in replacement. All your existing code works exactly the same, just safer.

### Testing the Difference

```python
# Test script to verify POST_ONLY enforcement
from bfxapi import Client

client = Client(api_key="...", api_secret="...")

# Try to place without flags
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=0.001,
    price=1  # Very low price
)

# Original: Would execute as taker if any asks exist
# Fork: Will be placed on book at $1 (POST_ONLY enforced)
print(f"Order flags: {order.flags}")  # Fork always shows 4096
```

## When to Use Which

### Use Original `bitfinex-api-py` When:
- ✅ You need market orders
- ✅ You need immediate execution
- ✅ You're implementing stop-losses
- ✅ You want full control over order flags

### Use `bitfinex-api-py-postonly` When:
- ✅ You never want taker fees
- ✅ You run unattended bots
- ✅ You value safety over execution speed
- ✅ You're market making
- ✅ You want protection from mistakes

## Technical Implementation

The fork adds enforcement at 4 layers:
1. REST API endpoints
2. WebSocket messages
3. Middleware layer
4. Input validation

This redundancy ensures no code path can bypass POST_ONLY enforcement.

## Support and Issues

- **Original Issues**: https://github.com/bitfinexcom/bitfinex-api-py/issues
- **Fork Issues**: https://github.com/0xferit/bitfinex-api-py/issues

Choose based on your needs - both are production-ready!