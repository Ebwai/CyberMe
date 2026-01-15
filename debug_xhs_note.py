import sys
import os
import asyncio
import json
from config import settings

# Add Spider_XHS to sys.path
XHS_PROJECT_PATH = r"f:\project\spider_Unit\local_knowledge_base\Spider_XHS"
if XHS_PROJECT_PATH not in sys.path:
    sys.path.append(XHS_PROJECT_PATH)

old_cwd = os.getcwd()
os.chdir(XHS_PROJECT_PATH)
try:
    from apis.xhs_pc_apis import XHS_Apis
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)
finally:
    os.chdir(old_cwd)

async def main():
    cookies = settings.XHS_COOKIE
    if not cookies:
        print("No XHS_COOKIE in .env")
        return

    api = XHS_Apis()
    
    # Get User ID first (simplified)
    # user_id = "61d16a580000000021029462" # From log
    # But usually we get it dynamically. Let's try to get collection directly if we have ID.
    user_id = "61d16a580000000021029462"
    
    os.chdir(XHS_PROJECT_PATH)
    try:
        print(f"Fetching collections for {user_id}...")
        success, msg, res_json = api.get_user_collect_note_info(user_id, "", cookies)
        print(f"Collection Fetch: {success}, {msg}")
        
        if success:
            notes = res_json.get("data", {}).get("notes", [])
            print(f"Found {len(notes)} notes.")
            if notes:
                item = notes[0]
                print(f"First Note ID: {item.get('note_id')}")
                print(f"Title: {item.get('display_title')}")
                print(f"Cover structure: {item.get('cover')}")
                print(f"Xsec Token: {item.get('xsec_token')}")
                print(f"Full Cover Dict: {item.get('cover')}") ## DEBUG
                
                # Now try getting detail
                note_id = item.get("note_id")
                xsec = item.get("xsec_token")
                url = f"https://www.xiaohongshu.com/explore/{note_id}?xsec_token={xsec}"
                print(f"\nFetching detail for {url}...")
                
                d_success, d_msg, d_data = api.get_note_info(url, cookies)
                print(f"Detail Success: {d_success}")
                if d_success:
                    note_card = d_data.get("data", {}).get("items", [{}])[0].get("note_card", {})
                    print(f"Detail Image List: {note_card.get('image_list')}")
                    print(f"Detail Type: {note_card.get('type')}")
                    print(f"Detail Video: {note_card.get('video')}")
                    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        os.chdir(old_cwd)

if __name__ == "__main__":
    asyncio.run(main())
