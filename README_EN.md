[中文](README.md) | [English](README_EN.md)

# CyberMe

> **Create a cyber avatar of yourself, possessing not only the general knowledge of large models but also all your information (yes, all of it—not just superficial knowledge like your bank card password, but your inner self, as long as you are willing to share). Connected with various tools, you only need to issue commands, and CyberMe can do anything in the cyber world just like you (or rather, IS you) (yes, anything, as long as you are willing).**

![CyberMe Header Image](pictures/github_demo_picture.jpg)

**Long-Term Goals and Progress**:
- [ ] **Phase 1: Information Synchronization (S-project)** --- From now on, all information you acquire, AI will also acquire a copy (CyberMe grows with you from now).
	- [x] High-quality data synchronization from social media: Xiaohongshu (RedNote), Bilibili, WeChat Official Accounts, Douyin (TikTok)—all information saved in favorites (info you consider valuable, info you follow).
  - [ ] Information source expansion:
- [ ] **Phase 2: Memory Database (M-project)** [Data Storage & Retrieval] --- waiting
  - [x] Framework selection and setup, see M-project for details.
  - [ ] Evaluation system construction: (In other words, your worldview, philosophy, values, and evaluation criteria for specific scenarios).
- [ ] **Phase 3: Behavior Synchronization (A-project)** [Tools & Workflow] --- waiting
  - [x] Social behavior: Personalized style sharing on Bilibili, Xiaohongshu, Douyin, WeChat Official Accounts.
  - [x] Reading emails sent to you at any time, processing them, and pushing them to your commonly used social platforms on your behalf.
- [ ] **Phase 4: Physical Independence (H-project)** [Local Computing + Physical World **Practice** & Interaction] --- waiting
  - [x] Initial phase uses intranet penetration solutions, using N8N as a hub to control and connect all systems and hardware.

**The Significance of CyberMe:**
- Background: Recently, there have been many popular products (like Doubao Mobile, OpenClawd, Kimi Agent Cluster). Does this project duplicate them?
- Answer: There are similarities, but the underlying starting point is different. The projects mentioned above are about assigning a task to someone else. The purpose of CyberMe is to create a digital version of **yourself**.
- **Origin of the Project: Every time we use various Large Language Models (LLMs) in apps or on the web, we often find that the AI's response is not what we want. The direct reason for this is that you haven't provided it with enough information; the AI doesn't know you, so naturally, it cannot understand your full needs. To solve this, there are generally two approaches. The first is to let the AI ask you questions at any time, thereby better capturing your needs and aligning with them. The second approach is to continuously maintain a personal information database. The more the AI knows you, the more its output will match your intentions. This understanding is not just as simple as a RAG knowledge base. Therefore, to achieve the goal of making AI more useful, first, the AI needs to become you. To become you, CyberMe continuously builds 'you' through the modules of these four phases.**

---

## S-project Overview

This project is a personal knowledge management and content collection tool, mainly consisting of 2 requirements:
1️⃣ **Multi-platform Multi-modal High-quality Information Acquisition**
2️⃣ **Multi-modal Information Processing**

It supports automatically pulling content (including text, images, videos [audio], and other multi-modal info) from "Favorites" or specified lists on the following platforms and converting all modal information into text for local storage (using text to represent all modal information is for cost-effective RAG database construction and processing later).
- Bilibili
- Douyin
- Xiaohongshu (RedNote)
- WeChat Official Accounts (via URL list)

The system runs in two stages daily:
- **22:00 Collection Task**: Crawls newly added favorites from various platforms for the day, saving them as Markdown + media files.
- **23:00 Processing Task**: Performs offline processing on downloaded multimedia (Speech-to-Text, Image OCR) and writes the results back to Markdown.

All output is unified in the `F:\DataInput\YYYY-MM-DD\...` directory, which is convenient for both RAG database construction and direct reading.

**Why this project exists**: There are many other solutions for information acquisition, so why is this project needed?
- Compared to using agents to operate browsers for crawling (like the recently popular OpenClawd and previous Doubao mobile):
	- Low cost: No need to deploy browsers or purchase expensive API services.
	- High efficiency: Can acquire a large amount of information in a short time.
  - Privacy protection: All information is stored locally and will not be uploaded to any server.
  - The principle of this project is the same as agents operating browsers, just without the AI decision-making process.
- There are some other reasons that are hard to articulate, but you'll know once you use it: the information you follow (itself) will be largely preserved (in a form suitable for building an AI knowledge base, not for self-media data analysis purposes).

---

## Directory Structure (Tree Diagram)

The core structure of the project root directory (`f:\project\spider_TRAE`) is as follows:

```text
spider_TRAE/
├─ main.py                         # Entry: Collection Task Scheduler (22:00)
├─ processor/
│  └─ main.py                      # Entry: Processing Task (23:00: Speech-to-Text & OCR)
├─ crawlers/
│  ├─ base.py                      # Crawler Base Class & ContentItem Data Structure
│  ├─ bilibili.py                  # Bilibili Favorites Crawler (Subtitle + Audio Fallback)
│  ├─ douyin.py                    # Douyin Favorites Crawler (Playwright Anti-crawling)
│  ├─ xhs.py                       # Xiaohongshu Favorites Crawler (Reuses Spider_XHS)
│  └─ wechat.py                    # WeChat Official Account Crawler (Based on URL file)
├─ utils/
│  ├─ storage.py                   # Unified Storage: Markdown Rendering + Media Download
│  ├─ media_tool.py                # Media Tools: yt-dlp + Whisper + OCR
│  └─ state_manager.py             # Sync-Point State Management (Cross-date Deduplication)
├─ project_doc/
│  ├─ SSRD.md                      # Software System Requirements Definition
│  ├─ SRS.md                       # Software Requirements Specification
│  ├─ System_Architecture.md       # System Architecture
│  ├─ testplan.md                  # Test Plan
│  └─ history_log.md               # History Log & Fix Records
├─ local_knowledge_base/
│  ├─ Spider_XHS/                  # External Xiaohongshu Project (Reuses its signature & API)
│  ├─ B 站无字幕视频字幕识别方案深度解析（2025-2026 最新）.md
│  ├─ B站字幕提取的调研.md
│  └─ 调研.md
├─ logs/
│  └─ spider_*.log                 # Crawler Run Logs (Auto-rotation by date)
├─ run_daily_crawl.bat             # Windows Scheduled Task: Start Collection Task
├─ run_daily_process.bat           # Windows Scheduled Task: Start Processing Task
├─ config.py                       # Global Config & .env Loading (Paths, Cookies, etc.)
├─ .env                            # Private Config (Cookies, Favorite IDs, etc.)
├─ README_CONFIG.md                # Guide for getting Platform Configs (Cookie/ID)
├─ requirements.txt                # Python Dependencies
└─ test_*.py / debug_*.py          # Environment Verification & Functional Test Scripts
```

Example of collected data directory structure (located under `F:\DataInput`):

```text
F:\DataInput\
└─ YYYY-MM-DD\
   ├─ Bilibili\
   │  └─ Bilibili_Author_Title\
   │     ├─ Bilibili_Author_Title.md
   │     └─ assets/ & audio.wav (optional)
   ├─ Douyin\
   │  └─ Douyin_Author_Title\
   │     ├─ Douyin_Author_Title.md
   │     └─ assets/ & video/audio (depending on platform capability)
   ├─ Xiaohongshu\
   │  └─ Xiaohongshu_Author_Title\
   │     ├─ Xiaohongshu_Author_Title.md
   │     └─ assets/ & video.mp4 & audio.wav
   └─ WeChat\
      └─ WeChat_OfficialAccount_Title\
         ├─ WeChat_OfficialAccount_Title.md
```

---

## Environment Setup & Dependencies

The project defaults to running in the Conda environment `yolov5` (verified in actual use). Recommended steps:

1. **Create / Use Conda Environment**

   ```bash
   conda create -n yolov5 python=3.9  # Skip if already exists
   conda activate yolov5
   ```

2. **Install Python Dependencies**

   In the project root directory `f:\project\spider_TRAE`:

   ```bash
   pip install -r requirements.txt
   ```

3. **Install Browser & Playwright Driver (for Douyin)**

   ```bash
   playwright install
   ```

4. **Install FFmpeg**

   - On Windows, it is recommended to install FFmpeg via `choco` or the official installer, and ensure `ffmpeg` is in the system PATH.
   - Check with the following command:

     ```bash
     ffmpeg -version
     ```

5. **Prepare Whisper Model Directory (Optional)**

   Configured in `config.py`:
   - `WHISPER_MODEL_DIR`: Model storage path (default `F:\Spider_proj\models`)
   - `TEMP_AUDIO_DIR`: Audio temp path (default `F:\Spider_proj\temp`)

   If default paths do not exist, folders will be automatically created on first run.

---

## Configuration (.env & Cookie)

All sensitive configurations are injected via the `.env` file. Field definitions are in [config.py](file:///f:/project/spider_TRAE/config.py) and [README_CONFIG.md](file:///f:/project/spider_TRAE/README_CONFIG.md).
You need to create the `.env` file in the project folder yourself and fill in your own configurations. Please refer to [README_CONFIG.md](file:///f:/project/spider_TRAE/README_CONFIG.md) for a detailed tutorial.

Key fields include:
- Bilibili: `BILI_SESSDATA`, `BILI_JCT`, `BILI_BUVID3`, `BILI_MEDIA_ID`
- Douyin: `DOUYIN_COOKIE`
- Xiaohongshu: `XHS_COOKIE`
- WeChat: `WECHAT_URLS_FILE` (default `F:\DataInput\wechat_urls.txt`), `WECHAT_DB_PATH` (optional)

For detailed steps on how to get them (how to copy Cookie / media_id from the browser), please refer to [README_CONFIG.md](file:///f:/project/spider_TRAE/README_CONFIG.md).

**How often do key fields in the file need to be replaced?** (Based on my one-month usage experience)
- Bilibili: Replace every 3 days (based on Bilibili login expiration time)
- Douyin: Replace every 10 days (based on Douyin login expiration time)
- Xiaohongshu: Replace every 7 days (based on Xiaohongshu login expiration time)
- WeChat: Add or remove URLs as needed (generally not replaced often)

---

## Usage

### 1. Manually Run Collection Task (22:00 Logic)

In Conda environment `yolov5`, enter the project root directory:

```bash
conda activate yolov5
cd f:\project\spider_TRAE
python main.py --now
```

- Defaults to executing collection for all configured platforms (Bilibili / Douyin / Xiaohongshu / WeChat).
- To collect from a specific platform only (e.g., only Bilibili), use:

```bash
python main.py --now Bilibili
python main.py --now Douyin
python main.py --now Xiaohongshu
python main.py --now WeChat
```

After collection is complete, corresponding Markdown and media files can be found in the `F:\DataInput\YYYY-MM-DD\...` directory.

### 2. Manually Run Processing Task (23:00 Logic)

```bash
conda activate yolov5
cd f:\project\spider_TRAE
python -m processor.main
```

This task will:
- Scan the daily directory `F:\DataInput\YYYY-MM-DD`.
- Perform Whisper Speech-to-Text on applicable audio/video:
  - **Only Bilibili + Xiaohongshu** undergo speech transcription.
- Perform OCR (EasyOCR) on applicable images:
  - **Only Xiaohongshu** undergoes OCR recognition.
- Automatically append transcription and OCR results to the corresponding Markdown file:
  - Subtitle/Transcript section: `[AI-Generated Transcript]` paragraph under `## Subtitle/Transcript`.
  - Image OCR section: `## Image OCR Result` paragraph.

### 3. Windows Task Scheduler Automation

The project has prepared two `.bat` scripts:
- [run_daily_crawl.bat](file:///f:/project/spider_TRAE/run_daily_crawl.bat) : Daily 22:00 Collection Task.
- [run_daily_process.bat](file:///f:/project/spider_TRAE/run_daily_process.bat) : Daily 23:00 Processing Task.

In Windows "Task Scheduler":
1. Create Task -> Set Trigger time (22:00 / 23:00).
2. In Actions, select "Start a program" and point to the corresponding `.bat` file.
3. Ensure the task running account has permission to access `F:\DataInput` and the Conda environment.

### 4. Historical Favorites Backfill Task (backfill_favorites.py)

In addition to the daily 22:00 incremental collection, you can use [backfill_favorites.py](file:///f:/project/spider_TRAE/backfill_favorites.py) to backfill "Historical Favorites", suitable for:
- Initial project deployment, needing to fill past favorites at once;
- Daily incremental tasks have been running for a while, but missed a period, needing to fill that gap;
- Only want to do historical backfill for a specific platform, while others remain as is.

#### 4.1 Basic Usage

In Conda environment `yolov5`, enter the project root directory:

```bash
conda activate yolov5
cd f:\project\spider_TRAE
python backfill_favorites.py
```

- Defaults to backfilling all: `Bilibili, Xiaohongshu, Douyin, WeChat` four platforms;
- Each platform has an independent "max fetch count per run":
  - `--limit-bili`: Max items to fetch for Bilibili per run (default 30);
  - `--limit-xhs`: Max items to fetch for Xiaohongshu per run (default 30);
  - `--limit-douyin`: Max items to fetch for Douyin per run (default 10);
  - `--limit-wechat`: Max items to fetch for WeChat per run (default 30).

You can also backfill only specific platforms, for example:

```bash
# Backfill only Bilibili and Xiaohongshu (Suitable for filling these two first)
python backfill_favorites.py --platforms Bilibili,Xiaohongshu

# Backfill only Douyin, and only 5 items per run, convenient for observing effects
python backfill_favorites.py --platforms Douyin --limit-douyin 5
```

Script run logs will be written to `logs/backfill_YYYY-MM-DD.log` for you to monitor progress.

#### 4.2 Overview of Backfill Strategies per Platform

- Bilibili
  - Uses official Web Favorites API (`/x/v3/fav/resource/list`) to get total count and pagination data;
  - Starts backfilling from the "oldest page" moving forward each time, and saves from old to new in the current run based on favorite time;
  - Records processed `bvid`, current page `pn`, and index `idx` in `backfill_state.json` to support multiple batch runs.

- Xiaohongshu
  - Reads favorite note list based on API provided by `local_knowledge_base/Spider_XHS`;
  - Attempts to count total favorites first (Log shows "Xiaohongshu Favorites Total: N items"); runs in "unknown total" mode if counting fails;
  - Advances to earlier favorites based on cursor returned by interface, and records `cursor` and processed `note_id` set to support multiple batch backfills.

- Douyin
  - Reuses `fetch_new_contents` capability from daily crawler to get all visible content in current favorites;
  - Sorts by `publish_time` from old to new, and executes save only for content not yet in backfill status;
  - Since Douyin favorites interface doesn't provide a stable "total" field, log will show "Total Unknown".

- WeChat
  - Reads article URL list from `WECHAT_URLS_FILE` configured in `.env`;
  - Executes crawl and save only for never-processed URLs; processed URLs are marked in backfill status.

All platform backfill statuses are unified and saved in `backfill_state.json` under `SAVE_PATH` root directory (Default path: `F:\DataInput\backfill_state.json`).

#### 4.3 Relationship with Daily Incremental Deduplication & Best Practices

Daily 22:00 collection task ensures incremental deduplication through two layers:
- Sync-Point within each platform (Last successfully crawled favorite ID);
- Fallback check based on "File Existence" in daily directory (see [crawlers/base.py](file:///f:/project/spider_TRAE/crawlers/base.py#L46-L88)).

The backfill script uses "Platform-internal Processed ID Set" for deduplication:
- Bilibili / Xiaohongshu / Douyin: Maintains `processed_ids` set in `backfill_state.json`;
- WeChat: Maintains `processed_urls` set in `backfill_state.json`;
- If the same favorite from the same platform is already in the corresponding set, it will be skipped when running backfill script again.

Note: **The backfill script does NOT reuse the Daily Task's Sync-Point**, their statuses are independent. This means:
- If a favorite was crawled by "Daily Task" but hasn't appeared in backfill script's `processed_ids`, the backfill script will request to crawl it again;
- At the disk level, since output paths are layered by "Date/Platform/Author_Title", if the same post is crawled on different dates, it will appear in directories of different dates; duplicate Markdown files for the same post won't be generated within the same day;
- At the network request & platform risk control level, this is a "duplicate crawl" and will consume extra request quota.

To minimize duplicate crawling with daily incremental tasks, the following sequence is recommended:
- **Initial Project Deployment**
  1. Complete `.env` configuration and environment verification first;
  2. Do not enable Windows Scheduled Tasks temporarily;
  3. Run `backfill_favorites.py` multiple times, adjusting `--limit-*` parameters appropriately, until logs show "Cumulative crawled" for Bilibili / Xiaohongshu etc. basically covers historical favorites;
  4. Then enable the 22:00 / 23:00 daily incremental tasks.

- **Old Project Running for a While**
  - If just occasionally filling a small piece of history (e.g., you created a new favorite folder on a platform and want to fill old content):
    - Run `backfill_favorites.py` manually at any time of the day, setting corresponding platform's `--limit-*` parameters smaller (e.g., 5~20 items);
    - Observe "Cumulative crawled" progress in `logs/backfill_*.log`, fill in multiple batches;
    - Even if individual content overlaps with daily tasks, it just overwrites the same Markdown, without generating massive duplicate files on disk.

- **Wait! Do NOT do these to avoid serious duplicate crawling**
  - Do not delete `backfill_state.json` arbitrarily, unless you explicitly want to "backfill from scratch";
  - Do not frequently switch Favorite IDs in `.env` on the same day (e.g., frequently changing `BILI_MEDIA_ID`), otherwise status might become inconsistent with actual favorite scope;
  - Do not run backfill scripts on multiple machines for the same favorites sharing the same output directory simultaneously, otherwise they will overwrite each other.

---

## Module Overview

- [main.py](file:///f:/project/spider_TRAE/main.py)
  - Responsible for initializing logs, scheduling APScheduler, and starting crawlers by platform.
  - Supports command line argument `--now [platform]` for real-time triggering.

- [crawlers/base.py](file:///f:/project/spider_TRAE/crawlers/base.py)
  - Defines `ContentItem` data structure.
  - Implements cross-platform deduplication strategy (Sync-Point + Local File Existence Check).
  - Provides unified authentication failure prompt `handle_auth_error`.

- [crawlers/bilibili.py](file:///f:/project/spider_TRAE/crawlers/bilibili.py)
  - Calls `bilibili-api-python` to get favorite lists and video details.
  - Prioritizes fetching official / AI subtitles; if missing, downloads audio via `MediaTool` for later transcription by processing task.

- [crawlers/douyin.py](file:///f:/project/spider_TRAE/crawlers/douyin.py)
  - Uses Playwright to launch browser, intercepting `favorite` interface from favorites page.
  - Handles Douyin-specific encryption parameters & risk control; reduces noise for some Protocol Errors.

- [crawlers/xhs.py](file:///f:/project/spider_TRAE/crawlers/xhs.py)
  - Reuses API & signature logic from `local_knowledge_base/Spider_XHS`.
  - Solves Image 403, Anti-proxy/SSL issues, and unifies results into Markdown + assets.

- [crawlers/wechat.py](file:///f:/project/spider_TRAE/crawlers/wechat.py)
  - Reads URL list from `WECHAT_URLS_FILE`.
  - Uses Playwright / requests to crawl article HTML, converting to Markdown via `html2text`.

- [utils/storage.py](file:///f:/project/spider_TRAE/utils/storage.py)
  - Renders YAML Frontmatter + Markdown body based on `ContentItem`.
  - Responsible for downloading images/audio/video to corresponding post directories.

- [utils/media_tool.py](file:///f:/project/spider_TRAE/utils/media_tool.py)
  - Encapsulates `yt-dlp` for audio/video download.
  - Integrates `openai-whisper` for Speech-to-Text (GPU supported).
  - Integrates OCR tools for image text recognition (mainly for Xiaohongshu graphics).

- [processor/main.py](file:///f:/project/spider_TRAE/processor/main.py)
  - Traverses daily directories, executing three-stage processing:
    1. Video audio extraction (only for platforms needing transcription like Xiaohongshu).
    2. Audio transcription (Bilibili + Xiaohongshu only).
    3. Image OCR (Xiaohongshu only).

- Various `test_*.py`
  - `test_media_tool.py` / `test_media_tool_async.py`: Verify MediaTool integration and asynchronous transcription.
  - `test_whisper_env.py` / `test_whisper_standalone.py`: Verify Whisper and FFmpeg environments.
  - `test_decoupled.py`: Verify complete flow after decoupling "Collection" and "Processing".
  - Other `debug_*.py`: Used for locating specific platform or dependency issues.

---

## Implemented Features List

- Multi-platform Favorites Collection
  - [x] Bilibili: Favorite list pull, metadata extraction, subtitle acquisition.
  - [x] Douyin: Favorite list pull, video info acquisition.
  - [x] Xiaohongshu: Code integration, list pull, graphic/video capture.
  - [x] WeChat Official Accounts: Path determination, body capture.
  - [ ] Scheduling & Storage (Daily timing, RAG format, incremental deduplication).

- Multi-modal Processing
  - [x] Audio/Video downloading (yt-dlp).
  - [x] Local offline speech transcription (Whisper).
  - [x] Local offline Image OCR (EasyOCR, XHS only).

---

## 10. Disclaimer

> **Please read the following terms carefully before using this project. Using this project indicates that you agree to all the following terms.**

1. **For Learning & Research Only**: This project (CyberMe / S-project) is purely an experimental tool for personal technical research and learning, aimed at exploring data collection, multi-modal processing, and knowledge management technologies.
2. **Legal Compliance**:
    *   Users must strictly abide by local laws and regulations (including but not limited to the "Cybersecurity Law of the People's Republic of China", "Data Security Law of the People's Republic of China", etc.) when using this project.
    *   Users should comply with the Robots protocol and Terms of Service of the target websites.
    *   It is **strictly prohibited** to use this project for any illegal purposes, including but not limited to: large-scale crawling causing Denial of Service (DDoS), infringing on personal privacy, stealing trade secrets, bypassing paywalls to obtain copyright-protected content, etc.
3. **Data Privacy & Copyright**:
    *   This project is only for users to crawl content **to which they have legitimate access rights** (such as their own favorites).
    *   Crawled data is limited to user's personal local offline use. **Unauthorized public dissemination, sale, or use for commercial profit is strictly prohibited.**
    *   The project author does not hold copyright to any crawled data; all content copyright belongs to the original authors and original platforms.
4. **Disclaimer of Liability**:
    *   This project is provided "AS IS", without any express or implied warranties.
    *   **The project author assumes no legal responsibility** for any direct or indirect losses (including but not limited to account banning, IP blocking, legal litigation, etc.) caused by the use of this project.
    *   If the target website requests to stop relevant crawling activities, please stop using this project immediately.
5. **About Removal**: If the content of this project unintentionally infringes upon your rights, please contact the author via GitHub Issue, and we will handle it promptly.
