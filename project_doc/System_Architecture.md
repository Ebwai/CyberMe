# System Architecture

## 1. Architecture Design Principles
- **Modularity**: Separate crawlers for each platform (Bilibili, Xiaohongshu, Douyin, WeChat).
- **State Management**: Use `backfill_state.json` to track progress (cursors, processed IDs) to support resumable crawls.
- **Anti-Crawling Compatibility**: 
    - Use real browser cookies.
    - **Dynamic Header Generation**: Automatically align `sec-ch-ua` headers with the configured `User-Agent` to avoid fingerprint mismatches (Anti-461).
    - **Runtime Patching**: Monkeypatch legacy libraries (`xhs_util`) to inject correct headers without modifying third-party code directly.
- **Robustness**: Retry mechanisms and extensive logging.

## 2. Layered Architecture
1. **Controller Layer**: `backfill_favorites.py` (Main Entry). Handles CLI args, state loading, and dispatches to specific crawlers.
2. **Crawler Layer**: `crawlers/`. Contains specific logic for each platform (API calls, data parsing).
3. **API Layer**: `apis/` (Legacy/Third-party wrappers). Low-level HTTP requests.
4. **Utility Layer**: `utils/`, `xhs_utils/`. Helpers for storage, JS execution, config.

## 3. Technology Selection
- **Python 3.10+**
- **Requests/Aiohttp**: For HTTP requests.
- **Execjs**: For executing JS signatures (X-S, X-T).
- **Loguru**: For logging.

## 4. Core Code Modules

### 4.1 Xiaohongshu Crawler (`crawlers/xhs.py` & `backfill_favorites.py`)
- **Module Name**: XHS Backfill
- **Input**: User ID, Cookie, Cursor.
- **Output**: List of Notes (Images/Videos).
- **Core Logic**:
    1.  **Init**: Load state, identify User ID.
    2.  **Patch**: Inject Dynamic Headers (match UA and sec-ch-ua).
    3.  **Fetch**: Loop `get_user_collect_note_info`.
    4.  **Parse**: Extract note IDs.
    5.  **State Update**: Save progress.
    6.  **Error Handling**: Detect 461 (Verification) and warn user.

### 4.2 Bilibili Crawler (`crawlers/bilibili.py`)
- **Core Logic**: Uses official API with `SESSDATA` to fetch favorite lists. Handles pagination via `pn` (page number).

## 5. Technical Challenges & POC
- **XHS 461 Error**: Solved by ensuring `User-Agent` in HTTP headers strictly matches `sec-ch-ua` client hints.
- **JS Signature**: Solved by dynamically setting CWD to allow `execjs` to find `static/*.js` files.
