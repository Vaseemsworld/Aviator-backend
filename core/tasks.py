import asyncio
import random
from channels.layers import get_channel_layer
from .views import get_crash_point

async def game_loop():
    channel_layer = get_channel_layer()
    while True:
        # Phase 1: Loading
        await channel_layer.group_send("game", {
            "type": "broadcast",
            "state": "loading"
        })
        await asyncio.sleep(5)   # 5 seconds loading

        # Phase 2: Running
        crash_point = get_crash_point()
        await channel_layer.group_send("game", {
            "type": "broadcast",
            "state": "running",
            "crash_point": crash_point
        })
        await asyncio.sleep(10)  # round lasts 10s

        # Phase 3: End
        await channel_layer.group_send("game", {
            "type": "broadcast",
            "state": "ended"
        })
        await asyncio.sleep(2)   # short break
