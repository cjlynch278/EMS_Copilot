"""
Simple Speech-to-Text using Google Cloud Speech-to-Text API.
Usage in Jupyter notebook:
    from simple_speech_to_text import transcribe_speech
    text = transcribe_speech()
"""

import os
import pyaudio
import wave
from google.cloud import speech

def transcribe_speech(record_seconds=5, sample_rate=16000):
    """
    Record speech from microphone and transcribe it using Google Cloud Speech-to-Text.
    
    Args:
        record_seconds (int): Number of seconds to record (default: 5)
        sample_rate (int): Audio sample rate in Hz (default: 16000)
    
    Returns:
        str: Transcribed text or error message
    """
    try:
        # Audio recording parameters
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = sample_rate
        
        # Initialize PyAudio
        audio = pyaudio.PyAudio()
        
        # Open audio stream
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        print(f"🎤 Recording {record_seconds} seconds... Speak now!")
        frames = []
        
        # Record audio
        for i in range(0, int(RATE / CHUNK * record_seconds)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        print("⏹️ Recording stopped.")
        
        # Close stream
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Initialize Google Cloud Speech client
        client = speech.SpeechClient()
        
        # Configure recognition
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code="en-US",
            enable_automatic_punctuation=True,
        )
        
        # Convert frames to audio content
        audio_content = b''.join(frames)
        audio_obj = speech.RecognitionAudio(content=audio_content)
        
        # Perform transcription
        response = client.recognize(config=config, audio=audio_obj)
        
        # Extract transcript
        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript
        
        return transcript.strip() if transcript else "No speech detected"
        
    except ImportError as e:
        return f"Missing dependency: {e}. Install with: pip install pyaudio google-cloud-speech"
    except Exception as e:
        return f"Error: {e}"

def save_audio(frames, filename="recorded_audio.wav", sample_rate=16000):
    """Save recorded audio frames to a WAV file."""
    try:
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = sample_rate
        
        audio = pyaudio.PyAudio()
        
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        
        audio.terminate()
        print(f"💾 Audio saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving audio: {e}")
        return False

# Example usage for Jupyter notebook:
# from simple_speech_to_text import transcribe_speech
# text = transcribe_speech(record_seconds=5)
# print(f"Transcribed text: {text}") 