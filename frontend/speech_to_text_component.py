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
        
    def record_audio(self, max_seconds=30, silence_threshold=0.01, silence_duration=2.0, sample_rate=16000):
        """
        Record audio from microphone until silence is detected.
        
        Args:
            max_seconds (int): Maximum recording time in seconds
            silence_threshold (float): Threshold for silence detection (0.0 to 1.0)
            silence_duration (float): How long to wait in silence before stopping (seconds)
            sample_rate (int): Audio sample rate in Hz
            
        Returns:
            bytes: Audio data as bytes
        """
        try:
            import numpy as np
            
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
            
            # Silence detection variables
            silence_chunks = 0
            silence_chunks_threshold = int(silence_duration * RATE / CHUNK)
            max_chunks = int(max_seconds * RATE / CHUNK)
            
            # Record audio until silence or max time
            for i in range(max_chunks):
                if not self.is_recording:
                    break
                    
                data = self.stream.read(CHUNK)
                self.frames.append(data)
                
                # Check for silence
                audio_data = np.frombuffer(data, dtype=np.int16)
                volume = np.sqrt(np.mean(audio_data**2))
                normalized_volume = volume / 32768.0  # Normalize to 0-1
                
                if normalized_volume < silence_threshold:
                    silence_chunks += 1
                else:
                    silence_chunks = 0
                
                # Stop if silence detected for long enough
                if silence_chunks >= silence_chunks_threshold:
                    break
            
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

def speech_to_text_button(label="🎤 Record Speech", key="speech_to_text", max_seconds=30, silence_duration=2.0):
    """
    Create a speech-to-text button for Streamlit.
    Uses pre-initialized component for immediate recording.
    
    Args:
        label (str): Button label
        key (str): Unique key for the button
        max_seconds (int): Maximum recording time in seconds
        silence_duration (float): How long to wait in silence before stopping (seconds)
        
    Returns:
        str: Transcribed text or None if cancelled/error
    """
    
    # Initialize session state for recording status
    if f"{key}_recording" not in st.session_state:
        st.session_state[f"{key}_recording"] = False
    if f"{key}_status" not in st.session_state:
        st.session_state[f"{key}_status"] = ""
    
    # Check if button is clicked
    if st.button(label, key=key):
        st.session_state[f"{key}_recording"] = True
        st.session_state[f"{key}_status"] = f"🎤 Recording... Speak now! (stops after {silence_duration}s of silence)"
        st.rerun()
    
    # Show status if recording
    if st.session_state[f"{key}_recording"]:
        status_placeholder = st.empty()
        status_placeholder.info(st.session_state[f"{key}_status"])
        
        try:
            # Check if component is initialized
            if not st.session_state.get('stt_initialized', False):
                st.error(f"❌ Speech-to-text not initialized: {st.session_state.get('stt_error', 'Unknown error')}")
                st.session_state[f"{key}_recording"] = False
                return None
            
            # Check if Google Cloud is authenticated
            if not st.session_state.get('gcloud_authenticated', False):
                st.error(f"❌ Google Cloud not authenticated: {st.session_state.get('gcloud_error', 'Unknown error')}")
                st.session_state[f"{key}_recording"] = False
                return None
            
            # Use pre-initialized component
            stt_component = st.session_state.stt_component
            
            # Update status to show recording
            st.session_state[f"{key}_status"] = "🔄 Recording audio..."
            status_placeholder.info(st.session_state[f"{key}_status"])
            
            # Record audio immediately
            audio_content = stt_component.record_audio(max_seconds=max_seconds, silence_duration=silence_duration)
            
            if audio_content:
                st.session_state[f"{key}_status"] = "🔄 Transcribing audio..."
                status_placeholder.info(st.session_state[f"{key}_status"])
                
                # Transcribe audio
                transcript = stt_component.transcribe_audio(audio_content)
                
                if transcript and transcript != "No speech detected":
                    st.session_state[f"{key}_status"] = "✅ Transcription complete!"
                    status_placeholder.success(st.session_state[f"{key}_status"])
                    
                    # Store in session state and automatically populate query
                    st.session_state.query_text = transcript
                    st.session_state.transcribed_text = transcript
                    
                    # Reset recording state
                    st.session_state[f"{key}_recording"] = False
                    return transcript
                else:
                    st.session_state[f"{key}_status"] = "❌ No speech detected. Please try again."
                    status_placeholder.warning(st.session_state[f"{key}_status"])
                    st.session_state[f"{key}_recording"] = False
                    return None
            else:
                st.session_state[f"{key}_status"] = "❌ Failed to record audio."
                status_placeholder.error(st.session_state[f"{key}_status"])
                st.session_state[f"{key}_recording"] = False
                return None
                
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.session_state[f"{key}_recording"] = False
            return None
    
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