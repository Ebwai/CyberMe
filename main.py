import asyncio
import sys
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from config import settings
from crawlers.base import BaseCrawler
from crawlers.bilibili import BiliCrawler
from crawlers.douyin import DouyinCrawler
from crawlers.xhs import XHSCrawler
from crawlers.wechat import WeChatCrawler
from utils.storage import save_content

# Configure Loguru
logger.remove()
logger.add(sys.stderr, level=settings.LOG_LEVEL)
logger.add("logs/spider_{time}.log", rotation="1 day", retention="7 days")

from processor.main import process_daily_content

async def run_crawlers(platform_filter: str = None):
    logger.info("Starting crawl task...")
    
    all_crawlers: list[BaseCrawler] = [
        BiliCrawler(),
        DouyinCrawler(),
        XHSCrawler(),
        WeChatCrawler()
    ]
    
    # Filter if platform specified
    crawlers_to_run = all_crawlers
    if platform_filter:
        crawlers_to_run = [c for c in all_crawlers if platform_filter.lower() in c.platform_name.lower()]
        if not crawlers_to_run:
            logger.warning(f"No crawler found matching: {platform_filter}")
            return

    for crawler in crawlers_to_run:
        try:
            logger.info(f"Running {crawler.platform_name} crawler...")
            items = await crawler.fetch_new_contents()
            logger.info(f"Fetched {len(items)} new items from {crawler.platform_name}")
            
            if items:
                # Track latest ID to update state later
                latest_item_id = items[0].id
                all_success = True
                
                for item in items:
                    try:
                        await save_content(item)
                    except Exception as e:
                        logger.error(f"Failed to save {item.id} from {crawler.platform_name}: {e}")
                        all_success = False
                
                if all_success:
                    from utils.state_manager import StateManager
                    StateManager.update_latest_id(crawler.platform_name, latest_item_id)
                else:
                    logger.warning(f"Not updating sync-point for {crawler.platform_name} due to partial failures.")
                
        except Exception as e:
            logger.error(f"Error checking {crawler.platform_name}: {e}")
            
    logger.info("Crawl task finished.")
    
    # Graceful shutdown for Windows ProactorEventLoop
    # Allow underlying transports (like SSL/aiohttp) to close
    await asyncio.sleep(0.5)

def run_processor_job():
    logger.info("Starting processing task...")
    process_daily_content()
    logger.info("Processing task finished.")

def main():
    scheduler = AsyncIOScheduler()
    
    # Crawl Job: 22:00
    scheduler.add_job(run_crawlers, 'cron', hour=22, minute=0)
    logger.info("Scheduled [Crawl Task] at 22:00 daily.")
    
    # Process Job: 23:00 (Check Config if needed, but hardcoding for decoupled plan)
    scheduler.add_job(run_processor_job, 'cron', hour=23, minute=0)
    logger.info("Scheduled [Process Task] at 23:00 daily.")
    
    try:
        scheduler.start()
        # Keep the main thread alive, but we can also use a robust event loop
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    # Usage: 
    #   python main.py --now [optional_platform]  -> Run Crawl Now
    #   python main.py --process [optional_date]  -> Run Process Now
    
    # Windows-specific event loop policy hack to silence "Event loop is closed"
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--now":
            target_platform = sys.argv[2] if len(sys.argv) > 2 else None
            asyncio.run(run_crawlers(target_platform))
            
        elif cmd == "--process":
            target_date = sys.argv[2] if len(sys.argv) > 2 else None
            process_daily_content(target_date)
    else:
        main()
