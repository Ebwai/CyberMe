import sys
import os

print(f"Python: {sys.executable}")
print(f"Path: {sys.path}")

print("\n--- Testing torch ---")
try:
    import torch
    print(f"SUCCESS: torch imported. Version: {torch.__version__}")
    from torch import Tensor
    print("SUCCESS: Tensor imported from torch.")
except Exception:
    import traceback
    traceback.print_exc()

print("\n--- Testing yt_dlp ---")
try:
    import yt_dlp
    print("SUCCESS: yt_dlp imported.")
except Exception:
    import traceback
    traceback.print_exc()

print("\n--- Testing whisper ---")
try:
    import whisper
    print("SUCCESS: whisper imported.")
except Exception:
    import traceback
    traceback.print_exc()

print("\n--- Testing pydantic_settings ---")
try:
    import pydantic_settings
    print("SUCCESS: pydantic_settings imported.")
except Exception:
    import traceback
    traceback.print_exc()
