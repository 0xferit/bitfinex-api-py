# How to Find and Use bitfinex-api-py-postonly

## Search Terms This Package Addresses

If you're searching for any of these, this package is for you:

- "bitfinex python force post only"
- "bitfinex api maker only orders"
- "prevent market orders bitfinex python"
- "bitfinex POST_ONLY flag python"
- "bitfinex no taker fees python"
- "bitfinex api safety wrapper"
- "how to avoid taker fees bitfinex"
- "bitfinex python api accidental market order"
- "ensure maker orders bitfinex"
- "bitfinex grid bot post only"
- "bitfinex market maker python"
- "bitfinex order won't cross spread"

## Problems This Package Solves

### 1. Accidental Market Orders
**Problem**: Your bot places a market order during high volatility
**Solution**: This package makes market orders impossible

### 2. Crossing the Spread
**Problem**: Your limit order immediately executes as a taker
**Solution**: All orders have POST_ONLY flag, won't cross spread

### 3. Taker Fees
**Problem**: Paying 0.2% taker fees instead of earning maker rebates
**Solution**: All orders are maker-only, eligible for rebates

### 4. Fat Finger Mistakes
**Problem**: Typo causes immediate execution at bad price
**Solution**: Orders always go to order book first

## Installation

### Quick Install (PyPI)
```bash
pip install bitfinex-api-py-postonly
```

### Install from GitHub
```bash
pip install git+https://github.com/0xferit/bitfinex-api-py.git
```

### Install Specific Version
```bash
pip install https://github.com/0xferit/bitfinex-api-py/releases/download/v3.0.5.post1/bitfinex_api_py_postonly-3.0.5.post1-py3-none-any.whl
```

## Migration from Original API

```python
# Before (original bitfinex-api-py)
from bfxapi import Client
client = Client(api_key="...", api_secret="...")
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=0.01,
    price=50000,
    flags=4096  # Had to remember POST_ONLY flag
)

# After (bitfinex-api-py-postonly)
from bfxapi import Client
client = Client(api_key="...", api_secret="...")
order = client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=0.01,
    price=50000
    # POST_ONLY automatically added!
)
```

## Keywords for Search Engines

bitfinex, python, api, post-only, maker-only, no-taker, safety, trading, cryptocurrency, bitcoin, limit-order, market-maker, grid-trading, dca, arbitrage, algo-trading, automated-trading, order-book, maker-rebate, taker-fee, spread, post_only, flag-4096

## Related Projects

- Original: [bitfinex-api-py](https://github.com/bitfinexcom/bitfinex-api-py)
- This Fork: [bitfinex-api-py-postonly](https://github.com/0xferit/bitfinex-api-py)

## Community

Found this useful? Star the repository to help others discover it!