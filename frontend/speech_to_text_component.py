"""
Speech-to-Text component for Streamlit app.
This component provides a microphone button that records audio and converts it to text.
"""

import streamlit as st
import pyaudio
import wave
import tempfile
import os
import base64
from google.cloud import speech
import threading
import time

class SpeechToTextComponent:
    def __init__(self):
        """Initialize the speech-to-text component."""
        self.audio = None
        self.stream = None
        self.is_recording = False
        self.frames = []
        
    def record_audio(self, record_seconds=5, sample_rate=16000):
        """
        Record audio from microphone.
        
        Args:
            record_seconds (int): Number of seconds to record
            sample_rate (int): Audio sample rate in Hz
            
        Returns:
            bytes: Audio data as bytes
        """
        try:
            # Audio recording parameters
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = sample_rate
            
            # Initialize PyAudio
            self.audio = pyaudio.PyAudio()
            
            # Open audio stream
            self.stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            self.frames = []
            self.is_recording = True
            
            # Record audio
            for i in range(0, int(RATE / CHUNK * record_seconds)):
                if not self.is_recording:
                    break
                data = self.stream.read(CHUNK)
                self.frames.append(data)
            
            # Close stream
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
            
            # Convert frames to audio content
            audio_content = b''.join(self.frames)
            return audio_content
            
        except Exception as e:
            st.error(f"Error recording audio: {e}")
            return None
    
    def transcribe_audio(self, audio_content, sample_rate=16000):
        """
        Transcribe audio using Google Cloud Speech-to-Text.
        
        Args:
            audio_content (bytes): Audio data
            sample_rate (int): Audio sample rate in Hz
            
        Returns:
            str: Transcribed text or error message
        """
        try:
            # Initialize Google Cloud Speech client
            client = speech.SpeechClient()
            
            # Configure recognition
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=sample_rate,
                language_code="en-US",
                enable_automatic_punctuation=True,
            )
            
            # Create audio object
            audio_obj = speech.RecognitionAudio(content=audio_content)
            
            # Perform transcription
            response = client.recognize(config=config, audio=audio_obj)
            
            # Extract transcript
            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript
            
            return transcript.strip() if transcript else "No speech detected"
            
        except Exception as e:
            return f"Error transcribing audio: {e}"
    
    def stop_recording(self):
        """Stop recording audio."""
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()

def speech_to_text_button(label="🎤 Record Speech", key="speech_to_text", record_seconds=5):
    """
    Create a speech-to-text button for Streamlit.
    Starts recording immediately when clicked.
    
    Args:
        label (str): Button label
        key (str): Unique key for the button
        record_seconds (int): Number of seconds to record
        
    Returns:
        str: Transcribed text or None if cancelled/error
    """
    
    # Check if button is clicked
    if st.button(label, key=key):
        
        # Create placeholder for status
        status_placeholder = st.empty()
        result_placeholder = st.empty()
        
        try:
            # Check if Google Cloud credentials are set
            if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                # Try to use gcloud auth
                try:
                    import subprocess
                    subprocess.run(["gcloud", "auth", "application-default", "print-access-token"], 
                                 check=True, capture_output=True)
                except:
                    st.error("❌ Google Cloud credentials not found. Please set GOOGLE_APPLICATION_CREDENTIALS or run 'gcloud auth application-default login'")
                    return None
            
            # Initialize component
            stt_component = SpeechToTextComponent()
            
            # Start recording immediately - no delay
            status_placeholder.info(f"🎤 Recording {record_seconds} seconds... Speak now!")
            audio_content = stt_component.record_audio(record_seconds)
            
            if audio_content:
                status_placeholder.info("🔄 Transcribing audio...")
                transcript = stt_component.transcribe_audio(audio_content)
                
                if transcript and transcript != "No speech detected":
                    status_placeholder.success("✅ Transcription complete!")
                    # Store in session state and automatically populate query
                    st.session_state.query_text = transcript
                    st.session_state.transcribed_text = transcript
                    return transcript
                else:
                    status_placeholder.warning("❌ No speech detected. Please try again.")
                    return None
            else:
                status_placeholder.error("❌ Failed to record audio.")
                return None
                
        except ImportError as e:
            st.error(f"❌ Missing dependency: {e}")
            st.info("Please install: pip install pyaudio google-cloud-speech")
            return None
        except Exception as e:
            st.error(f"❌ Error: {e}")
            return None

def speech_to_text_with_preview(label="🎤 Record Speech", key="speech_to_text_preview", record_seconds=5):
    """
    Create a speech-to-text button with preview of transcribed text.
    
    Args:
        label (str): Button label
        key (str): Unique key for the button
        record_seconds (int): Number of seconds to record
        
    Returns:
        str: Transcribed text or None if cancelled/error
    """
    
    # Create columns for button and preview
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button(label, key=key):
            transcript = speech_to_text_button(label, key + "_inner", record_seconds)
            if transcript:
                st.session_state.transcribed_text = transcript
    
    with col2:
        if 'transcribed_text' in st.session_state:
            st.text_area("Transcribed Text:", st.session_state.transcribed_text, height=100, key=key + "_preview")
            return st.session_state.transcribed_text
    
    return None 