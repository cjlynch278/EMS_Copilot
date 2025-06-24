"""
Google Cloud Text-to-Speech REST API Wrapper
Direct wrapper for the REST API you showed
"""

import requests
import json
import base64
import os
import subprocess
from IPython.display import Audio

class GoogleTTSRest:
    def __init__(self):
        self.base_url = "https://texttospeech.googleapis.com/v1/text:synthesize"
        self.project_id = self._get_project_id()
        self.access_token = self._get_access_token()
    
    def _get_project_id(self):
        """Get current Google Cloud project ID"""
        try:
            result = subprocess.run(
                ["gcloud", "config", "list", "--format=value(core.project)"],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            print("❌ Error getting project ID. Make sure gcloud is configured.")
            return None
    
    def _get_access_token(self):
        """Get Google Cloud access token"""
        try:
            result = subprocess.run(
                ["gcloud", "auth", "print-access-token"],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            print("❌ Error getting access token. Make sure you're authenticated with gcloud.")
            return None
    
    def synthesize(self, text, voice_name="en-US-Chirp3-HD-Orus", language_code="en-US"):
        """
        Synthesize speech using Google's REST API
        
        Args:
            text (str): Text to synthesize
            voice_name (str): Voice name (e.g., "en-US-Chirp3-HD-Orus")
            language_code (str): Language code (e.g., "en-US")
        
        Returns:
            bytes: Audio data
        """
        
        if not self.project_id or not self.access_token:
            print("❌ Missing project ID or access token")
            return None
        
        # Prepare the request payload
        payload = {
            "input": {
                "text": text  # Using text instead of markup for simplicity
            },
            "voice": {
                "languageCode": language_code,
                "name": voice_name,
                "voiceClone": {}  # Empty voice clone config
            },
            "audioConfig": {
                "audioEncoding": "LINEAR16"
            }
        }
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_id,
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            # Make the request
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                # Parse the response
                result = response.json()
                
                # Decode the base64 audio content
                audio_content = base64.b64decode(result.get("audioContent", ""))
                
                print(f"✅ Successfully synthesized audio")
                print(f"📊 Audio size: {len(audio_content)} bytes")
                
                return audio_content
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return None
    
    def synthesize_and_save(self, text, filename, voice_name="en-US-Chirp3-HD-Orus"):
        """
        Synthesize speech and save to file
        
        Args:
            text (str): Text to synthesize
            filename (str): Output filename
            voice_name (str): Voice name
        """
        
        audio_content = self.synthesize(text, voice_name)
        
        if audio_content:
            with open(filename, "wb") as f:
                f.write(audio_content)
            print(f"📁 Saved to: {filename}")
            return filename
        else:
            print("❌ Failed to synthesize audio")
            return None

def demo_google_tts_rest():
    """Demo the Google TTS REST API wrapper"""
    
    print("Google Cloud TTS REST API Demo")
    print("=" * 30)
    
    # Initialize the wrapper
    tts = GoogleTTSRest()
    
    if not tts.project_id or not tts.access_token:
        print("❌ Please authenticate with gcloud:")
        print("   gcloud auth login")
        print("   gcloud config set project YOUR_PROJECT_ID")
        return
    
    print(f"✅ Project: {tts.project_id}")
    print(f"✅ Authenticated")
    
    # Test text
    test_text = "This is a test for the EMS app using Google's HD voices via REST API."
    
    # Test different HD voices
    hd_voices = [
        "en-US-Chirp3-HD-Orus",
        "en-US-Chirp3-HD-Aria", 
        "en-US-Chirp3-HD-Jenny",
        "en-US-Chirp3-HD-Guy"
    ]
    
    for voice in hd_voices:
        print(f"\n--- Testing: {voice} ---")
        
        filename = f"rest_tts_{voice.replace('-', '_').replace('/', '_')}.wav"
        
        result = tts.synthesize_and_save(test_text, filename, voice)
        
        if result:
            # If in Jupyter, play the audio
            try:
                display(Audio(filename, rate=24000, autoplay=False))
            except:
                print("🎵 Audio file created - play manually")

def ems_alert_demo():
    """Demo EMS-specific content with HD voice"""
    
    tts = GoogleTTSRest()
    
    if not tts.project_id or not tts.access_token:
        print("❌ Please authenticate with gcloud first")
        return
    
    ems_text = """
    Emergency Medical Services Alert. 
    Patient is a 45-year-old male with chest pain. 
    Vital signs: Blood pressure 140/90, heart rate 95, oxygen saturation 98%. 
    Recommend immediate transport to nearest cardiac facility.
    """
    
    print("EMS Alert Demo with HD Voice")
    print("=" * 30)
    
    filename = "ems_alert_hd_voice.wav"
    result = tts.synthesize_and_save(ems_text, filename, "en-US-Chirp3-HD-Orus")
    
    if result:
        try:
            display(Audio(filename, rate=24000, autoplay=False))
        except:
            print("🎵 EMS alert audio created")

if __name__ == "__main__":
    demo_google_tts_rest()
    print("\n" + "="*50)
    ems_alert_demo() 