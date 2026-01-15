import asyncio
from bilibili_api import video, Credential
import os
from dotenv import load_dotenv

load_dotenv()

async def debug_bili():
    credential = Credential(
        sessdata=os.getenv("BILI_SESSDATA"),
        bili_jct=os.getenv("BILI_JCT"),
        buvid3=os.getenv("BILI_BUVID3")
    )
    bvid = "BV1GM6mB9EKr" # One of the IDs from log
    v = video.Video(bvid=bvid, credential=credential)
    info = await v.get_info()
    cid = info['cid']
    print(f"CID: {cid}")
    
    try:
        # Try method 1
        sub1 = await v.get_subtitle(cid=cid)
        print(f"Method 1 success: {len(sub1) if sub1 else 0} subtitles")
    except Exception as e:
        print(f"Method 1 fail: {e}")

    try:
        # Try method 2
        v.cid = cid
        sub2 = await v.get_subtitle()
        print(f"Method 2 success: {len(sub2) if sub2 else 0}")
    except Exception as e:
        print(f"Method 2 fail: {e}")

if __name__ == "__main__":
    asyncio.run(debug_bili())
