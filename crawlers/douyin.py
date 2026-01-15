from typing import List, Optional
from playwright.async_api import async_playwright, Page, Response
from loguru import logger
from config import settings
from crawlers.base import BaseCrawler, ContentItem
import json
import asyncio
from datetime import datetime

class DouyinCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.platform_name = "Douyin"
        self.cookies = self._parse_cookies(settings.DOUYIN_COOKIE)

    def _parse_cookies(self, cookie_str: str) -> List[dict]:
        cookies = []
        if not cookie_str:
            return cookies
        for item in cookie_str.split(';'):
            if '=' in item:
                k, v = item.strip().split('=', 1)
                cookies.append({'name': k, 'value': v, 'domain': '.douyin.com', 'path': '/'})
        return cookies

    async def fetch_new_contents(self) -> List[ContentItem]:
        self.logger.info("Starting Douyin crawl...")
        
        async with async_playwright() as p:
            # Launch browser
            # headless=True is default, but sometimes False helps with anti-bot
            # using chromium
            browser = await p.chromium.launch(headless=True, args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ])
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080},
                device_scale_factor=1,
            )
            
            # Add cookies
            if self.cookies:
                await context.add_cookies(self.cookies)
            
            page = await context.new_page()
            
            # Add stealth scripts if needed (e.g. override navigator.webdriver)
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            # We need to capture the response from the favorites API
            # API Pattern: /aweme/v1/web/aweme/list/
            # or /aweme/v1/web/aweme/favorite/
            
            captured_data = []

            async def handle_response(response: Response):
                url = response.url
                # Log all API calls for debugging at DEBUG level
                if "aweme" in url or "web" in url:
                    self.logger.debug(f"Intercepted URL: {url[:120]}")
                    
                if "aweme/v1/web/" in url:
                    status = response.status
                    self.logger.info(f"CAPTURED potential target: {url[:100]} (Status: {status})")
                    try:
                        content_type = response.headers.get('content-type', '')
                        if 'json' in content_type:
                            data = await response.json()
                            if 'aweme_list' in data:
                                captured_data.extend(data['aweme_list'])
                                self.logger.info(f"Captured {len(data['aweme_list'])} items from network")
                            else:
                                self.logger.debug(f"JSON captured but no 'aweme_list'. Keys: {list(data.keys())}")
                    except Exception as e:
                        err_msg = str(e)
                        # Suppress noisy Playwright protocol errors when target is closed/busy
                        if "Protocol error" in err_msg or "Target closed" in err_msg or "No resource with given identifier" in err_msg:
                            self.logger.debug(f"Ignored protocol error: {err_msg}")
                        else:
                            self.logger.error(f"Error parsing API response: {e}")

            page.on("response", handle_response)

            try:
                # Step 1: Just go to Douyin home to ensure cookies/session
                # Use domcontentloaded for faster load, avoid networkidle timeout
                self.logger.info("Navigating to Douyin Home...")
                await page.goto("https://www.douyin.com/", wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(3)
                
                # Step 2: Navigate to favorites
                self.logger.info("Navigating to Favorites...")
                await page.goto("https://www.douyin.com/user/self?showTab=favorite_collection", wait_until="domcontentloaded", timeout=30000)
                
                # Check if redirected to login
                current_url = page.url
                if "login" in current_url or "passport" in current_url:
                    self.handle_auth_error("Douyin")
                    await browser.close()
                    return []
                
                # Wait longer for content to load
                self.logger.info("Waiting for data capture (10 seconds)...")
                await asyncio.sleep(10)
                
                # Also try to scroll a bit to trigger lazy loading if needed
                self.logger.info("Scrolling to trigger lazy load...")
                for i in range(5):
                    self.logger.info(f"Scrolling {i+1}/5...")
                    await page.evaluate("window.scrollBy(0, 500)")
                    await asyncio.sleep(2)
                
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(5)
                
                # Log captured data count
                self.logger.info(f"Total captured items from network: {len(captured_data)}")
                
            except Exception as e:
                self.logger.error(f"Error during Playwright navigation: {e}")
            finally:
                await browser.close()
                
            # Process captured data
            potential_items = []
            for aweme in captured_data:
                try:
                    aweme_id = aweme.get('aweme_id')
                    desc = aweme.get('desc')
                    create_time = aweme.get('create_time')
                    author_name = aweme.get('author', {}).get('nickname')
                    
                    # Video URL
                    # aweme['video']['play_addr']['url_list'][0] usually has watermark
                    # We might want the web link
                    video_web_url = f"https://www.douyin.com/video/{aweme_id}"
                    
                    # Try to find caption
                    subtitle_text = ""
                    if 'video' in aweme and 'caption_info' in aweme['video']:
                        # It might be a URL to subtitle file or complex structure
                        caption_info = aweme['video']['caption_info']
                        # Need to investigate structure. Often it's simple text or url.
                        # For now, placeholder.
                        pass
                        
                    # Images (SlideMode)
                    images = []
                    if aweme.get('images'):
                        for img in aweme['images']:
                            if img and img.get('url_list'):
                                images.append(img['url_list'][-1]) # Best quality
                                
                    item = ContentItem(
                        platform=self.platform_name,
                        id=aweme_id,
                        title=desc[:50] if desc else "No Title", # Douyin has no title, just desc
                        url=video_web_url,
                        author=author_name,
                        publish_time=str(datetime.fromtimestamp(create_time)) if create_time else "",
                        content=desc,
                        subtitle=subtitle_text,
                        images=images,
                        video_url=video_web_url 
                    )
                    potential_items.append(item)
                except Exception as e:
                    self.logger.warning(f"Error parsing Douyin item: {e}")

            from utils.state_manager import StateManager
            limit_id = StateManager.get_last_latest_id(self.platform_name)
            return self.filter_existing(potential_items, limit_id)
