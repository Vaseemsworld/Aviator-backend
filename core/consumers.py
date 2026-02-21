import asyncio
from datetime import datetime, timezone
import json
import math
from channels.generic.websocket import AsyncWebsocketConsumer
from .utils import generate_crash_point

class GameConsumer(AsyncWebsocketConsumer):
    GROUP_NAME = 'game'

    _loop_task = None
    _loop_lock = asyncio.Lock()
    _running = False

    _crash_point = 1.0
    _score = 1.0
    _cooldown_seconds = 10.0

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)

        async with self._loop_lock:
            if not self._running:
                self._running = True
                self._loop_task = asyncio.create_task(self.game_loop())
        
        await self.send_json({
            'type': 'SNAPSHOT',
            'score': round(self._score,2),
            'crash_point': float(self._crash_point),
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)

        async with self._loop_lock:
            if self._running and self._loop_task:
                self._running = False
                self._loop_task.cancel()
                try:
                    await self._loop_task
                except asyncio.CancelledError:
                    pass
                self._loop_task = None
    
    async def broadcast(self, payload: dict):
        await self.channel_layer.group_send(
            self.GROUP_NAME,
            {
                'type': 'game.message',
                'payload': payload
            }
        )
    async def game_message(self, event):
        await self.send_json(event['payload'])
    
    async def send_json(self, data):
        await self.send(text_data=json.dumps(data, separators=(',', ':')))
    
    async def game_loop(self):
        TICK_MS = 1000 / 60  # 60 FPS
        COOLDOWN = self._cooldown_seconds
        

        def score_at_time(elapsed_ms: float) -> float:
            rate = 0.00015
            return math.exp(rate * elapsed_ms)
        
        try:
            while self._running:
                """---Round Start---"""
                self._score = 1.0
                self._crash_point = round(generate_crash_point(),2)
                round_start = asyncio.get_event_loop().time() * 1000.0
                round_start_iso = datetime.now(tz=timezone.utc).isoformat()
                print('round started', 'crash_point:', self._crash_point)
                await self.broadcast({
                    'type': 'ROUND_START',
                    'crash_point': float(self._crash_point),
                    'timestamp': round_start_iso,
                })

                """---Running (Tick)---"""
                last = asyncio.get_event_loop().time() * 1000.0
                while self._score <= self._crash_point:
                    await asyncio.sleep(TICK_MS / 1000.0)

                    now = asyncio.get_event_loop().time() * 1000.0
                    elapsed = now - round_start

                    self._score = score_at_time(elapsed)
                    
                    print('running.........',round(self._score, 2), )

                    await self.broadcast({
                        'type': 'TICK',
                        'score': round(self._score, 2),
                    })

                self._score = float(self._crash_point)

                """---Crash---"""
                print('crashed at', self._score)
                await self.broadcast({
                    'type': 'CRASH',
                    'final_score': float(self._crash_point),
                })

                """---Cooldown---"""
                print(f"cooldown started for {COOLDOWN} seconds")
                await self.broadcast({
                    'type': "COOLDOWN_START",
                    "duration": COOLDOWN,
                })

                for remaining in range(int(COOLDOWN), 0, -1):
                    print(f"cooldown: {remaining}s left")
                    await self.broadcast({
                        'type': 'COOLDOWN_TICK',
                        'remaining': remaining,
                    })
                    await asyncio.sleep(1)

                print("cooldown ended")
                await self.broadcast({
                    'type': 'COOLDOWN_END',
                })
        except asyncio.CancelledError:
            pass
        finally:
            self._running = False
            