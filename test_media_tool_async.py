import asyncio
import sys
import logging
from utils.media_tool import MediaTool

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

async def main():
    print("--- Async MediaTool Test ---")
    
    # 1. Check Availability
    if MediaTool.is_available():
        print("MediaTool is AVAILABLE.")
    else:
        print("MediaTool is NOT AVAILABLE.")
        return

    # 2. Test Transcription (Async)
    test_url = "https://www.bilibili.com/video/BV1oViKBeED4"
    test_id = "test_async_verify"
    
    print(f"Testing URL: {test_url}")
    print("monitor: Calling transcribe...")
    
    try:
        text = await MediaTool.transcribe(test_url, test_id)
        print("monitor: Transcribe returned.")
        
        if text:
            print("SUCCESS: Transcription result obtained.")
            print(f"Preview: {text[:50]}...")
        else:
            print("FAILURE: Transcription returned empty string.")
            
    except Exception as e:
        print(f"FAILURE: Exception during transcribe: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
