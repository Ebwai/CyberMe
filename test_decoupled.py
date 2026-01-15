import asyncio
import os
import shutil
from datetime import datetime
from config import settings
from crawlers.base import ContentItem
from utils.storage import save_content
from processor.main import process_daily_content

# Setup Test Data
TEST_BVID = "BV1oViKBeED4" 
TEST_TITLE = "Test_Decoupled_Flow_GPU"
TEST_AUTHOR = "Tester"
TEST_DATE = "2026-01-14"

async def test_collection_phase():
    print("--- [Phase 1] Collection (Simulated) ---")
    
    # Create a dummy item mimicking BiliCrawler output
    item = ContentItem(
        platform="BilibiliTest",
        id=TEST_BVID,
        title=TEST_TITLE,
        url=f"https://www.bilibili.com/video/{TEST_BVID}",
        author=TEST_AUTHOR,
        publish_time="2026-01-14 12:00:00",
        crawl_time="2026-01-14 22:00:00",
        content="Testing decoupled audio download.",
        subtitle="", # Empty to trigger audio download logic in storage
        images=[],
        video_url=f"https://www.bilibili.com/video/{TEST_BVID}",
        audio_url=f"https://www.bilibili.com/video/{TEST_BVID}" # Signals storage to download
    )
    
    # Force date to be today for main.py to pick it up, or we mock storage date.
    # storage.py uses datetime.now()
    # So we will check the folder generated.
    
    await save_content(item)
    print("Collection phase finished.")

def verify_files():
    print("--- [Phase 2] File Verification ---")
    today = datetime.now().strftime("%Y-%m-%d")
    folder_name = f"BilibiliTest_{TEST_AUTHOR}_{TEST_TITLE}"
    post_dir = os.path.join(settings.SAVE_PATH, today, "BilibiliTest", folder_name)
    
    audio_path = os.path.join(post_dir, "audio.wav")
    md_path = os.path.join(post_dir, f"{folder_name}.md")
    
    if os.path.exists(audio_path):
        print(f"[PASS] Audio file found at: {audio_path}")
    else:
        print(f"[FAIL] Audio file missing at: {audio_path}")
        return False
        
    if os.path.exists(md_path):
        print(f"[PASS] Markdown file found at: {md_path}")
        return True
    else:
        print(f"[FAIL] Markdown file missing at: {md_path}")
        return False

def test_processing_phase():
    print("--- [Phase 3] Processing (Translation) ---")
    # This will scan today's folder
    # BilibiliTest platform should be picked up if we scan recursive
    process_daily_content()
    print("Processing phase finished.")

def verify_transcript():
    print("--- [Phase 4] Transcript Verification ---")
    today = datetime.now().strftime("%Y-%m-%d")
    folder_name = f"BilibiliTest_{TEST_AUTHOR}_{TEST_TITLE}"
    post_dir = os.path.join(settings.SAVE_PATH, today, "BilibiliTest", folder_name)
    md_path = os.path.join(post_dir, f"{folder_name}.md")
    
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if "[AI-Generated Transcript]" in content:
        print("[PASS] Transcript found in Markdown.")
        print(content[-500:]) # Print last 500 chars
    else:
        print("[FAIL] Transcript NOT found in Markdown.")

async def main():
    # Cleanup previous test if exists
    today = datetime.now().strftime("%Y-%m-%d")
    folder_name = f"BilibiliTest_{TEST_AUTHOR}_{TEST_TITLE}"
    post_dir = os.path.join(settings.SAVE_PATH, today, "BilibiliTest", folder_name)
    if os.path.exists(post_dir):
        try:
            shutil.rmtree(os.path.dirname(post_dir)) # Delete BilibiliTest folder
        except:
            pass
            
    await test_collection_phase()
    if verify_files():
        test_processing_phase()
        verify_transcript()

if __name__ == "__main__":
    asyncio.run(main())
