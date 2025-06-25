from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from ems_copilot.domain.services.orchestrator_agent import OrchestratorAgent
import logging
import json
import os
import tempfile
from google.cloud import texttospeech

app = FastAPI()


# Initialize orchestrator agent
orchestrator_agent = OrchestratorAgent(
    gemini_api_key=os.getenv("GEMINI_API_KEY"),
    firebase_credentials_path=os.getenv("FIRESTORE_CREDENTIALS_PATH")
)

# Request model
class QueryRequest(BaseModel):
    query: str

# Text-to-Speech request model
class TextToSpeechRequest(BaseModel):
    text: str
    voice_name: str = "en-US-Standard-A"  # Default voice
    language_code: str = "en-US"  # Default language
    speaking_rate: float = 1.0  # Default speaking rate
    pitch: float = 0.0  # Default pitch

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

# Text-to-Speech endpoint
@app.post("/text-to-speech")
async def text_to_speech(request: TextToSpeechRequest):
    """
    Convert text to speech and return a WAV file.
    
    Args:
        request: TextToSpeechRequest containing text and voice parameters
        
    Returns:
        FileResponse: WAV audio file
    """
    try:
        logging.info(f"Converting text to speech: {request.text[:50]}...")
        
        # Initialize the Text-to-Speech client
        client = texttospeech.TextToSpeechClient()
        
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=request.text)
        
        # Build the voice request
        voice = texttospeech.VoiceSelectionParams(
            language_code=request.language_code,
            name=request.voice_name
        )
        
        # Select the type of audio file to return
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=request.speaking_rate,
            pitch=request.pitch
        )
        
        # Perform the text-to-speech request
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(response.audio_content)
            temp_file_path = temp_file.name
        
        # Return the audio file
        return FileResponse(
            path=temp_file_path,
            media_type="audio/wav",
            filename="speech.wav",
            background=lambda: os.unlink(temp_file_path)  # Clean up temp file after response
        )
        
    except Exception as e:
        logging.error(f"Error in text-to-speech conversion: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error converting text to speech: {str(e)}"
        )

# Get available voices endpoint
@app.get("/voices")
async def get_voices(language_code: str = "en-US"):
    """
    Get a list of available voices for the specified language.
    
    Args:
        language_code: Language code to filter voices (default: en-US)
        
    Returns:
        List of available voices
    """
    try:
        logging.info(f"Fetching voices for language: {language_code}")
        
        # Initialize the Text-to-Speech client
        client = texttospeech.TextToSpeechClient()
        
        # Perform the request
        response = client.list_voices(language_code=language_code)
        
        # Format the response
        voices = []
        for voice in response.voices:
            voices.append({
                "name": voice.name,
                "language_codes": list(voice.language_codes),
                "ssml_gender": voice.ssml_gender.name,
                "natural_sample_rate_hertz": voice.natural_sample_rate_hertz
            })
        
        return {"voices": voices}
        
    except Exception as e:
        logging.error(f"Error fetching voices: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching voices: {str(e)}"
        )

# HD Text-to-Speech endpoint using Google's HD voices
@app.post("/tts/hd")
async def hd_text_to_speech(request: TextToSpeechRequest):
    """
    Convert text to speech using Google's HD voices for better quality.
    
    Args:
        request: TextToSpeechRequest containing text and voice parameters
        
    Returns:
        Response: Raw audio content
    """
    try:
        logging.info(f"Converting text to HD speech: {request.text[:50]}...")
        
        # Initialize the Text-to-Speech client
        client = texttospeech.TextToSpeechClient()
        
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=request.text)
        
        # Build the voice request with HD voice
        voice = texttospeech.VoiceSelectionParams(
            language_code=request.language_code,
            name=request.voice_name
        )
        
        # Select the type of audio file to return (HD quality)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            sample_rate_hertz=24000,  # Higher sample rate for HD quality
            speaking_rate=request.speaking_rate,
            pitch=request.pitch
        )
        
        # Perform the text-to-speech request
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        # Return the raw audio content directly
        return Response(
            content=response.audio_content,
            media_type="audio/wav",
            headers={"Content-Disposition": "inline"}
        )
        
    except Exception as e:
        logging.error(f"Error in HD text-to-speech conversion: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error converting text to speech: {str(e)}"
        )