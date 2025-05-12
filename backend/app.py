from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.chroma_agent import ChromaAgent
from agents.sql_agent import SQLAgent
from agents.triage_agent import TriageAgent
from agents.vitals_agent import VitalsAgent
from agents.route_agent import RouteAgent
from agents.openai_agent import OpenAIAgent
import logging

app = FastAPI()

# Initialize agents
chroma_agent = ChromaAgent()
sql_agent = SQLAgent()
triage_agent = TriageAgent()
vitals_agent = VitalsAgent()
route_agent = RouteAgent()

# Request model
class QueryRequest(BaseModel):
    query: str
    type: str  # Type of query (e.g., "protocol", "database", "triage", etc.)

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