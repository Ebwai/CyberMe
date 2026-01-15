import asyncio
from bilibili_api import Credential, favorite_list, user, sync
from config import settings
import sys

async def main():
    print(f"BILI_SESSDATA present: {bool(settings.BILI_SESSDATA)}")
    print(f"BILI_JCT present: {bool(settings.BILI_JCT)}")
    print(f"BILI_BUVID3 present: {bool(settings.BILI_BUVID3)}")
    print(f"BILI_MEDIA_ID: {settings.BILI_MEDIA_ID}")

    sess = settings.BILI_SESSDATA
    if not sess:
        print("ERROR: SESSDATA is empty!")
        return

    c = Credential(sessdata=settings.BILI_SESSDATA, bili_jct=settings.BILI_JCT, buvid3=settings.BILI_BUVID3)

    print("\n--- Testing Login Status ---")
    try:
        # User 1 is just a dummy ID, check_valid doesn't need real ID if checking self
        is_valid = await c.check_valid()
        print(f"Credential Valid: {is_valid}")
        
        myself = await user.get_self_info(c)
        print(f"Logged in as: {myself['name']} (mid: {myself['mid']})")
    except Exception as e:
        print(f"Login Check Failed: {e}")
        return

    print("\n--- Testing Favorite List Access ---")
    try:
        media_id = int(settings.BILI_MEDIA_ID)
        resp = await favorite_list.get_video_favorite_list_content(media_id=media_id, credential=c)
        print(f"Success! Got {len(resp.get('medias', []))} items.")
    except Exception as e:
        print(f"Favorite List Fetch Failed: {e}")

if __name__ == '__main__':
    asyncio.run(main())
