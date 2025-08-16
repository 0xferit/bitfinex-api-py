# bitfinex-api-py-postonly

[![Safety Fork](https://img.shields.io/badge/Fork-Safety%20Enhanced-green)](https://github.com/0xferit/bitfinex-api-py)
[![POST_ONLY Enforced](https://img.shields.io/badge/Orders-POST__ONLY%20Enforced-blue)](https://github.com/0xferit/bitfinex-api-py)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org)

**Safety fork of Bitfinex Python API that forces all orders to be POST_ONLY (maker-only), preventing accidental taker/market orders.**

## What This Changes

1. **Forces POST_ONLY flag (4096) on ALL orders** - Cannot be disabled
2. **Rejects MARKET orders** - Throws ValueError with clear message  
3. **Adds WebSocket heartbeat events** - Monitor connection health

## Installation

```bash
pip install bitfinex-api-py-postonly
```

## Key Differences

| Feature | Original | This Fork |
|---------|----------|-----------|
| **POST_ONLY default** | ❌ No | ✅ Forced |
| **Market orders** | ✅ Allowed | ❌ Rejected |
| **Can cross spread** | ✅ Yes | ❌ No |
| **Taker fees possible** | ✅ Yes | ❌ No |
| **Heartbeat events** | ❌ No | ✅ Yes |

## Example

### Original (Manual POST_ONLY)
```python
# Must remember flag 4096 or risk taker execution
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=0.01,
    price=50000,
    flags=4096  # ⚠️ Easy to forget!
)
```

### This Fork (Automatic POST_ONLY)
```python
# POST_ONLY always enforced, even with flags=0
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=0.01,
    price=50000
    # ✅ POST_ONLY added automatically
)

# Market orders rejected
try:
    order = client.rest.auth.submit_order(type="MARKET", ...)
except ValueError:
    # "Order type 'MARKET' is incompatible with POST_ONLY enforcement"
```

## Use Cases

**✅ Perfect for:** Market makers, grid trading, DCA bots, arbitrage systems

**❌ Not for:** Stop-losses, momentum trading, strategies needing immediate execution

## Migration

```bash
pip uninstall bitfinex-api-py
pip install bitfinex-api-py-postonly
```

No code changes needed for limit order strategies.

## Important Notes

- **Funding offers** not affected (no POST_ONLY flag)
- **Other flags** preserved (HIDDEN, REDUCE_ONLY work normally)
- **No bypass** - POST_ONLY enforcement cannot be disabled
- **4-layer enforcement** - REST, WebSocket, middleware, and client levels

## Links

- **Fork**: https://github.com/0xferit/bitfinex-api-py
- **Original**: https://github.com/bitfinexcom/bitfinex-api-py
- **PyPI**: https://pypi.org/project/bitfinex-api-py-postonly/

## License

Apache 2.0 (same as original)