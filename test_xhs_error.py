import asyncio
from crawlers.xhs import XHSCrawler
from loguru import logger

async def test_xhs_connection_failure():
    print("\n[TEST] Simulating XHS Connection (Proxy/SSL) Failure...")
    
    crawler = XHSCrawler()
    
    # Monkeypatch the API call to raise a ProxyError-like Exception
    original_get_info = crawler.api.get_user_self_info2
    
    def mocked_get_info(*args, **kwargs):
        raise Exception("requests.exceptions.ProxyError: Max retries exceeded with url...")
    
    crawler.api.get_user_self_info2 = mocked_get_info
    
    try:
        results = await crawler.fetch_new_contents()
        if not results:
            print("\n[TEST] Success: XHS Connection error was detected and handled with tips.")
    except Exception as e:
        print(f"\n[TEST] Error: Test failed with unexpected exception: {e}")
    finally:
        crawler.api.get_user_self_info2 = original_get_info

if __name__ == "__main__":
    asyncio.run(test_xhs_connection_failure())
