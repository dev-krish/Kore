import asyncio
import json
import logging
from typing import Dict, List, AsyncGenerator

logger = logging.getLogger(__name__)

class EventManager:
    """Manages active SSE client connections per campaign for live agent streaming."""

    def __init__(self):
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}

    def subscribe(self, campaign_id: str) -> asyncio.Queue:
        if campaign_id not in self._subscribers:
            self._subscribers[campaign_id] = []
        queue = asyncio.Queue()
        self._subscribers[campaign_id].append(queue)
        logger.info(f"Client subscribed to SSE events for campaign {campaign_id}")
        return queue

    def unsubscribe(self, campaign_id: str, queue: asyncio.Queue):
        if campaign_id in self._subscribers:
            if queue in self._subscribers[campaign_id]:
                self._subscribers[campaign_id].remove(queue)
            if not self._subscribers[campaign_id]:
                del self._subscribers[campaign_id]
        logger.info(f"Client unsubscribed from campaign {campaign_id}")

    async def broadcast(self, campaign_id: str, event_data: dict):
        if campaign_id in self._subscribers:
            data_str = json.dumps(event_data)
            for queue in self._subscribers[campaign_id]:
                await queue.put(data_str)

event_manager = EventManager()
