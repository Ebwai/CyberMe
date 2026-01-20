import asyncio
import argparse
import os
import logging
from utils.media_tool import MediaTool

# Configure logging to show info/debug in console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    parser = argparse.ArgumentParser(description="Debug Bilibili Download via MediaTool")
    parser.add_argument("input", help="Bilibili Video URL or BVID (e.g., BV1xx411c7mD)")
    args = parser.parse_args()
    
    input_val = args.input.strip()
    
    # Construct URL if it's just an ID
    if input_val.startswith("http"):
        url = input_val
    elif input_val.startswith("BV") or input_val.startswith("av"):
        url = f"https://www.bilibili.com/video/{input_val}"
    else:
        # Assume it might be a BVID without BV prefix or just try as is
        # But commonly users might paste just the hash part
        if len(input_val) > 0:
             # Try prepending BV if it looks like a BVID hash (usually 10 chars for the hash part?)
             # Actually let's just default to constructing it with the input
             url = f"https://www.bilibili.com/video/{input_val}"
    
    print(f"\n--- Debugging Bilibili Download ---")
    print(f"Target URL: {url}")
    
    # Check MediaTool
    if not MediaTool.is_available():
        print("❌ MediaTool not available (check ffmpeg/yt-dlp)")
        return

    import yt_dlp
    print(f"yt-dlp version: {yt_dlp.version.__version__}")

    # Prepare output
    output_dir = "debug_output"
    os.makedirs(output_dir, exist_ok=True)
    # Use a generic name, or try to use the ID
    filename = input_val.split("/")[-1] if "/" in input_val else input_val
    filename = filename.replace("?", "_").replace("&", "_")
    target_path = os.path.join(output_dir, f"{filename}.wav")
    
    print(f"Output Path: {target_path}")
    print("Starting download... (this may take time)")
    
    success = await MediaTool.download_audio(url, target_path)
    
    if success:
        print(f"\n✅ Download SUCCESS: {target_path}")
    else:
        print(f"\n❌ Download FAILED.")
        print("Possible reasons:")
        print("1. Network timeout (try again)")
        print("2. Video requires login (SESSDATA)")
        print("3. Invalid URL or ID")
        print("4. yt-dlp version outdated")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
