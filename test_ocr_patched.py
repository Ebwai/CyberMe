import torch
import builtins
import os

# Save the original load
original_load = torch.load

def patched_load(f, map_location=None, pickle_module=builtins, **kwargs):
    # Remove weights_only if present
    if 'weights_only' in kwargs:
        print(f"DEBUG: intercepted weights_only={kwargs['weights_only']}")
        del kwargs['weights_only']
    return original_load(f, map_location=map_location, pickle_module=pickle_module, **kwargs)

# Apply patch
torch.load = patched_load

import easyocr

MODELS_DIR = r"F:\Spider_proj\models"
os.makedirs(MODELS_DIR, exist_ok=True)

try:
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"Initializing reader with models_dir={MODELS_DIR}")
    reader = easyocr.Reader(['ch_sim', 'en'], gpu=torch.cuda.is_available(), model_storage_directory=MODELS_DIR)
    print("Reader initialized successfully!")
    
    # Test path
    test_img = r"F:\DataInput\2026-01-14\Xiaohongshu\Xiaohongshu_麦克斯坦_推荐一个快速提升提示词能力的方法\assets\img_0.jpg"
    if os.path.exists(test_img):
        print(f"Testing image: {test_img}")
        result = reader.readtext(test_img, detail=0)
        print("OCR Result:")
        print("\n".join(result))
    else:
        print(f"Test image not found at {test_img}")
        
except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()
