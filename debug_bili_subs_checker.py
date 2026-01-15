import asyncio
from bilibili_api import video, Credential
from config import settings
import sys

async def check_subs(bvid):
    print(f"Checking subtitles for {bvid}...")
    
    sess = settings.BILI_SESSDATA
    if not sess:
        print("WARNING: No SESSDATA. Results might be limited.")
        
    c = Credential(sessdata=sess, bili_jct=settings.BILI_JCT, buvid3=settings.BILI_BUVID3)
    
    v = video.Video(bvid=bvid, credential=c)
    try:
        info = await v.get_info()
        cid = info['cid']
        title = info['title']
        print(f"Video Title: {title}")
        print(f"CID: {cid}")
        
        subs = await v.get_subtitle(cid=cid)
        print(f"Subtitles found type: {type(subs)}")
        print(f"Subtitles keys: {subs.keys() if isinstance(subs, dict) else 'Not Dict'}")
        
        if subs and 'subtitles' in subs:
            print(f"Subtitle count: {len(subs['subtitles'])}")
            for s in subs['subtitles']:
                print(f" - API Language Code: {s.get('lan')} | Name: {s.get('lan_doc')}")
        else:
            print("No 'subtitles' key in response.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_bili_subs_checker.py <BVID>")
    else:
        asyncio.run(check_subs(sys.argv[1]))
