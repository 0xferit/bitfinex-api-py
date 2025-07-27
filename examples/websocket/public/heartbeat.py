# python -c "import examples.websocket.public.heartbeat"

from bfxapi import Client
from bfxapi.websocket.subscriptions import Subscription

bfx = Client()


@bfx.wss.on("heartbeat")
def on_heartbeat(subscription: Subscription = None):
    """
    Handle heartbeat events from the WebSocket server.
    
    For public channels, the subscription parameter contains the subscription info.
    For authenticated connections, subscription will be None.
    """
    if subscription:
        print(f"Heartbeat received for subscription: {subscription['channel']} - {subscription.get('symbol', subscription.get('key', 'N/A'))}")
    else:
        print("Heartbeat received for authenticated connection")


@bfx.wss.on("open")
async def on_open():
    # Subscribe to a ticker to see heartbeats for subscriptions
    await bfx.wss.subscribe("ticker", symbol="tBTCUSD")


@bfx.wss.on("subscribed")
def on_subscribed(subscription: Subscription):
    print(f"Subscribed to {subscription['channel']} for {subscription.get('symbol', subscription.get('key', 'N/A'))}")


print("Starting WebSocket client - you should see heartbeat events...")
print("Heartbeats are sent by the server to keep the connection alive.")
print("Press Ctrl+C to stop.")

bfx.wss.run()
