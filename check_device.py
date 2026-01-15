import torch
import whisper
import os
from config import settings

log_file = "whisper_device_check.log"

def main():
    try:
        device = settings.WHISPER_DEVICE
        print(f"Loading model on {device}...")
        model = whisper.load_model(settings.WHISPER_MODEL_SIZE, device=device)
        actual_device = next(model.parameters()).device
        
        with open(log_file, "w") as f:
            f.write(f"Settings Device: {device}\n")
            f.write(f"Actual Model Device: {actual_device}\n")
            f.write(f"CUDA Available: {torch.cuda.is_available()}\n")
            
        print(f"Verification logged to {log_file}")
    except Exception as e:
        with open(log_file, "w") as f:
            f.write(f"Error: {e}\n")
        print(f"Error logged to {log_file}")

if __name__ == "__main__":
    main()
