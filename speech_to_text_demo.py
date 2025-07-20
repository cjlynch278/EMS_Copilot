#!/usr/bin/env python3
"""
Simple Speech-to-Text demo using Google Cloud Speech-to-Text API.
This script captures audio from your laptop microphone and transcribes it in real-time.
"""

import os
import pyaudio
import wave
import threading
import time
from google.cloud import speech
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SpeechToTextDemo:
    def __init__(self):
        """Initialize the Speech-to-Text demo."""
        # Audio recording parameters
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.RECORD_SECONDS = 5
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        
        # Initialize Google Cloud Speech client
        self.client = speech.SpeechClient()
        
        # Configure recognition
        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.RATE,
            language_code="en-US",
            enable_automatic_punctuation=True,
        )
        
        self.is_recording = False
        
    def record_audio(self):
        """Record audio from microphone."""
        stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        print("🎤 Recording... Speak now!")
        frames = []
        
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            if not self.is_recording:
                break
            data = stream.read(self.CHUNK)
            frames.append(data)
        
        print("⏹️  Recording stopped.")
        
        stream.stop_stream()
        stream.close()
        
        return frames
    
    def transcribe_audio(self, audio_frames):
        """Transcribe audio using Google Cloud Speech-to-Text."""
        try:
            # Convert frames to audio content
            audio_content = b''.join(audio_frames)
            
            # Create audio object
            audio = speech.RecognitionAudio(content=audio_content)
            
            # Perform the transcription
            response = self.client.recognize(config=self.config, audio=audio)
            
            # Extract and return the transcript
            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript
            
            return transcript.strip()
            
        except Exception as e:
            print(f"❌ Error transcribing audio: {e}")
            return ""
    
    def save_audio_file(self, audio_frames, filename="recorded_audio.wav"):
        """Save recorded audio to a WAV file."""
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(audio_frames))
        print(f"💾 Audio saved to {filename}")
    
    def run_demo(self):
        """Run the speech-to-text demo."""
        print("🎤 Google Cloud Speech-to-Text Demo")
        print("=" * 50)
        print("This demo will:")
        print("1. Record 5 seconds of audio from your microphone")
        print("2. Send it to Google Cloud Speech-to-Text")
        print("3. Display the transcribed text")
        print("=" * 50)
        
        while True:
            try:
                # Get user input
                user_input = input("\nPress Enter to start recording (or 'q' to quit): ").strip().lower()
                
                if user_input == 'q':
                    break
                
                # Start recording
                self.is_recording = True
                audio_frames = self.record_audio()
                self.is_recording = False
                
                if not audio_frames:
                    print("❌ No audio recorded. Please try again.")
                    continue
                
                # Save audio file (optional)
                self.save_audio_file(audio_frames)
                
                # Transcribe audio
                print("🔄 Transcribing audio...")
                transcript = self.transcribe_audio(audio_frames)
                
                if transcript:
                    print("\n📝 Transcription:")
                    print("-" * 30)
                    print(transcript)
                    print("-" * 30)
                else:
                    print("❌ No speech detected or transcription failed.")
                    
            except KeyboardInterrupt:
                print("\n👋 Demo stopped by user.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("Please check your Google Cloud credentials and try again.")
                break
        
        # Clean up
        self.audio.terminate()
        print("👋 Demo ended.")

def check_requirements():
    """Check if required packages are installed."""
    try:
        import pyaudio
        import wave
        from google.cloud import speech
        from dotenv import load_dotenv
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("\nPlease install required packages:")
        print("pip install pyaudio google-cloud-speech python-dotenv")
        return False

def main():
    """Main function."""
    print("🔍 Checking requirements...")
    
    if not check_requirements():
        return
    
    # Check for Google Cloud credentials
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("⚠️  Warning: GOOGLE_APPLICATION_CREDENTIALS environment variable not set.")
        print("Please set it to the path of your Google Cloud service account key file.")
        print("Example: export GOOGLE_APPLICATION_CREDENTIALS='/path/to/your/key.json'")
        print("\nYou can also run: gcloud auth application-default login")
        return
    
    # Run the demo
    demo = SpeechToTextDemo()
    demo.run_demo()

if __name__ == "__main__":
    main() 