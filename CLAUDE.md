# Bitfinex API Python Fork - Safety Features

## Purpose
This fork adds two safety features to prevent accidental market orders and monitor connection health.

## Feature 1: Post-Only Order Enforcement
**Status:** ACTIVE  
**Protection:** ALL orders automatically become post-only (maker-only)

### How It Works
- Flag 4096 (POST_ONLY) is automatically added to every order
- Cannot be disabled or bypassed
- Funding offers are not affected

### Enforcement Points
1. **REST API**: `submit_order()` and `update_order()` in `rest_auth_endpoints.py`
2. **Middleware**: All `order/submit` and `order/update` endpoints in `middleware.py`
3. **WebSocket**: Input validation in `bfx_websocket_inputs.py` and client-level in `bfx_websocket_client.py`

## Feature 2: Heartbeat Events
**Status:** ACTIVE  
**Purpose:** Monitor WebSocket connection health

### Usage
```python
from bfxapi import Client

bfx = Client(api_key="...", api_secret="...")

@bfx.wss.on("heartbeat")
def on_heartbeat(subscription):
    if subscription:
        print(f"Public channel heartbeat: {subscription['channel']}")
    else:
        print("Authenticated connection heartbeat")

bfx.wss.run()
```

## Implementation Details

### Post-Only Enforcement - Technical Implementation

**Core Function** (`bfxapi/_utils/post_only_enforcement.py`):
```python
def enforce_post_only(flags: Optional[int], order_type: Optional[str] = None) -> int:
    """
    Ensure POST_ONLY flag is set, preserving other flags.
    Validates that order type is compatible with POST_ONLY.
    
    Raises ValueError if order type contains 'MARKET' (incompatible with POST_ONLY).
    """
    if order_type and 'MARKET' in order_type.upper():
        raise ValueError(
            f"Order type '{order_type}' is incompatible with POST_ONLY enforcement. "
            "POST_ONLY only works with limit-style orders."
        )
    return POST_ONLY | (flags if flags is not None else 0)
```

**Hardening Features:**
- Rejects MARKET orders with clear error message
- Case-insensitive order type validation
- Preserves all existing flags using bitwise OR

**Layer 1 - REST API** (`rest_auth_endpoints.py`):
- Line 106: `flags = enforce_post_only(flags, order_type=type)` in `submit_order()` - validates order type
- Line 146: `flags = enforce_post_only(flags)` in `update_order()` - no type validation needed
- Funding offers explicitly skip enforcement (no flags sent)

**Layer 2 - Middleware** (`middleware.py`):
- Lines 66-77: Intercepts all `order/submit` and `order/update` endpoints
- Line 73: `enforce_post_only(flags, order_type)` for submit - validates order type
- Line 77: `enforce_post_only(flags)` for update
- Includes maintenance note for endpoint pattern updates
- Catch-all protection layer

**Layer 3 - WebSocket Input** (`bfx_websocket_inputs.py`):
- Line 32: `enforce_post_only(flags, order_type=type)` in `submit_order()` - validates order type
- Line 71: `enforce_post_only(flags)` in `update_order()`
- Funding offers skip enforcement (line 114)

**Layer 4 - WebSocket Client** (`bfx_websocket_client.py`):
- Lines 350-355: Final enforcement before sending to WebSocket
- Handles both "on" (new order) and "ou" (update order) events

### Heartbeat Events - Technical Implementation

**WebSocket Bucket** (`bfx_websocket_bucket.py`):
- Lines 69-72: Emits heartbeat events for public channels instead of discarding

**WebSocket Client** (`bfx_websocket_client.py`):
- Lines 267-268: Emits heartbeat events for authenticated channel (channel 0)

**Event Emitter** (`bfx_event_emitter.py`):
- Line 35: Added "heartbeat" to valid events list

## Verification for Auditors

### Quick Verification (< 1 minute)
```bash
# Count enforcement points in production code (excluding imports and definition)
grep -r "enforce_post_only(" bfxapi/ --include="*.py" | grep -v "def enforce" | grep -v test | wc -l
# Expected: 8 occurrences

# Verify POST_ONLY flag value
grep "POST_ONLY = 4096" bfxapi/constants/order_flags.py
# Expected: Match found

# Check all enforcement locations
grep -n "enforce_post_only" bfxapi/rest/_interfaces/rest_auth_endpoints.py
# Expected: Lines 106 and 146

grep -n "enforce_post_only" bfxapi/rest/_interface/middleware.py  
# Expected: Lines 69 and 72

grep -n "enforce_post_only" bfxapi/websocket/_client/bfx_websocket_inputs.py
# Expected: Lines 32 and 71

grep -n "enforce_post_only" bfxapi/websocket/_client/bfx_websocket_client.py
# Expected: Lines 350 and 353
```

### Production Code Changes

**Post-Only Enforcement Files:**
```
bfxapi/_utils/post_only_enforcement.py        # NEW: 37 lines (with validation)
bfxapi/constants/order_flags.py               # NEW: 6 lines  
bfxapi/rest/_interface/middleware.py          # +13 lines (with notes)
bfxapi/rest/_interfaces/rest_auth_endpoints.py # +13 lines
bfxapi/websocket/_client/bfx_websocket_inputs.py # +15 lines
bfxapi/websocket/_client/bfx_websocket_client.py # +8 lines
tests/test_post_only_enforcement.py           # 240+ lines (13 tests)
```

**Heartbeat Events Files:**
```
bfxapi/websocket/_client/bfx_websocket_bucket.py # +4 lines
bfxapi/websocket/_client/bfx_websocket_client.py # +4 lines
bfxapi/websocket/_event_emitter/bfx_event_emitter.py # +1 line
examples/websocket/heartbeat.py               # NEW: 65 lines
README.md                                      # +27 lines
```

### Code Delta Summary
- **Post-Only Enforcement**: ~92 lines of production code (with validation)
- **Heartbeat Events**: ~40 lines of production code  
- **Core safety logic**: 37 lines (the `enforce_post_only` function with market order validation)
- **Tests**: 240+ lines, 13 comprehensive tests
- **No external dependencies added**

## PyPI Publishing

This package uses GitHub Actions with Trusted Publishing (OIDC) for secure, automated PyPI releases.

### Publishing Process

1. **Update version in setup.py**
2. **Create Git tag and push:**
   ```bash
   git tag v3.0.5.post2
   git push origin v3.0.5.post2
   ```
3. **Create GitHub Release** - triggers automatic PyPI upload via `.github/workflows/publish.yml`

### Configuration
- **PyPI Project**: bitfinex-api-py-postonly
- **Workflow**: `.github/workflows/publish.yml`
- **No API tokens** - Uses OIDC authentication

## Important Notes

⚠️ **This is a SAFETY fork, not for bypassing exchange rules**

- All orders will be maker-only (won't cross spread)
- MARKET orders are rejected with clear error message
- Monitor heartbeats to ensure connection is alive
- Funding offers are not affected by POST_ONLY enforcement
- The enforcement cannot be disabled without modifying the source code

## Example: Order Submission

```python
from bfxapi import Client

bfx = Client(api_key="...", api_secret="...")

# This will ALWAYS be post-only (flag 4096 added automatically)
order = bfx.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=0.01,
    price=50000
    # No need to specify flags - POST_ONLY is forced
)

# Even if you try flags=0, POST_ONLY is still added
order = bfx.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=0.01,
    price=50000,
    flags=0  # Still becomes flags=4096 internally!
)

# Other flags are preserved
order = bfx.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD",
    amount=0.01,
    price=50000,
    flags=64  # HIDDEN flag - becomes 4160 (4096 | 64)
)
```

## Protection Levels

1. **Application Level**: `submit_order()` and `update_order()` force POST_ONLY
2. **Middleware Level**: Order submit/update REST calls force POST_ONLY
3. **WebSocket Level**: Order submit/update WS messages force POST_ONLY

Each level provides redundant protection to ensure no order can bypass the POST_ONLY requirement.