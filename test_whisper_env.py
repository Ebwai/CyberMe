import sys
import os
import subprocess

def check_env():
    print(f"Python Executable: {sys.executable}")
    
    # Check Imports
    try:
        import yt_dlp
        print("SUCCESS: yt_dlp imported.")
    except ImportError as e:
        print(f"FAILURE: yt_dlp import failed: {e}")

    try:
        import whisper
        print("SUCCESS: whisper imported.")
    except ImportError as e:
        print(f"FAILURE: whisper import failed: {e}")

    # Check FFmpeg
    try:
        # Check if ffmpeg is in path
        result = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
        if result.returncode == 0:
            print("SUCCESS: ffmpeg found in PATH.")
            print(result.stdout.split('\n')[0])
        else:
            print("FAILURE: ffmpeg returned non-zero exit code.")
    except FileNotFoundError:
        print("FAILURE: ffmpeg not found in PATH.")
    except Exception as e:
        print(f"FAILURE: ffmpeg check error: {e}")

if __name__ == "__main__":
    check_env()
