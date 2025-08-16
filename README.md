# bitfinex-api-py-postonly

[![Safety Fork](https://img.shields.io/badge/Fork-Safety%20Enhanced-green)](https://github.com/0xferit/bitfinex-api-py)
[![POST_ONLY Enforced](https://img.shields.io/badge/Orders-POST__ONLY%20Enforced-blue)](https://github.com/0xferit/bitfinex-api-py)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org)

**A safety-enhanced fork of the official Bitfinex Python API that prevents accidental market/taker orders.**

## ⚠️ CRITICAL: What This Fork Changes

This fork modifies the official Bitfinex Python API to:

1. **Force POST_ONLY flag on ALL orders** - Cannot be disabled
2. **Reject MARKET orders** - Throws clear error message
3. **Expose WebSocket heartbeat events** - Monitor connection health

## Installation

```bash
pip install bitfinex-api-py-postonly
```

## What's Different From Original

### 1. All Orders Are Post-Only (Maker-Only)

```python
from bfxapi import Client

client = Client(api_key="...", api_secret="...")

# POST_ONLY flag (4096) is automatically added
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=0.01,
    price=50000
    # No flags needed - POST_ONLY is forced
)

# Even if you try flags=0, POST_ONLY is still added
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=0.01,
    price=50000,
    flags=0  # Still becomes 4096 internally
)
```

### 2. Market Orders Are Rejected

```python
# This will raise ValueError
try:
    order = client.rest.auth.submit_order(
        type="MARKET",  # or "EXCHANGE MARKET"
        symbol="tBTCUSD",
        amount=0.01
    )
except ValueError as e:
    print(e)  # "Order type 'MARKET' is incompatible with POST_ONLY enforcement"
```

### 3. WebSocket Heartbeat Events

```python
@client.wss.on("heartbeat")
def on_heartbeat(subscription):
    if subscription:
        print(f"Channel {subscription['channel']} is alive")
    else:
        print("Authenticated connection heartbeat")
```

## Use Cases

### ✅ Perfect For

**Market Making Bots**
```python
# All orders guaranteed to be maker orders
async def place_bid_ask():
    # Both orders will be POST_ONLY, earning maker rebates
    await client.rest.auth.submit_order(
        type="EXCHANGE LIMIT",
        symbol="tBTCUSD",
        amount=0.1,
        price=current_bid - spread
    )
```

**Grid Trading**
```python
# Grid orders won't execute immediately during volatility
for level in grid_levels:
    client.rest.auth.submit_order(
        type="EXCHANGE LIMIT",
        symbol="tBTCUSD",
        amount=0.01,
        price=level
        # POST_ONLY prevents crossing spread
    )
```

**DCA Strategies**
```python
# Buy orders only fill when price comes to you
for price in target_prices:
    client.rest.auth.submit_order(
        type="EXCHANGE LIMIT",
        symbol="tBTCUSD",
        amount=0.01,
        price=price
        # Won't market buy during spikes
    )
```

### ❌ NOT Suitable For

- Strategies requiring market orders
- Stop-loss implementations
- Immediate execution needs
- Momentum trading

## Technical Implementation

### Enforcement Layers

1. **REST API** (`rest_auth_endpoints.py`)
   - `submit_order()` - Line 106: Validates order type and adds POST_ONLY
   - `update_order()` - Line 146: Adds POST_ONLY

2. **Middleware** (`middleware.py`)
   - Lines 71-77: Catches all order endpoints
   - Validates order type for submissions
   - Includes maintenance notes for new endpoints

3. **WebSocket** (`bfx_websocket_inputs.py`)
   - `submit_order()` - Line 32: Validates and enforces
   - `update_order()` - Line 71: Enforces POST_ONLY

4. **WebSocket Client** (`bfx_websocket_client.py`)
   - Lines 213-220: Final enforcement layer

### Core Safety Function

```python
def enforce_post_only(flags: Optional[int], order_type: Optional[str] = None) -> int:
    """
    Ensure POST_ONLY flag is set, preserving other flags.
    Validates order type compatibility.
    """
    if order_type and 'MARKET' in order_type.upper():
        raise ValueError(
            f"Order type '{order_type}' is incompatible with POST_ONLY enforcement. "
            "POST_ONLY only works with limit-style orders."
        )
    return POST_ONLY | (flags if flags is not None else 0)
```

## Fee Impact

### Monthly Trading: 100 BTC @ $50,000

**Original API:**
- 50% taker orders: -$5,000 in fees
- 50% maker orders: +$2,500 rebate
- **Net: -$2,500/month cost**

**This Fork:**
- 100% maker orders: +$5,000 rebate
- **Net: +$5,000/month earned**

**Difference: $7,500/month saved**

## Comparison With Original

| Feature | Original `bitfinex-api-py` | This Fork |
|---------|---------------------------|-----------|
| **POST_ONLY default** | ❌ No | ✅ Yes (forced) |
| **Can place market orders** | ✅ Yes | ❌ No (rejected) |
| **Can cross spread** | ✅ Yes | ❌ No |
| **Taker orders possible** | ✅ Yes | ❌ No |
| **Risk of accidental market orders** | ⚠️ High | ✅ Zero |
| **API compatibility** | - | 💯 100% |
| **Heartbeat events** | ❌ No | ✅ Yes |

### Original API (Manual Safety)
```python
# Must remember POST_ONLY flag (4096)
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD", 
    amount=0.01,
    price=50000,
    flags=4096  # ⚠️ Easy to forget!
)
```

### This Fork (Automatic Safety)
```python
# POST_ONLY always enforced
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=0.01,
    price=50000
    # ✅ POST_ONLY added automatically
)
```

## Migration From Original

No code changes needed - it's a drop-in replacement:

```bash
# Uninstall original
pip uninstall bitfinex-api-py

# Install fork
pip install bitfinex-api-py-postonly
```

Your existing code continues to work, just safer.

## Important Notes

- **Funding offers** are NOT affected (no POST_ONLY flag)
- **All order types** must be limit-style (LIMIT, EXCHANGE LIMIT, etc.)
- **Flag preservation**: Other flags (HIDDEN, REDUCE_ONLY) are preserved
- **No bypass**: There is no way to disable POST_ONLY enforcement

## Repository

- **Fork**: https://github.com/0xferit/bitfinex-api-py
- **Original**: https://github.com/bitfinexcom/bitfinex-api-py
- **PyPI**: https://pypi.org/project/bitfinex-api-py-postonly/

## License

Apache 2.0 - Same as original

## Problems This Package Solves

- **Accidental Market Orders**: Makes market orders impossible (raises ValueError)
- **Crossing the Spread**: POST_ONLY flag prevents immediate taker execution
- **Taker Fees**: All orders are maker-only, eligible for rebates instead of fees
- **Fat Finger Mistakes**: Orders always go to order book first, won't execute at wrong price

## Discovery Keywords

If you're searching for: bitfinex python force post only, bitfinex api maker only orders, prevent market orders bitfinex python, bitfinex POST_ONLY flag python, bitfinex no taker fees python, bitfinex api safety wrapper, avoid taker fees bitfinex, bitfinex python api accidental market order, ensure maker orders bitfinex, bitfinex grid bot post only, bitfinex market maker python, bitfinex order won't cross spread

## Changes Summary

- Added `bfxapi/_utils/post_only_enforcement.py` (37 lines)
- Added `bfxapi/constants/order_flags.py` (6 lines)  
- Modified 4 files to enforce POST_ONLY (~50 lines total)
- Added comprehensive tests (240+ lines, 13 tests)
- No external dependencies added