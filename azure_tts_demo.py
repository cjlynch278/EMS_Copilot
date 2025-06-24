"""
Azure Cognitive Services Text-to-Speech Demo
Azure has some of the most realistic TTS voices available!
"""

import azure.cognitiveservices.speech as speechsdk
import os
import tempfile
from IPython.display import Audio
import time

def azure_tts_demo():
    """Demo Azure TTS with realistic voices"""
    
    # You'll need to set these environment variables or replace with your actual values
    # Get these from Azure Portal -> Cognitive Services -> Speech Service
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    service_region = os.getenv("AZURE_SPEECH_REGION")  # e.g., "eastus", "westus2"
    
    if not speech_key or not service_region:
        print("Please set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables")
        print("Get these from Azure Portal -> Cognitive Services -> Speech Service")
        return
    
    # Initialize speech config
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, 
        region=service_region
    )
    
    # Set audio output format
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
    )
    
    # Test different realistic voices
    voices_to_test = [
        # Neural voices (most realistic)
        "en-US-JennyNeural",      # Female, very natural
        "en-US-GuyNeural",        # Male, very natural
        "en-US-AriaNeural",       # Female, professional
        "en-US-DavisNeural",      # Male, professional
        "en-US-SaraNeural",       # Female, friendly
        "en-US-TonyNeural",       # Male, friendly
        
        # Standard voices (still good)
        "en-US-JennyMultilingualNeural",  # Multilingual
        "en-US-RyanMultilingualNeural",   # Multilingual
    ]
    
    test_text = "Hello! This is a test of Azure's incredibly realistic text-to-speech voices. The neural voices sound remarkably human-like and natural."
    
    print("Azure TTS Demo - Testing Realistic Voices")
    print("=" * 50)
    
    for voice_name in voices_to_test:
        print(f"\n--- Testing: {voice_name} ---")
        
        # Set the voice
        speech_config.speech_synthesis_voice_name = voice_name
        
        # Create speech synthesizer
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        
        # Synthesize speech
        result = speech_synthesizer.speak_text_async(test_text).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"✅ Success! Audio synthesized with {voice_name}")
            
            # Save to file
            filename = f"azure_tts_{voice_name.replace('-', '_')}.wav"
            
            # Get audio data and save
            audio_data = result.audio_data
            with open(filename, "wb") as f:
                f.write(audio_data)
            
            print(f"📁 Saved to: {filename}")
            print(f"📊 Audio size: {len(audio_data)} bytes")
            
            # If running in Jupyter, you can play it directly
            try:
                display(Audio(filename, autoplay=False))
            except:
                print("🎵 Audio file created - play it manually")
                
        else:
            print(f"❌ Failed: {result.reason}")
            if result.cancellation_details:
                print(f"   Error: {result.cancellation_details.reason}")
                print(f"   Details: {result.cancellation_details.error_details}")

def azure_tts_simple(text, voice_name="en-US-JennyNeural"):
    """Simple function to convert text to speech with Azure"""
    
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    service_region = os.getenv("AZURE_SPEECH_REGION")
    
    if not speech_key or not service_region:
        print("Please set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION")
        return None
    
    # Configure speech
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, 
        region=service_region
    )
    speech_config.speech_synthesis_voice_name = voice_name
    
    # Create synthesizer
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    
    # Synthesize
    result = speech_synthesizer.speak_text_async(text).get()
    
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return result.audio_data
    else:
        print(f"Error: {result.reason}")
        return None

def list_azure_voices():
    """List available Azure voices"""
    
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    service_region = os.getenv("AZURE_SPEECH_REGION")
    
    if not speech_key or not service_region:
        print("Please set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION")
        return
    
    # Create speech config
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, 
        region=service_region
    )
    
    # Create speech synthesizer
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    
    # Get voices
    voices = speech_synthesizer.get_voices_async("en-US").get()
    
    print("Available Azure Voices (en-US):")
    print("=" * 40)
    
    neural_voices = []
    standard_voices = []
    
    for voice in voices.voices:
        if "Neural" in voice.name:
            neural_voices.append(voice.name)
        else:
            standard_voices.append(voice.name)
    
    print("\n🧠 Neural Voices (Most Realistic):")
    for voice in neural_voices[:10]:  # Show first 10
        print(f"  - {voice}")
    
    print(f"\n📊 Total Neural voices: {len(neural_voices)}")
    print(f"📊 Total Standard voices: {len(standard_voices)}")

if __name__ == "__main__":
    print("Azure TTS Demo")
    print("=" * 20)
    
    # Check if credentials are set
    if not os.getenv("AZURE_SPEECH_KEY") or not os.getenv("AZURE_SPEECH_REGION"):
        print("\n❌ Azure credentials not found!")
        print("\nTo use Azure TTS, you need:")
        print("1. Azure Speech Service (create in Azure Portal)")
        print("2. Set environment variables:")
        print("   export AZURE_SPEECH_KEY='your_key_here'")
        print("   export AZURE_SPEECH_REGION='eastus'")
        print("\nOr set them in your Python code:")
        print("   os.environ['AZURE_SPEECH_KEY'] = 'your_key_here'")
        print("   os.environ['AZURE_SPEECH_REGION'] = 'eastus'")
    else:
        print("✅ Azure credentials found!")
        print("\n1. List available voices:")
        list_azure_voices()
        
        print("\n2. Test realistic voices:")
        azure_tts_demo() 