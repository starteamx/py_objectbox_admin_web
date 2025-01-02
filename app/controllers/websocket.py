from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.database.manager import DatabaseManager

router = APIRouter()
db_manager = DatabaseManager()

@router.websocket("/ws/{instance_id}")
async def websocket_endpoint(websocket: WebSocket, instance_id: int):
    await websocket.accept()
    try:
        while True:
            # Here you can handle incoming messages or send updates
            data = await websocket.receive_text()
            # Process the data or send a response
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        # Handle disconnection
        print(f"WebSocket disconnected for instance {instance_id}")
        # Optionally update the database or perform cleanup 