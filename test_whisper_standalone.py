import os
import sys

def test_standalone():
    print("--- Standalone Whisper Test ---")
    
    # 1. Test Imports
    try:
        import yt_dlp
        import whisper
        print("Imports Successful.")
    except ImportError as e:
        print(f"Import Failed: {e}")
        return

    # 2. Test Model Loading (Dry Run)
    try:
        print("Attempting to load generic 'base' model...")
        # Note: This might try to download the model if not present.
        # We want to see if it *can* download or load.
        model = whisper.load_model("base")
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Model Load Failed: {e}")

    # 3. Test yt-dlp (Dry Run / Version)
    try:
        print(f"yt-dlp version: {yt_dlp.version.__version__}")
    except Exception as e:
        print(f"yt-dlp check failed: {e}")

if __name__ == "__main__":
    test_standalone()
