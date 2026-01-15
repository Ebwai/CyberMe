import sys
import os
from dotenv import load_dotenv

load_dotenv()

XHS_PROJECT_PATH = r"f:\project\spider_Unit\local_knowledge_base\Spider_XHS"
if XHS_PROJECT_PATH not in sys.path:
    sys.path.append(XHS_PROJECT_PATH)

old_cwd = os.getcwd()
os.chdir(XHS_PROJECT_PATH)
try:
    from apis.xhs_pc_apis import XHS_Apis
    api = XHS_Apis()
    cookies = os.getenv("XHS_COOKIE")
    
    # Test self info
    success, msg, data = api.get_user_self_info2(cookies)
    print(f"Self info success: {success}, msg: {msg}")
    if success and data and "data" in data:
        user_id = data["data"].get("user_id")
        print(f"User ID: {user_id}")
        
        # Test collections
        c_success, c_msg, c_data = api.get_user_collect_note_info(user_id, "", cookies)
        print(f"Collections success: {c_success}, msg: {c_msg}")
        if c_success:
            notes = c_data.get("data", {}).get("notes", [])
            print(f"Notes captured: {len(notes)}")
    else:
        print(f"Data dump: {data}")
finally:
    os.chdir(old_cwd)
