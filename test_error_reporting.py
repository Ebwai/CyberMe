import asyncio
import os
from crawlers.bilibili import BiliCrawler
from config import settings
from loguru import logger

async def test_bili_auth_failure():
    print("\n[TEST] Simulating Bilibili Auth Failure...")
    
    # Backup real settings temporarily
    old_sessdata = settings.BILI_SESSDATA
    
    try:
        # Inject invalid session data
        settings.BILI_SESSDATA = "invalid_session_data_for_testing"
        
        crawler = BiliCrawler()
        # This should trigger handle_auth_error inside fetch_new_contents
        results = await crawler.fetch_new_contents()
        
        if not results:
            print("\n[TEST] Success: Auth failure was detected and handled.")
        else:
            print("\n[TEST] Failure: Auth failure was NOT detected.")
            
    finally:
        # Restore settings
        settings.BILI_SESSDATA = old_sessdata

if __name__ == "__main__":
    asyncio.run(test_bili_auth_failure())
