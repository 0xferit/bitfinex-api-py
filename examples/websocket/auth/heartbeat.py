# python -c "import examples.websocket.auth.heartbeat"

import os

from bfxapi import Client

bfx = Client(
    api_key=os.getenv("BFX_API_KEY"),
    api_secret=os.getenv("BFX_API_SECRET"),
)


@bfx.wss.on("heartbeat")
def on_heartbeat():
    """
    Handle heartbeat events from the WebSocket server for authenticated connections.
    
    These heartbeats are sent on the authenticated channel (channel 0) and don't
    have an associated subscription.
    """
    print("Heartbeat received on authenticated connection")


@bfx.wss.on("authenticated")
async def on_authenticated(event):
    print(f"Authentication successful: {event}")
    print("Now listening for heartbeats on the authenticated connection...")


@bfx.wss.on("open")
async def on_open():
    print("WebSocket connection opened")


print("Starting authenticated WebSocket client...")
print("You should see heartbeat events after authentication.")
print("Press Ctrl+C to stop.")

bfx.wss.run()
