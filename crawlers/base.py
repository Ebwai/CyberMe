from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
import os
from loguru import logger
from config import settings

@dataclass
class ContentItem:
    platform: str
    id: str
    title: str
    url: str
    author: str
    publish_time: Optional[str] = None
    crawl_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content: str = "" # Main text content or description
    subtitle: Optional[str] = None # Subtitle text for videos
    images: List[str] = None # List of image URLs
    video_url: Optional[str] = None # Direct video URL if available
    audio_url: Optional[str] = None # URL to download audio from (for transcription)
    audio_file: Optional[str] = None # Local path to saved audio file
    tags: List[str] = None
    download_headers: dict = None

    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.tags is None:
            self.tags = []

class BaseCrawler(ABC):
    def __init__(self):
        self.platform_name = "Base"
        self.logger = logger.bind(platform=self.platform_name)

    @abstractmethod
    async def fetch_new_contents(self) -> List[ContentItem]:
        """
        Fetch newly added content from favorites.
        Should handle incremental checks.
        """
        pass
    
    def filter_existing(self, items: List[ContentItem], limit_id: str = None) -> List[ContentItem]:
        """
        Filter out items that have already been processed.
        1. Globally via limit_id (Sync-Point).
        2. Locally via file existence check (Backup).
        """
        # Phase 1: Global Truncation (Order-based)
        # If we encounter the limit_id, everything after it is "old" and can be ignored
        if limit_id:
            truncated_items = []
            found_limit = False
            for item in items:
                if str(item.id) == str(limit_id):
                    self.logger.info(f"Reached sync-point ID: {limit_id}. Stopping further processing.")
                    found_limit = True
                    break
                truncated_items.append(item)
            items = truncated_items

        # Phase 2: Local File Existence Check (Redundancy)
        new_items = []
        today_str = datetime.now().strftime("%Y-%m-%d")
        base_dir = os.path.join(settings.SAVE_PATH, today_str)
        
        if not os.path.exists(base_dir):
            return items

        for item in items:
            # Simple check based on filename convention
            # Filename: [Platform]_[Author]_[Title].md
            # We need to sanitize filename
            safe_title = "".join([c for c in item.title if c.isalnum() or c in (' ', '-', '_')]).strip()
            safe_author = "".join([c for c in item.author if c.isalnum() or c in (' ', '-', '_')]).strip()
            folder_name = f"{item.platform}_{safe_author}_{safe_title}"[:200]
            # Check for the post directory
            post_dir = os.path.join(base_dir, item.platform, folder_name)
            
            if not os.path.exists(post_dir):
                new_items.append(item)
            else:
                self.logger.debug(f"Skipping existing item: {item.title}")
                
        return new_items

    def handle_auth_error(self, platform: str):
        """
        Output a highly visible error message for authentication failures.
        """
        print("\n" + "="*60)
        print(f"❌  【{platform}】 身份验证失效或未授权！")
        print("="*60)
        print(f"原因详情: 检测到 Cookie 过期或账号未登录，导致无法获取收藏夹内容。")
        print(f"解决办法: 请查看项目根目录下的 [README_CONFIG.md] 文件，")
        print(f"         按照其中的步骤重新获取并更新 .env 文件中的 {platform} 相关配置。")
        print("="*60 + "\n")
        self.logger.error(f"{platform} authentication failed. User intervention required.")
