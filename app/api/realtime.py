import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.db.redis import get_redis

router = APIRouter(tags=['realtime'])


class ConnectionManager:
    def __init__(self) -> None:
        self.active: dict[str, set[WebSocket]] = {}

    async def connect(self, business_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.setdefault(business_id, set()).add(websocket)

    def disconnect(self, business_id: str, websocket: WebSocket) -> None:
        self.active.get(business_id, set()).discard(websocket)

    async def broadcast(self, business_id: str, payload: dict) -> None:
        for websocket in list(self.active.get(business_id, set())):
            await websocket.send_json(payload)


manager = ConnectionManager()


@router.websocket('/ws/staff/{business_id}')
async def staff_socket(websocket: WebSocket, business_id: str):
    await manager.connect(business_id, websocket)
    redis = await get_redis()
    await redis.publish(f'staff:{business_id}:events', json.dumps({'type': 'device.online'}))
    try:
        while True:
            payload = await websocket.receive_json()
            await manager.broadcast(business_id, payload)
            await redis.publish(f'staff:{business_id}:events', json.dumps(payload))
    except WebSocketDisconnect:
        manager.disconnect(business_id, websocket)
        await redis.publish(f'staff:{business_id}:events', json.dumps({'type': 'device.offline'}))
