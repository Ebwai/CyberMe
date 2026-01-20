import os
import json
import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import aiohttp
from loguru import logger
from config import settings
from utils.storage import save_content
from crawlers.base import ContentItem
from crawlers.bilibili import BiliCrawler
from crawlers.xhs import XHSCrawler
from crawlers.douyin import DouyinCrawler
from crawlers.wechat import WeChatCrawler
from bilibili_api import favorite_list
import argparse
import sys

STATE_FILE = os.path.join(settings.SAVE_PATH, "backfill_state.json")

class BackfillState:
    def __init__(self, path: str):
        self.path = path
        self.state: Dict[str, Any] = {}
        self._load()
    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.state = json.load(f)
            except Exception:
                self.state = {}
        else:
            self.state = {}
    def get(self, platform: str) -> Dict[str, Any]:
        return self.state.get(platform, {})
    def update(self, platform: str, data: Dict[str, Any]):
        self.state[platform] = data
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=4, ensure_ascii=False)

async def backfill_bilibili(limit: int, state: BackfillState):
    crawler = BiliCrawler()
    if not crawler.media_id:
        logger.error("Bilibili MEDIA_ID 未配置")
        return
    if not await crawler.credential.check_valid():
        crawler.handle_auth_error("Bilibili")
        return
    ps = 20
    media_count = 0
    sessdata = settings.BILI_SESSDATA or ""
    bili_jct = settings.BILI_JCT or ""
    buvid3 = settings.BILI_BUVID3 or ""
    cookie_str = "; ".join([f"SESSDATA={sessdata}", f"bili_jct={bili_jct}", f"buvid3={buvid3}"]).strip("; ")
    # 获取总数（优先走官方 Web API; 若权限不足则提示并退出）
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                "media_id": int(crawler.media_id),
                "platform": "web",
                "order": "mtime",
                "type": 0,
                "tid": 0,
                "pn": 1,
                "ps": ps,
            }
            async with session.get(
                "https://api.bilibili.com/x/v3/fav/resource/list",
                params=params,
                headers={
                    "Cookie": cookie_str,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Origin": "https://www.bilibili.com",
                    "Referer": "https://www.bilibili.com/",
                },
            ) as resp:
                ct = resp.headers.get("content-type", "")
                if "json" not in ct:
                    text = await resp.text()
                    logger.error(f"Bilibili 总数获取失败: 非JSON响应，HTTP {resp.status}，可能权限不足。")
                    return
                data = await resp.json()
                code = int(data.get("code", 0))
                if code != 0:
                    msg = data.get("message")
                    logger.error(f"Bilibili 总数获取失败: code={code}, message={msg}")
                    return
                info = ((data or {}).get("data", {}) or {}).get("info", {}) or {}
                media_count = int(info.get("media_count", 0) or 0)
    except Exception as e:
        logger.error(f"Bilibili 总数获取失败: {e}")
        return
    if media_count <= 0:
        logger.warning("Bilibili 收藏夹为空或不可访问")
        return
    logger.info(f"Bilibili 收藏夹总数: {media_count} 条")
    total_pages = (media_count + ps - 1) // ps
    st = state.get("Bilibili")
    pn = int(st.get("pn", total_pages)) if st else total_pages
    idx = int(st.get("idx", -1)) if st else -1
    processed_ids: Set[str] = set(st.get("processed_ids", [])) if st else set()
    wait_ids: Set[str] = set(st.get("wait_ids", [])) if st else set()
    processed_before = len(processed_ids)
    processed_this_run = 0
    while processed_this_run < limit and pn >= 1:
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "media_id": int(crawler.media_id),
                    "platform": "web",
                    "order": "mtime",
                    "type": 0,
                    "tid": 0,
                    "pn": pn,
                    "ps": ps,
                }
                async with session.get(
                    "https://api.bilibili.com/x/v3/fav/resource/list",
                    params=params,
                    headers={
                        "Cookie": cookie_str,
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "application/json, text/plain, */*",
                        "Accept-Language": "zh-CN,zh;q=0.9",
                        "Origin": "https://www.bilibili.com",
                        "Referer": "https://www.bilibili.com/",
                    },
                ) as resp:
                    ct = resp.headers.get("content-type", "")
                    if "json" not in ct:
                        logger.error(f"Bilibili 分页数据获取失败: 非JSON响应，HTTP {resp.status}")
                        break
                    data = await resp.json()
                    code = int(data.get("code", 0))
                    if code != 0:
                        logger.error(f"Bilibili 分页数据获取失败: code={code}, message={data.get('message')}")
                        break
                    medias = ((data or {}).get("data", {}) or {}).get("medias", []) or []
        except Exception as e:
            logger.error(f"Bilibili 分页数据获取失败: {e}")
            break
        if not medias:
            break
        if idx < 0 or idx >= len(medias):
            idx = len(medias) - 1
        async with aiohttp.ClientSession() as sub_session:
            while idx >= 0 and processed_this_run < limit:
                m = medias[idx]
                title = m.get("title") or ""
                bvid = m.get("bvid") or m.get("bv_id") or str(m.get("id"))
                if bvid in processed_ids:
                    idx -= 1
                    continue
                
                is_wait = bvid in wait_ids
                
                intro = m.get("intro") or ""
                cover = m.get("cover") or ""
                upper = (m.get("upper") or {}).get("name") or ""
                pubtime = m.get("pubtime") or 0
                
                subtitle_text = ""
                if not is_wait:
                    subtitle_text = await crawler._get_subtitle_text(bvid, session=sub_session)
                
                item = ContentItem(
                    platform=crawler.platform_name,
                    id=str(bvid),
                    title=title,
                    url=f"https://www.bilibili.com/video/{bvid}",
                    author=upper,
                    publish_time=str(datetime.fromtimestamp(pubtime)) if pubtime else "",
                    crawl_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    content=intro,
                    subtitle=subtitle_text,
                    images=[cover] if cover else [],
                    video_url=None,
                    audio_url=f"https://www.bilibili.com/video/{bvid}" if not subtitle_text else None,
                    audio_file=None,
                )
                
                status = await save_content(item, skip_markdown=is_wait)
                
                if status == "success":
                    processed_ids.add(str(bvid))
                    if str(bvid) in wait_ids:
                        wait_ids.remove(str(bvid))
                    processed_this_run += 1
                elif status == "partial":
                    wait_ids.add(str(bvid))
                    if str(bvid) in processed_ids:
                        processed_ids.remove(str(bvid))
                
                idx -= 1
        if idx < 0:
            pn -= 1
    cumulative = len(processed_ids)
    state.update(
        "Bilibili",
        {
            "pn": pn,
            "idx": idx,
            "ps": ps,
            "media_id": crawler.media_id,
            "total_count": media_count,
            "processed_ids": list(processed_ids),
            "wait_ids": list(wait_ids),
        },
    )
    logger.info(f"Bilibili 本次成功爬取收藏夹内容: {processed_this_run} 条")
    logger.info(f"Bilibili 累计已爬取收藏夹内容: {cumulative}/{media_count} 条")

async def backfill_xhs(limit: int, state: BackfillState):
    crawler = XHSCrawler()
    if not crawler.api:
        return
    from crawlers.xhs import XHS_PROJECT_PATH
    old_cwd = os.getcwd()
    os.chdir(XHS_PROJECT_PATH)
    try:
        user_id = await crawler._get_my_user_id()
        if not user_id:
            return
        st = state.get("Xiaohongshu")
        xhs_state: Dict[str, Any] = dict(st) if st else {}
        cursor = str(xhs_state.get("cursor", "")) if xhs_state else ""
        processed_ids: Set[str] = set(xhs_state.get("processed_ids", [])) if xhs_state else set()
        wait_ids: Set[str] = set(xhs_state.get("wait_ids", [])) if xhs_state else set()
        total_count = xhs_state.get("total_count")
        def compute_total_collect_count() -> int:
            local_cursor = ""
            seen: Set[str] = set()
            total = 0
            while True:
                success, msg, res_json = crawler.api.get_user_collect_note_info(user_id, local_cursor, crawler.cookies)
                if not success:
                    break
                data = (res_json or {}).get("data", {}) or {}
                notes = data.get("notes", []) or []
                if not notes:
                    break
                for note in notes:
                    nid = note.get("note_id")
                    if nid and nid not in seen:
                        seen.add(nid)
                        total += 1
                local_cursor = str(data.get("cursor") or "")
                has_more = bool(data.get("has_more"))
                if not local_cursor or not has_more:
                    break
            return total
        if total_count is None:
            try:
                total_count = compute_total_collect_count()
                logger.info(f"Xiaohongshu 收藏夹总数: {total_count} 条")
            except Exception:
                total_count = None
                logger.warning("Xiaohongshu 收藏夹总数统计失败，将仅记录已爬数量")
        processed_before = len(processed_ids)
        processed_this_run = 0
        current_cursor = cursor
        while processed_this_run < limit:
            success, msg, res_json = crawler.api.get_user_collect_note_info(user_id, current_cursor, crawler.cookies)
            if not success:
                logger.error(f"Xiaohongshu API request failed: {msg}")
                break
            
            data = (res_json or {}).get("data", {}) or {}
            notes = data.get("notes", []) or []
            has_more = bool(data.get("has_more"))
            next_cursor = str(data.get("cursor") or "")
            
            if not notes:
                logger.info("Xiaohongshu: No more notes found.")
                break
            
            # 记录这一页是否所有内容都被跳过（都是已处理的）
            # 如果整页都跳过了，我们必须手动强制使用 API 返回的 next_cursor 继续翻页
            # 否则因为 current_cursor 在循环中只更新为“已处理”的 note_id，可能会卡住
            all_skipped = True
            
            # 为了回填逻辑（从旧到新存），我们使用 reversed
            # 但要注意：API 的分页依赖 correct cursor。
            # 通常 API 返回的 notes 列表，最后一个元素的 ID 或者是 data.get("cursor") 是获取下一页的凭证。
            # 无论我们在这一页里怎么遍历（正序或倒序），下一页的请求 cursor 应该是确定的。
            
            for note in reversed(notes):
                note_id = note.get("note_id")
                if not note_id:
                    continue
                
                if str(note_id) in processed_ids:
                    # 即使跳过，也要更新一下临时 cursor，防止 break 后死循环（虽然下面会用 next_cursor 覆盖）
                    continue
                
                is_wait = str(note_id) in wait_ids
                
                all_skipped = False
                title = note.get("display_title") or ""
                cover_dict = note.get("cover", {}) or {}
                cover_url = None
                if "info_list" in cover_dict and cover_dict["info_list"]:
                    cover_url = cover_dict["info_list"][0].get("url")
                if not cover_url:
                    cover_url = cover_dict.get("url_default")
                author = (note.get("user") or {}).get("nickname") or ""
                content_desc = title
                images: List[str] = [cover_url] if cover_url else []
                video_url: Optional[str] = None
                note_url = f"https://www.xiaohongshu.com/explore/{note_id}"
                xsec_token = note.get("xsec_token", "")
                full_query_url = f"{note_url}?xsec_token={xsec_token}" if xsec_token else note_url
                try:
                    det_success, det_msg, det_data = crawler.api.get_note_info(full_query_url, crawler.cookies)
                    if det_success:
                        note_data = ((det_data or {}).get("data", {}).get("items", {}) or [])[0].get("note_card", {}) if det_data else {}
                        content_desc = note_data.get("desc", content_desc)
                        title = note_data.get("title", title)
                        img_list = note_data.get("image_list", []) or []
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
                            video_dict = (note_data.get("video") or {}).get("media", {}) or {}
                            stream = (video_dict.get("stream") or {}).get("h264", []) or []
                            if stream:
                                video_url = stream[0].get("master_url")
                except Exception:
                    pass
                item = ContentItem(
                    platform=crawler.platform_name,
                    id=str(note_id),
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
                status = await save_content(item, skip_markdown=is_wait)
                
                if status == "success":
                    processed_ids.add(str(note_id))
                    if str(note_id) in wait_ids:
                        wait_ids.remove(str(note_id))
                    processed_this_run += 1
                elif status == "partial":
                    wait_ids.add(str(note_id))
                    if str(note_id) in processed_ids:
                        processed_ids.remove(str(note_id))
                
                # 在循环内部，不需要更新 current_cursor 给下一页用，
                # 因为下一页的 cursor 应该由 API 响应决定 (next_cursor)。
                # 但我们需要更新状态以便中断后恢复。
                # 如果我们用 reversed，那么“最旧”的那个 note_id 并不是下一页的 cursor。
                # 下一页 cursor 是这一页“最后”也就是“最旧”的那个（正序的最后一个）。
                
                if processed_this_run >= limit:
                    break
            
            # 翻页逻辑：
            # 1. 如果还有更多 (has_more) 且 cursor 有效，则继续。
            # 2. 无论这一页是否处理了数据（可能全跳过），都要翻页。
            if has_more and next_cursor:
                current_cursor = next_cursor
            else:
                logger.info("Xiaohongshu: Reached end of favorites.")
                break
                
            if processed_this_run >= limit:
                break

        cumulative = len(processed_ids)
        xhs_state["cursor"] = current_cursor
        xhs_state["processed_ids"] = list(processed_ids)
        xhs_state["wait_ids"] = list(wait_ids)
        if total_count is not None:
            xhs_state["total_count"] = total_count
        state.update("Xiaohongshu", xhs_state)
        if total_count:
            logger.info(f"Xiaohongshu 本次成功爬取收藏夹内容: {processed_this_run} 条")
            logger.info(f"Xiaohongshu 累计已爬取收藏夹内容: {cumulative}/{total_count} 条")
        else:
            logger.info(f"Xiaohongshu 本次成功爬取收藏夹内容: {processed_this_run} 条")
            logger.info(f"Xiaohongshu 累计已爬取收藏夹内容: {cumulative} 条（总数未知）")
    finally:
        os.chdir(old_cwd)

async def backfill_douyin(limit: int, state: BackfillState):
    crawler = DouyinCrawler()
    items = await crawler.fetch_new_contents()
    def to_ts(s: Optional[str]) -> int:
        if not s:
            return 0
        try:
            return int(datetime.fromisoformat(s).timestamp())
        except Exception:
            return 0
    items_sorted = sorted(items, key=lambda x: to_ts(x.publish_time))
    st = state.get("Douyin")
    processed_ids: Set[str] = set(st.get("processed_ids", [])) if st else set()
    wait_ids: Set[str] = set(st.get("wait_ids", [])) if st else set()
    before = len(processed_ids)
    processed_this_run = 0
    for item in items_sorted:
        if item.id in processed_ids:
            continue
        
        is_wait = item.id in wait_ids
        status = await save_content(item, skip_markdown=is_wait)
        
        if status == "success":
            processed_ids.add(item.id)
            if item.id in wait_ids:
                wait_ids.remove(item.id)
            processed_this_run += 1
        elif status == "partial":
            wait_ids.add(item.id)
            if item.id in processed_ids:
                processed_ids.remove(item.id)
            
        if processed_this_run >= limit:
            break
    cumulative = len(processed_ids)
    state.update("Douyin", {
        "processed_ids": list(processed_ids),
        "wait_ids": list(wait_ids)
    })
    logger.info(f"Douyin 本次成功爬取收藏夹内容: {processed_this_run} 条")
    logger.info(f"Douyin 累计已爬取收藏夹内容: {cumulative} 条（总数未知）")

async def backfill_wechat(limit: int, state: BackfillState):
    crawler = WeChatCrawler()
    urls: List[str] = []
    if os.path.exists(crawler.urls_file):
        with open(crawler.urls_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and line.startswith("http"):
                    urls.append(line)
    total_urls = len(urls)
    st = state.get("WeChat")
    processed_urls = set(st.get("processed_urls", [])) if st else set()
    wait_urls = set(st.get("wait_urls", [])) if st else set()
    remaining = [u for u in urls if u not in processed_urls]
    if not remaining:
        return
    processed = 0
    async with aiohttp.ClientSession() as _:
        async with aiohttp.ClientSession() as __:
            pass
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        for url in remaining:
            try:
                item = await crawler._parse_article(page, url)
                if item:
                    is_wait = url in wait_urls
                    status = await save_content(item, skip_markdown=is_wait)
                    
                    if status == "success":
                        processed_urls.add(url)
                        if url in wait_urls:
                            wait_urls.remove(url)
                        processed += 1
                    elif status == "partial":
                        wait_urls.add(url)
                        if url in processed_urls:
                            processed_urls.remove(url)

                if processed >= limit:
                    break
            except Exception:
                pass
        await browser.close()
    cumulative = len(processed_urls)
    state.update("WeChat", {
        "processed_urls": list(processed_urls),
        "wait_urls": list(wait_urls)
    })
    logger.info(f"WeChat 收藏列表总数: {total_urls} 条")
    logger.info(f"WeChat 本次成功爬取收藏夹内容: {processed} 条")
    logger.info(f"WeChat 累计已爬取收藏夹内容: {cumulative}/{total_urls} 条")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--platforms", type=str, default="Bilibili,Xiaohongshu,Douyin,WeChat")
    parser.add_argument("--limit-bili", type=int, default=30)
    parser.add_argument("--limit-xhs", type=int, default=30)
    parser.add_argument("--limit-douyin", type=int, default=10)
    parser.add_argument("--limit-wechat", type=int, default=30)
    args = parser.parse_args()
    os.makedirs("logs", exist_ok=True)
    logger.remove()
    logger.add(sys.stderr, level=settings.LOG_LEVEL)
    logger.add("logs/backfill_{time}.log", rotation="1 day", retention="7 days")
    state = BackfillState(STATE_FILE)
    platforms = [s.strip() for s in args.platforms.split(",") if s.strip()]
    if "Bilibili" in platforms:
        await backfill_bilibili(args.limit_bili, state)
    if "Xiaohongshu" in platforms:
        await backfill_xhs(args.limit_xhs, state)
    if "Douyin" in platforms:
        await backfill_douyin(args.limit_douyin, state)
    if "WeChat" in platforms:
        await backfill_wechat(args.limit_wechat, state)
    await asyncio.sleep(0.5)

if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except Exception:
            pass
    asyncio.run(main())
