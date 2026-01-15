import sys
import os
from typing import List, Optional
from config import settings
from crawlers.base import BaseCrawler, ContentItem
from loguru import logger
from datetime import datetime
import asyncio

# Prevent requests from using system proxies that might be misconfigured
os.environ['NO_PROXY'] = '*'

# Add Spider_XHS to sys.path
XHS_PROJECT_PATH = r"f:\project\spider_Unit\local_knowledge_base\Spider_XHS"
if XHS_PROJECT_PATH not in sys.path:
    sys.path.append(XHS_PROJECT_PATH)

# Use absolute paths for JS files - patched in xhs_util.py, but chdir helps for requires
old_cwd = os.getcwd()
os.chdir(XHS_PROJECT_PATH)
try:
    from apis.xhs_pc_apis import XHS_Apis
except ImportError as e:
    logger.error(f"Failed to import Spider_XHS modules. Check path: {XHS_PROJECT_PATH}. Error: {e}")
    XHS_Apis = None
finally:
    os.chdir(old_cwd)

class XHSCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.platform_name = "Xiaohongshu"
        self.cookies = settings.XHS_COOKIE
        if XHS_Apis:
            self.api = XHS_Apis()
        else:
            self.logger.warning("XHS API not initialized")
            self.api = None
        
        self.user_id = None # Cached User ID

    async def _get_my_user_id(self):
        if self.user_id:
            return self.user_id
        
        try:
            success, msg, data = self.api.get_user_self_info2(self.cookies)
            if success and data and "data" in data:
                 self.user_id = data["data"].get("user_id")
                 self.logger.info(f"Identified XHS User ID: {self.user_id}")
                 return self.user_id
            else:
                if "登录" in msg or "Unauthorized" in msg or "未授权" in msg:
                    self.handle_auth_error("Xiaohongshu")
                else:
                    self.logger.error(f"Failed to get XHS user info: {msg}")
                return None
        except Exception as e:
            err_msg = str(e)
            if "ProxyError" in err_msg or "SSLError" in err_msg:
                print("\n" + "!"*60)
                print(f"⚠️  【Xiaohongshu】 网络连接失败（Proxy/SSL Error）")
                print("!"*60)
                print(f"原因详情: 可能是系统代理设置冲突或 SSL 证书验证失败。")
                print(f"解决办法: 请检查 Windows 系统代理设置，并确保环境变量已禁用不必要的代理。")
                print(f"         当前代码已通过 os.environ['NO_PROXY'] = '*' 尝试规避。")
                print("!"*60 + "\n")
            self.logger.error(f"XHS API Connection failed: {e}")
            return None

    async def fetch_new_contents(self) -> List[ContentItem]:
        if not self.api:
            return []
            
        # Change directory to XHS project root to allow JS module resolution (static/...)
        old_cwd = os.getcwd()
        os.chdir(XHS_PROJECT_PATH)
        
        try:
            user_id = await self._get_my_user_id()
            if not user_id:
                return []

            self.logger.info(f"Fetching XHS favorites for user {user_id}...")
            
            # Fetch first page of collections
            success, msg, res_json = self.api.get_user_collect_note_info(user_id, "", self.cookies)
            
            if not success:
                self.logger.error(f"Failed to fetch XHS collections: {msg}")
                return []
                
            notes = res_json.get("data", {}).get("notes", [])
            self.logger.info(f"Got {len(notes)} items from XHS API")
            
            potential_items = []
            potential_items = []
            for note in notes:
                note_id = note.get("note_id")
                title = note.get("display_title")
                
                # Extract Cover
                cover_dict = note.get("cover", {})
                cover_url = None
                if "info_list" in cover_dict and cover_dict["info_list"]:
                    cover_url = cover_dict["info_list"][0].get("url")
                if not cover_url:
                    cover_url = cover_dict.get("url_default")
                
                author = note.get("user", {}).get("nickname")
                
                content_desc = title # Default
                images = [cover_url] if cover_url else []
                video_url = None
                
                try:
                    note_url = f"https://www.xiaohongshu.com/explore/{note_id}"
                    xsec_token = note.get("xsec_token", "")
                    full_query_url = f"{note_url}?xsec_token={xsec_token}"
                    
                    det_success, det_msg, det_data = self.api.get_note_info(full_query_url, self.cookies)
                    
                    if det_success:
                        note_data = det_data.get("data", {}).get("items", {})[0].get("note_card", {})
                        content_desc = note_data.get("desc", content_desc)
                        title = note_data.get("title", title)
                        img_list = note_data.get("image_list", [])
                        if img_list:
                             images = []
                             for img in img_list:
                                 url = None
                                 if "info_list" in img and img["info_list"]:
                                     url = img["info_list"][0].get("url")
                                 if not url:
                                     url = img.get("url_default")
                                 if url:
                                     images.append(url)
                        
                        if note_data.get("type") == "video":
                            try:
                                video_dict = note_data.get("video", {}).get("media", {})
                                stream = video_dict.get("stream", {}).get("h264", [])
                                if stream:
                                    video_url = stream[0].get("master_url")
                            except:
                                pass
                                
                except Exception as e:
                    self.logger.warning(f"Failed to get details for note {note_id}: {e}")

                item = ContentItem(
                    platform=self.platform_name,
                    id=note_id,
                    title=title,
                    url=f"https://www.xiaohongshu.com/explore/{note_id}",
                    author=author,
                    publish_time="",
                    crawl_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    content=content_desc,
                    subtitle=None,
                    images=images,
                    video_url=video_url,
                    download_headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Referer": "https://www.xiaohongshu.com/"
                    }
                )
                potential_items.append(item)
                await asyncio.sleep(1)

            from utils.state_manager import StateManager
            limit_id = StateManager.get_last_latest_id(self.platform_name)
            return self.filter_existing(potential_items, limit_id)
        finally:
            os.chdir(old_cwd)
