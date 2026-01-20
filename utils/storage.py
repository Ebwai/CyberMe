import os
import asyncio
import aiohttp
import aiofiles
from datetime import datetime
from loguru import logger
from jinja2 import Template
from config import settings
from crawlers.base import ContentItem
from utils.media_tool import MediaTool

import re

def sanitize_filename(name: str) -> str:
    return "".join([c for c in name if c.isalnum() or c in (' ', '-', '_')]).strip()

MARKDOWN_TEMPLATE = """---
title: {{ item.title }}
url: {{ item.url }}
author: {{ item.author }}
platform: {{ item.platform }}
publish_time: {{ item.publish_time }}
crawl_time: {{ item.crawl_time }}
tags: {{ item.tags }}
---
# {{ item.title }}
> 作者: {{ item.author }}  发布时间: {{ item.publish_time }}  [查看原文]({{ item.url }})

{% if image_paths %}
{% for img_path in image_paths %}
![图{{ loop.index }}]({{ img_path }})
{% endfor %}
{% endif %}

## 简介/正文
{{ item.content }}

## 字幕/文稿
{% if item.subtitle %}
{{ item.subtitle }}
{% elif audio_path %}
[PENDING_TRANSCRIPTION] Audio saved to `{{ audio_path }}`.
{% endif %}
"""

async def download_asset(session, url: str, filepath: str, headers: dict = None) -> bool:
    if not url:
        return False
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                async with aiofiles.open(filepath, mode='wb') as f:
                    await f.write(await response.read())
                return True
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
    return False

async def save_content(item: ContentItem, skip_markdown: bool = False) -> str:
    """
    Save content to disk.
    Returns:
        "success": Metadata and all assets saved successfully.
        "partial": Metadata saved (or skipped), but some assets failed.
        "fail": Critical failure (metadata save failed).
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    # F:\DataInput\2026-01-13\Douyin\
    base_dir = os.path.join(settings.SAVE_PATH, today_str, item.platform)
    
    # Safe filename
    safe_title = sanitize_filename(item.title)
    safe_author = sanitize_filename(item.author)
    
    # New Structure: F:\DataInput\YYYY-MM-DD\Platform\Author_Title\
    # truncate title if too long to avoid path length issues
    folder_name = f"{item.platform}_{safe_author}_{safe_title}"[:200]
    
    post_dir = os.path.join(settings.SAVE_PATH, today_str, item.platform, folder_name)
    assets_dir = os.path.join(post_dir, "assets")
    
    os.makedirs(assets_dir, exist_ok=True)
    
    # Track success of critical components
    # We consider audio/video download failure as "incomplete crawl" if they were present
    all_success = True

    # Process Images
    image_paths = []
    if item.images:
        async with aiohttp.ClientSession() as session:
             tasks = []
             for i, img_url in enumerate(item.images):
                 ext = "jpg"
                 # Try to guess extension or default to jpg
                 if ".png" in img_url: ext = "png"
                 elif ".webp" in img_url: ext = "webp"
                 elif ".gif" in img_url: ext = "gif" # Added gif
                 
                 filename = f"img_{i}.{ext}"
                 filepath = os.path.join(assets_dir, filename)
                 
                 # Add task
                 tasks.append(download_asset(session, img_url, filepath, item.download_headers))
                 
                 # Store relative path for markdown
                 image_paths.append(f"assets/{filename}")
                 
             # Run downloads
             await asyncio.gather(*tasks)
    
    # Process Audio (If needed - Bilibili fallback)
    audio_rel_path = None
    if item.audio_url:
        audio_filename = "audio.wav" # Default to wav, MediaTool might convert
        audio_filepath = os.path.join(post_dir, audio_filename)
        
        # Download audio using MediaTool
        # We pass the full path. MediaTool handles it.
        success = await MediaTool.download_audio(item.audio_url, audio_filepath)
        if success:
            audio_rel_path = audio_filename
            # Mark as pending transcription in UI/Markdown if needed, 
            # but the existence of the file triggers the processor.
        else:
            logger.error(f"Failed to download audio for {item.id}")
            all_success = False

    # Process Video (If needed - XHS video notes)
    video_rel_path = None
    if item.video_url:
        video_filename = "video.mp4"
        video_filepath = os.path.join(post_dir, video_filename)
        
        # Use MediaTool (yt-dlp) for robust video downloading
        # This handles both webpage URLs (Bilibili/Douyin) and direct links (XHS)
        success = await MediaTool.download_video(item.video_url, video_filepath)
        
        if success:
            video_rel_path = video_filename
            logger.info(f"Downloaded video: {video_filename}")
        else:
            logger.warning(f"Failed to download video from {item.video_url}")
            all_success = False

    # Render Markdown
    if not skip_markdown:
        template = Template(MARKDOWN_TEMPLATE)
        
        context = {
            "item": item,
            "image_paths": image_paths,
            "audio_path": audio_rel_path
        }
        
        md_content = template.render(context)
        
        # Save Markdown
        output_filename = f"{folder_name}.md"
        output_path = os.path.join(post_dir, output_filename)
        
        try:
            async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
                await f.write(md_content)
            logger.info(f"Saved content to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save markdown to {output_path}: {e}")
            return "fail"
    else:
        logger.info(f"Skipping markdown save for {item.id} (Asset-only mode)")

    if all_success:
        return "success"
    else:
        return "partial"
