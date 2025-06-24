"""
Google Cloud Text-to-Speech HD Voices Demo
Using the newer HD voices and voice cloning features
"""

from google.cloud import texttospeech
import os
import json
from IPython.display import Audio

def google_hd_tts_demo():
    """Demo Google's HD voices and voice cloning"""
    
    # Initialize the client
    client = texttospeech.TextToSpeechClient()
    
    # Test text
    test_text = "This is a test for the EMS app. The HD voices sound much more realistic than standard TTS."
    
    # HD Voices to test (much better quality)
    hd_voices = [
        "en-US-Chirp3-HD-Orus",      # High-quality male voice
        "en-US-Chirp3-HD-Aria",      # High-quality female voice
        "en-US-Chirp3-HD-Jenny",     # Another high-quality option
        "en-US-Chirp3-HD-Guy",       # High-quality male voice
    ]
    
    print("Google Cloud TTS HD Voices Demo")
    print("=" * 40)
    
    for voice_name in hd_voices:
        print(f"\n--- Testing HD Voice: {voice_name} ---")
        
        # Set the text input
        synthesis_input = texttospeech.SynthesisInput(text=test_text)
        
        # Build the voice request with HD voice
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=voice_name
        )
        
        # Audio config for high quality
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            sample_rate_hertz=24000  # Higher sample rate for better quality
        )
        
        # Perform the synthesis
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        # Save to file
        filename = f"google_hd_{voice_name.replace('-', '_').replace('/', '_')}.wav"
        with open(filename, "wb") as out:
            out.write(response.audio_content)
        
        print(f"✅ Generated: {filename}")
        print(f"📊 Audio size: {len(response.audio_content)} bytes")
        
        # If in Jupyter, play the audio
        try:
            display(Audio(filename, rate=24000, autoplay=False))
        except:
            print("🎵 Audio file created - play manually")

def google_voice_clone_demo():
    """Demo Google's voice cloning feature"""
    
    # Note: Voice cloning requires additional setup and permissions
    # This is a more advanced feature
    
    client = texttospeech.TextToSpeechClient()
    
    # Voice cloning example (requires voice clone setup)
    synthesis_input = texttospeech.SynthesisInput(text="This is a test of voice cloning.")
    
    # Voice with cloning parameters
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Chirp3-HD-Orus",  # Base voice
        # voice_clone=texttospeech.VoiceClone()  # Uncomment if you have voice cloning set up
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        sample_rate_hertz=24000
    )
    
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    
    filename = "google_voice_clone_test.wav"
    with open(filename, "wb") as out:
        out.write(response.audio_content)
    
    print(f"Voice clone test saved to: {filename}")

def list_google_hd_voices():
    """List available Google HD voices"""
    
    client = texttospeech.TextToSpeechClient()
    
    # Get all voices
    response = client.list_voices(language_code="en-US")
    
    print("Available Google TTS Voices (en-US):")
    print("=" * 40)
    
    hd_voices = []
    standard_voices = []
    neural_voices = []
    
    for voice in response.voices:
        if "HD" in voice.name:
            hd_voices.append(voice.name)
        elif "Neural" in voice.name:
            neural_voices.append(voice.name)
        else:
            standard_voices.append(voice.name)
    
    print("\n🎯 HD Voices (Best Quality):")
    for voice in hd_voices:
        print(f"  - {voice}")
    
    print(f"\n🧠 Neural Voices:")
    for voice in neural_voices[:5]:  # Show first 5
        print(f"  - {voice}")
    
    print(f"\n📊 Standard Voices:")
    for voice in standard_voices[:5]:  # Show first 5
        print(f"  - {voice}")
    
    print(f"\n📈 Summary:")
    print(f"  HD Voices: {len(hd_voices)}")
    print(f"  Neural Voices: {len(neural_voices)}")
    print(f"  Standard Voices: {len(standard_voices)}")

if __name__ == "__main__":
    print("Google Cloud TTS HD Voices Demo")
    print("=" * 30)
    
    # Check if credentials are set
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("❌ Google Cloud credentials not found!")
        print("Please set GOOGLE_APPLICATION_CREDENTIALS environment variable")
    else:
        print("✅ Google Cloud credentials found!")
        
        print("\n1. Listing available voices:")
        list_google_hd_voices()
        
        print("\n2. Testing HD voices:")
        google_hd_tts_demo()
        
        print("\n3. Testing voice cloning:")
        google_voice_clone_demo() 