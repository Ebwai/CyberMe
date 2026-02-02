import asyncio
import json
import aiohttp
from datetime import datetime
from typing import List
from bilibili_api import Credential, favorite_list, video, sync
from bilibili_api.user import User
from loguru import logger
from config import settings
from crawlers.base import BaseCrawler, ContentItem

class BiliCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.platform_name = "Bilibili"
        
        # Initialize Credential
        self.credential = Credential(
            sessdata=settings.BILI_SESSDATA,
            bili_jct=settings.BILI_JCT,
            buvid3=settings.BILI_BUVID3
        )
        
        # Check if media_id is provided, otherwise we might need to find the default favorites
        self.media_id = settings.BILI_MEDIA_ID

    async def _get_subtitle_text(self, bvid: str, session: aiohttp.ClientSession = None) -> str:
        """
        Fetch subtitle for a video.
        """
        try:
            v = video.Video(bvid=bvid, credential=self.credential)
            # We need the cid for subtitles. get_info() fetches it.
            info = await v.get_info()
            cid = info.get('cid')
            
            # Ensure v has cid - wait, debug script showed passing to method works best
            subtitles = await v.get_subtitle(cid=cid)
            
            if not subtitles:
                self.logger.warning(f"No subtitles found for video {bvid} (cid={cid})")
                return ""
            
            self.logger.info(f"Found subtitles for {bvid}, parsing...")
            
            # Look for zh-CN or ai-zh
            target_sub = None
            if isinstance(subtitles, dict) and 'subtitles' in subtitles:
                for sub in subtitles.get('subtitles', []):
                    if sub.get('lan') == 'zh-CN':
                        target_sub = sub
                        break
                
                if not target_sub:
                    for sub in subtitles.get('subtitles', []):
                        if sub.get('lan') == 'ai-zh':
                            target_sub = sub
                            break
                
                # If still not found, take the first one
                if not target_sub and subtitles.get('subtitles'):
                    target_sub = subtitles['subtitles'][0]
                    
            if target_sub:
                sub_url = target_sub.get('subtitle_url')
                if sub_url:
                    # Allow non-ssl if needed, but it should be fine
                    if sub_url.startswith('//'):
                        sub_url = 'https:' + sub_url
                        
                    # Fetch JSON content
                    # Use provided session or create a temp one
                    if session:
                        async with session.get(sub_url) as resp:
                            if resp.status == 200:
                                sub_data = await resp.json()
                                # Parse body
                                lines = []
                                for item in sub_data.get('body', []):
                                    lines.append(f"{item.get('content')}")
                                return "\n".join(lines)
                    else:
                        async with aiohttp.ClientSession() as temp_session:
                            async with temp_session.get(sub_url) as resp:
                                if resp.status == 200:
                                    sub_data = await resp.json()
                                    lines = []
                                    for item in sub_data.get('body', []):
                                        lines.append(f"{item.get('content')}")
                                    return "\n".join(lines)
            
            # Fallback: Audio Download for later transcription
            # If we are here, no official subtitle was found.
            # We return a specific marker or let the main loop handle the download based on subtitle emptiness.
            # However, to be explicit, we can signal that audio is needed.
            self.logger.info(f"No official subtitles for {bvid}. Audio will be downloaded for later transcription.")
            # We don't download here because we don't have the target path (which depends on title/author).
            # We return empty string, but the main loop will check and set audio_url.
            return ""

        except Exception as e:
            e_str = str(e)
            if "啥都木有" in e_str or "稿件不可见" in e_str or "-404" in e_str or "62002" in e_str:
                self.logger.warning(f"Video {bvid} is invalid/deleted: {e_str}")
                return "INVALID_VIDEO"
            self.logger.warning(f"Failed to get subtitle for {bvid}: {e}")
        
        return ""

    async def fetch_new_contents(self) -> List[ContentItem]:
        if not self.media_id:
            self.logger.error("BILI_MEDIA_ID is not set in config.")
            return []

        # Check credential validity
        if not await self.credential.check_valid():
            self.handle_auth_error("Bilibili")
            return []

        self.logger.info(f"Fetching favorites from Media ID: {self.media_id}")
        
        try:
            # Use favorite_list.get_video_favorite_list_content
            resp = await favorite_list.get_video_favorite_list_content(
                media_id=int(self.media_id),
                credential=self.credential
            )
            
            medias = resp.get('medias', [])
            if medias is None:
                # This can happen if the credential is technically valid but unauthorized for this list
                self.logger.error(f"Failed to fetch medias. Response: {resp}")
                self.handle_auth_error("Bilibili")
                return []
                
            self.logger.info(f"Got {len(medias)} items from Bili API")
            
            potential_items = []
            
            # Use a shared session for subtitles
            async with aiohttp.ClientSession() as session:
                for m in medias:
                    # m structure: {id, title, intro, cover, upper:{name, mid}, link, ctime, pubtime, bvid...}
                    title = m.get('title')
                    bvid = m.get('bvid')
                    intro = m.get('intro')
                    cover = m.get('cover')
                    upper = m.get('upper', {}).get('name')
                    ctime = m.get('ctime') # Collection time
                    pubtime = m.get('pubtime')
                    
                    # Get Subtitle
                    subtitle_text = await self._get_subtitle_text(bvid, session=session)
                    
                    is_invalid = subtitle_text == "INVALID_VIDEO"
                    if is_invalid:
                        subtitle_text = "" # Clear magic string for storage

                    # Construct Item
                    item = ContentItem(
                        platform=self.platform_name,
                        id=bvid,
                        title=title,
                        url=f"https://www.bilibili.com/video/{bvid}",
                        author=upper,
                        publish_time=str(datetime.fromtimestamp(pubtime)) if pubtime else "",
                        crawl_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        content=intro or "",
                        subtitle=subtitle_text,
                        images=[cover] if cover else [],
                        video_url=None, # Disable video download as per user request (only audio needed for transcription if no subtitle)
                        # If subtitle is empty, we trigger audio download for transcription
                        # BUT if video is invalid, we do NOT try to download audio
                        audio_url=f"https://www.bilibili.com/video/{bvid}" if (not subtitle_text and not is_invalid) else None,
                        audio_file=None # Handled by storage
                    )
                    potential_items.append(item)
                
            # Filter existing locally and globally (Sync-Point)
            from utils.state_manager import StateManager
            limit_id = StateManager.get_last_latest_id(self.platform_name)
            new_items = self.filter_existing(potential_items, limit_id)
            return new_items

        except Exception as e:
            self.logger.error(f"Error fetching Bilibili favorites: {e}")
            return []
