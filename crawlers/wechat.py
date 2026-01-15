import os
from typing import List, Optional
from config import settings
from crawlers.base import BaseCrawler, ContentItem
from loguru import logger
from playwright.async_api import async_playwright
import aiofiles
import html2text

class WeChatCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.platform_name = "WeChat"
        self.urls_file = settings.WECHAT_URLS_FILE
        self.db_path = settings.WECHAT_DB_PATH
        
    async def _fetch_from_urls_file(self) -> List[str]:
        urls = []
        if os.path.exists(self.urls_file):
            async with aiofiles.open(self.urls_file, 'r', encoding='utf-8') as f:
                async for line in f:
                    line = line.strip()
                    if line and line.startswith('http'):
                        urls.append(line)
        else:
            self.logger.warning(f"URLs file not found: {self.urls_file}")
        return urls
        
    async def _parse_article(self, page, url) -> Optional[ContentItem]:
        try:
            await page.goto(url)
            # Parse content
            # WeChat articles usually: #activity-name (Title), #js_name (Author), #js_content (Body)
            title = await page.inner_text("#activity-name")
            author = await page.inner_text("#js_name")
            
            # Get HTML content
            content_html = await page.inner_html("#js_content")
            
            # Convert to Markdown
            h = html2text.HTML2Text()
            h.ignore_links = False
            content_md = h.handle(content_html)
            
            publish_time = "" # Hard to extract reliable publish time without digging into JS vars
            
            # Extract publish time if possible (var ct = "...")
            try:
                publish_timestamp = await page.evaluate("() => { return window.ct || 0 }")
                if publish_timestamp:
                    from datetime import datetime
                    publish_time = str(datetime.fromtimestamp(int(publish_timestamp)))
            except:
                pass

            return ContentItem(
                platform=self.platform_name,
                id=url.split('/')[-1], # Use last part of URL as ID approx
                title=title.strip(),
                url=url,
                author=author.strip(),
                publish_time=publish_time,
                content=content_md,
                subtitle=None,
                images=[], # Images are inside markdown
                video_url=None
            )
        except Exception as e:
            self.logger.error(f"Error parsing Wechat url {url}: {e}")
            return None

    async def fetch_new_contents(self) -> List[ContentItem]:
        # 1. Try DB (Not implemented fully as it requires SQLCipher keys)
        if self.db_path:
            self.logger.warning("Local DB parsing not fully implemented. Skipping.")
        
        # 2. Try URLs file
        urls = await self._fetch_from_urls_file()
        if not urls:
            return []
            
        items = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            for url in urls:
                item = await self._parse_article(page, url)
                if item:
                    items.append(item)
            
            await browser.close()

        # Clear file after processing? Or keep and let filter_existing handle it?
        # Better to keep, filter_existing will skip.
        # But if file grows too big, we might want to archive it.
        # For now, just read.
        
        from utils.state_manager import StateManager
        limit_id = StateManager.get_last_latest_id(self.platform_name)
        return self.filter_existing(items, limit_id)

from typing import Optional
