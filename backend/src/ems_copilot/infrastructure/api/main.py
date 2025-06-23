from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from ems_copilot.domain.services.orchestrator_agent import OrchestratorAgent
import logging
import json
import os

app = FastAPI()


# Initialize orchestrator agent
orchestrator_agent = OrchestratorAgent(
    gemini_api_key=os.getenv("GEMINI_API_KEY"),
    firebase_credentials_path=os.getenv("FIRESTORE_CREDENTIALS_PATH")
)

# Request model
class QueryRequest(BaseModel):
    query: str

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")

            # Process message through orchestrator
            response = orchestrator_agent.orchestrate(user_message)
            
            # Send response back to client
            await manager.send_message(
                json.dumps({"response": response}),
                websocket
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logging.error(f"Error in WebSocket connection: {str(e)}")
        await manager.send_message(
            json.dumps({"error": "An error occurred processing your message"}),
            websocket
        )

# Route query to the orchestrator agent
@app.post("/query")
async def route_query(request: QueryRequest):
    logging.info(f"Received query: {request.query}")
    try:
        response = orchestrator_agent.orchestrate(request.query)
        return {"response": response}
    except Exception as e:
        logging.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")