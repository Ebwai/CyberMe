import asyncio
import os
import shutil
from utils.media_tool import MediaTool
from config import settings

# Force using the correct Environment paths if needed, 
# but relying on the runtime python to have the libs installed.

async def test_transcription():
    print("--- Starting MediaTool Integration Test ---")
    
    # Ensure directories exist
    os.makedirs(settings.WHISPER_MODEL_DIR, exist_ok=True)
    os.makedirs(settings.TEMP_AUDIO_DIR, exist_ok=True)
    
    # 1. Initialize Tool
    if MediaTool.is_available():
        print("MediaTool is AVAILABLE.")
    else:
        print("MediaTool is NOT AVAILABLE (Modules missing or disabled).")
        return

    # 2. Test Audio Download & Transcribe
    test_url = "https://www.bilibili.com/video/BV1oViKBeED4" 
    test_id = "test_audio_verification_dialogue"
    
    print(f"Testing with URL: {test_url}")
    
    print("Step 1: Downloading Audio...")
    audio_path = await MediaTool.download_audio(test_url, test_id)
    if audio_path:
        print(f"Audio downloaded to: {audio_path}")
        
        print("Step 2: Transcribing...")
        # Note: In actual code we use the wrapper transcribe(url, id)
        # But here we can call model.transcribe directly if we want to bypass cleanup temporarily 
        # or just use the classmethod.
        text = await MediaTool.transcribe(test_url, test_id)
        print(f"Transcription Result: {text[:100]}...") 
        
        print("Test Complete.")
    else:
        print("Audio download failed.")

if __name__ == "__main__":
    asyncio.run(test_transcription())
