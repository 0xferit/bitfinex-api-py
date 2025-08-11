"""
Demonstrates heartbeat event handling for both public and authenticated
WebSocket connections.

Usage:
    python examples/websocket/heartbeat.py

If BFX_API_KEY and BFX_API_SECRET environment variables are set, the client will
authenticate and display heartbeats on the authenticated connection (channel 0).
Otherwise, only public channel heartbeats are shown.
"""

import os
from typing import Any, Dict, Optional

from bfxapi import Client
from bfxapi.websocket.subscriptions import Subscription

# Initialize client with optional authentication
api_key = os.getenv("BFX_API_KEY")
api_secret = os.getenv("BFX_API_SECRET")

if api_key and api_secret:
    print("Initializing authenticated client...")
    bfx = Client(api_key=api_key, api_secret=api_secret)
else:
    print("Initializing public client (set BFX_API_KEY and BFX_API_SECRET for auth)...")
    bfx = Client()


@bfx.wss.on("heartbeat")
def on_heartbeat(subscription: Optional[Subscription]) -> None:
    """Handle heartbeat events from both public and authenticated channels."""
    if subscription:
        channel = subscription["channel"]
        label = subscription.get("symbol", subscription.get("key", "unknown"))
        print(f"Heartbeat for {channel}: {label}")
    else:
        print("Heartbeat on authenticated connection (channel 0)")


@bfx.wss.on("authenticated")
async def on_authenticated(event: Dict[str, Any]) -> None:
    """Handle authentication confirmation."""
    user_id = event.get("userId", "unknown")
    print(f"Successfully authenticated with userId: {user_id}")


@bfx.wss.on("open")
async def on_open() -> None:
    """Subscribe to public channels when connection opens."""
    print("WebSocket connection opened")
    # Subscribe to a public channel to observe subscription heartbeats
    await bfx.wss.subscribe("ticker", symbol="tBTCUSD")
    print("Subscribed to ticker channel for tBTCUSD")


if __name__ == "__main__":
    print("Starting WebSocket client... Press Ctrl+C to stop.")
    try:
        bfx.wss.run()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error: {e}")
