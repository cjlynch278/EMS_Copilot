from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from ems_copilot.domain.services.chroma_agent import ChromaAgent
from ems_copilot.domain.services.sql_agent import SQLAgent
from ems_copilot.domain.services.triage_agent import TriageAgent
from ems_copilot.domain.services.vitals_agent import VitalsAgent
from ems_copilot.domain.services.route_agent import RouteAgent
from ems_copilot.domain.services.openai_agent import OpenAIAgent
from ems_copilot.domain.services.orchestrator_agent import OrchestratorAgent
import logging
import json

app = FastAPI()

# Initialize agents
chroma_agent = ChromaAgent()
sql_agent = SQLAgent()
triage_agent = TriageAgent()
vitals_agent = VitalsAgent()
route_agent = RouteAgent()
orchestrator_agent = OrchestratorAgent()

# Request model
class QueryRequest(BaseModel):
    query: str
    type: str  # Type of query (e.g., "protocol", "database", "triage", etc.)

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

# Route query to the appropriate agent
@app.post("/query")
async def route_query(request: QueryRequest):
    # Use OpenAIAgent to classify the query type
    print("--------------------")
    logging.info(f"Received query: {request.query}")
    query_type = openai_agent.classify_query(request.query)

    if query_type == "protocol":
        return {"response": chroma_agent.handle_query(request.query)}
    elif query_type == "database":
        return {"response": sql_agent.handle_query(request.query)}
    elif query_type == "triage":
        return {"response": triage_agent.handle_query(request.query)}
    elif query_type == "vitals":
        return {"response": vitals_agent.handle_query(request.query)}
    elif query_type == "route":
        return {"response": route_agent.handle_query(request.query)}
    else:
        raise HTTPException(status_code=400, detail="Unable to classify query type")