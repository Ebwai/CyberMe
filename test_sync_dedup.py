import asyncio
import os
import json
from dataclasses import dataclass
from typing import List
from crawlers.base import BaseCrawler, ContentItem
from utils.state_manager import StateManager
from config import settings

class MockCrawler(BaseCrawler):
    def __init__(self, items_to_return: List[ContentItem]):
        super().__init__()
        self.platform_name = "MockPlatform"
        self.items_to_return = items_to_return

    async def fetch_new_contents(self) -> List[ContentItem]:
        limit_id = StateManager.get_last_latest_id(self.platform_name)
        return self.filter_existing(self.items_to_return, limit_id)

async def test_sync_point():
    platform = "MockPlatform"
    state_file = settings.STATE_FILE_PATH
    
    # Clean logic
    if os.path.exists(state_file):
        os.remove(state_file)
    
    # 1. First run: 3 items [A, B, C]
    item_a = ContentItem(platform=platform, id="A", title="Title A", url="url_a", author="X", publish_time="", crawl_time="", content="")
    item_b = ContentItem(platform=platform, id="B", title="Title B", url="url_b", author="X", publish_time="", crawl_time="", content="")
    item_c = ContentItem(platform=platform, id="C", title="Title C", url="url_c", author="X", publish_time="", crawl_time="", content="")
    
    crawler1 = MockCrawler([item_a, item_b, item_c])
    items1 = await crawler1.fetch_new_contents()
    
    print(f"Run 1: Fetched {len(items1)} items. Expected: 3")
    assert len(items1) == 3
    
    # Simulate main.py success update
    StateManager.update_latest_id(platform, items1[0].id)
    
    # Verify state file
    with open(state_file, 'r') as f:
        state = json.load(f)
    print(f"State after Run 1: {state}. Expected: {{'{platform}': 'A'}}")
    assert state[platform] == "A"

    # 2. Second run: New item D added, [D, A, B, C]
    item_d = ContentItem(platform=platform, id="D", title="Title D", url="url_d", author="X", publish_time="", crawl_time="", content="")
    crawler2 = MockCrawler([item_d, item_a, item_b, item_c])
    items2 = await crawler2.fetch_new_contents()
    
    print(f"Run 2: Fetched {len(items2)} items. Expected: 1 (Item D)")
    assert len(items2) == 1
    assert items2[0].id == "D"
    
    # Update state again
    StateManager.update_latest_id(platform, items2[0].id)
    with open(state_file, 'r') as f:
        state = json.load(f)
    print(f"State after Run 2: {state}. Expected: {{'{platform}': 'D'}}")
    assert state[platform] == "D"

    # 3. Third run: No new items [D, A, B, C]
    crawler3 = MockCrawler([item_d, item_a, item_b, item_c])
    items3 = await crawler3.fetch_new_contents()
    print(f"Run 3: Fetched {len(items3)} items. Expected: 0")
    assert len(items3) == 0

    print("\n✅ Sync-Point deduplication test PASSED!")

if __name__ == "__main__":
    asyncio.run(test_sync_point())
