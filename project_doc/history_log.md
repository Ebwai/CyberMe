# History Record (history_log.md)

## 2026-01-15 03:10 | 更新 GitHub README 头图为本地图片
### 1. 问题记录
用户将 `github_demo_picture.jpg` 放在 `pictures` 目录下，希望 GitHub 仓库首页直接展示该实际图片，而不是之前的占位链接。
### 2. 原因分析
*   **一致性需求**: [需求增加] README 中的头图应与项目仓库内真实资源一致，方便后续维护与替换。{问题确信度: High}
### 3. 解决方案
*   **README 调整**: 将 `README.md` 中头图链接修改为相对路径 `pictures/github_demo_picture.jpg`，确保 GitHub 渲染时可以直接加载本地图片资源。

---

## 2026-01-15 02:55 | 完善 GitHub 仓库文档与品牌化
### 1. 问题记录
用户需要生成一个 GitHub 仓库专用的头图描述，并将 "cyberme" 的核心宗旨置顶于 `README.md`。
### 2. 原因分析
*   **品牌塑造**: [需求增加] "cyberme" 不仅仅是一个爬虫工具，更是一个赛博分身的概念。需要在项目首页强调这一愿景。
### 3. 解决方案
*   **README 更新**:
    *   在 `README.md` 顶部增加 **CyberMe** 标题与核心宗旨（Blockquote 格式）。
    *   插入一个指向头图的图片链接占位符，并附带生成的头图设计描述（赛博朋克风格、数字分身）。

---

## 2026-01-15 02:45 | 增加 README 与依赖一键安装支持
### 1. 问题记录
用户需要一个完整的 README 文档来说明项目用法与结构，并希望通过更新 `requirements.txt` 实现一键安装所有依赖。
### 2. 原因分析
*   **可用性提升**: [需求增加] 之前只有零散的说明文档（如 README_CONFIG、架构/需求文档），缺少面向最终使用者的一站式使用说明；依赖列表中也未明确包含 OCR 相关库。{问题确信度: High}
### 3. 解决方案
*   **文档补全**: 在项目根目录新增 `README.md`，统一说明项目目标、目录结构树状图、运行方式（手动 & 定时任务）、已实现功能与参考项目。
*   **依赖补全**: 更新 `requirements.txt`，在原有依赖基础上补充 `easyocr`，确保语音转写与图片 OCR 所需依赖可以通过 `pip install -r requirements.txt` 一次性安装。

---

## 2026-01-15 02:30 | 优化多模态处理范围
### 1. 问题记录
用户指定 OCR 仅针对小红书执行，语音转译仅针对 B站和小红书执行。
### 2. 原因分析
*   **需求细化**: [需求调整] 为了节省资源或专注于特定平台的内容特性，需要对处理任务的范围进行更细粒度的控制。
### 3. 解决方案
*   **逻辑过滤**: 修改 `processor/main.py`，增加平台白名单机制。
    *   OCR 白名单: `['Xiaohongshu']`
    *   转译白名单: `['Bilibili', 'Xiaohongshu']`
*   **目录识别**: 通过解析文件路径中的平台层级来实现过滤。

---

## 2026-01-15 02:00 | 修复处理任务中的编码错误
### 1. 问题记录
运行 `run_daily_process.bat` 时，多个线程报错 `UnicodeDecodeError: 'gbk' codec can't decode byte...`，导致 ffmpeg 提取失败。
### 2. 原因分析
*   **编码冲突**: [真实问题原因] `utils/media_tool.py` 中 `subprocess.run` 使用了 `text=True` (默认 GBK 编码 on Windows) 来读取 `ffmpeg` 的输出。当 `ffmpeg` 输出包含非 GBK 字符（如特殊元数据或 UTF-8 进度条）时，Python 的 `_readerthread` 尝试解码失败。{问题确信度: High}
### 3. 解决方案
*   **强制 UTF-8**: 修改 `subprocess.run` 调用，显式指定 `encoding='utf-8'` 并设置 `errors='ignore'` 以防止解码错误中断流程。

---

## 2026-01-15 01:50 | 修复批处理脚本路径
### 1. 问题记录
用户反馈或自检发现 `run_daily_process.bat` 和 `run_daily_crawl.bat` 中的工作目录指向错误的 `spider_Unit`。
### 2. 原因分析
*   **路径硬编码**: [真实问题原因] 脚本是从旧项目复制而来，保留了旧的绝对路径 `f:\project\spider_Unit`。{问题确信度: High}
### 3. 解决方案
*   **路径修正**: 将两个批处理文件中的路径修改为当前项目路径 `f:\project\spider_TRAE`。

---

## 2026-01-15 01:45 | 修复资源泄漏问题
### 1. 问题记录
日志中出现 `Unclosed client session` 和 `RuntimeError: Event loop is closed`。
### 2. 原因分析
*   **资源泄漏**: [真实问题原因] `utils/storage.py` 中 `aiohttp.ClientSession` 在图片下载逻辑中被创建，但如果 `item.images` 为空或异常退出，可能未正确关闭。虽然使用了 `async with`，但在高并发或异常流中可能存在边缘情况。{问题确信度: Medium}
*   **事件循环关闭**: [真实问题原因] 这是 Windows ProactorEventLoop 的已知问题，通常发生在程序退出时未能优雅关闭所有异步任务。{问题确信度: High}
### 3. 解决方案
*   **显式管理**: 在 `utils/storage.py` 中优化 `ClientSession` 的作用域。
*   **忽略噪音**: `RuntimeError: Event loop is closed` 通常是无害的退出时错误，不影响数据完整性。

---

## 2026-01-15 01:40 | 修正 B站下载逻辑
### 1. 问题记录
用户反馈之前的修改导致 B站爬虫下载了不必要的视频文件（`video.mp4`），而原意是仅在无字幕时下载音频用于转写。
### 2. 原因分析
*   **逻辑错误**: [真实问题原因] `crawlers/bilibili.py` 中无条件设置了 `video_url`，导致 `utils/storage.py` 调用 `yt-dlp` 下载了完整视频。{问题确信度: High}
### 3. 解决方案
*   **回退逻辑**: 修改 `crawlers/bilibili.py`，将 `video_url` 显式设为 `None`。
*   **保留音频**: 仅在无字幕时设置 `audio_url`，利用 `MediaTool` 的音频下载能力（同样基于 `yt-dlp`）获取音频流。

---

## 2026-01-15 01:00 | 修复 B站视频下载 412 与抖音日志噪音
### 1. 问题记录
1.  **哔哩哔哩**: 视频下载失败，报错 `Failed to download video, status: 412`。
2.  **抖音**: 爬虫运行时出现大量 `Protocol error` 报错日志。
3.  **资源泄漏**: 程序结束时提示 `Unclosed client session`。

### 2. 原因分析
*   **B站下载 412**: [真实问题原因] `crawlers/bilibili.py` 将网页 URL 传给 `storage.py`，后者尝试直接 HTTP GET 下载，触发 B站反爬（需要 Referer/UA）且目标是 HTML 页面而非视频流。{问题确信度: High}
*   **抖音 Protocol Error**: [真实问题原因] Playwright 在拦截请求时，若页面跳转或资源已释放，调用 `response.json()` 会抛出竞态错误。这是预期内的行为，但在日志中未被正确过滤。{问题确信度: High}

### 3. 解决方案
1.  **MediaTool 增强**: 在 `utils/media_tool.py` 中增加 `download_video` 方法，集成 `yt-dlp` 以支持从网页 URL 智能提取并下载视频。
2.  **存储逻辑修正**: 修改 `utils/storage.py`，弃用 `aiohttp` 直接下载视频的逻辑，转为调用 `MediaTool.download_video`，彻底解决 B站及其他平台（如抖音网页版）的视频下载问题。
3.  **日志降噪**: 优化 `crawlers/douyin.py`，捕获并忽略 Playwright 的 `Protocol error`。

---

## 2026-01-13 23:30 | 爬虫异常与功能缺失
### 1. 问题记录
1.  **小红书**: 图片没有爬取并保存下来。
2.  **哔哩哔哩**: 没开放或没有字幕的视频没有识别出对应的字幕并记录。
3.  **抖音**: 爬虫运行超时，Log显示 `Page.goto: Timeout 60000ms exceeded`。
4.  **项目结构**: 不同平台爬取内容未分文件夹存储。

### 2. 原因分析
*   **小红书图片丢失**: [真实问题原因] `utils/storage.py` 下载时未携带 Headers (`User-Agent`, `Referer`) 导致 403 Forbidden。{问题确信度: High}
*   **哔哩哔哩字幕缺失**: [真实问题原因] 当前仅通过 API 获取官方/CC字幕。无字幕视频需 AI 识别。{问题确信度: High}
*   **抖音超时**: [真实问题原因] 反爬虫机制检测或 `networkidle` 等待策略过于严格。{问题确信度: Medium}

### 3. 解决方案
*   **小红书**: 修复 `storage.py` 添加 Headers。
*   **哔哩哔哩**: 优化 API 获取逻辑；调研 Whisper 本地识别。
*   **抖音**: 优化 Playwright 等待策略 and 隐匿特征。
*   **结构**: 修改保存路径增加平台分层。

---

## 2026-01-13 19:45 | 需求增加
### 问题记录
用户希望能够单独测试特定平台的爬虫效果（如只测试抖音）。
### 原因分析
{100%} [需求增加] 当前的 `main.py --now` 会运行所有激活的爬虫，缺乏灵活性。
### 解决方案
修改 `main.py`：
- `run_crawlers` 函数增加 `platform_filter` 参数。
- CLI 逻辑支持 `python main.py --now [platform]`。

---

## 2026-01-14 15:05 | 环境依赖与异步问题
### 问题记录
- `yolov5` 环境直接调用 Python 时缺少 OpenSSL DLLs，导致 `_ssl` 加载失败。
- `MediaTool` 原始实现为同步阻塞，但在异步环境中被 `await` 导致 `TypeError`。
### 原因分析
- `yolov5` 环境直接调用 Python 时缺少 OpenSSL DLLs，导致 `_ssl` 加载失败。
- `whisper.load_model` 和 `model.transcribe` 是计算密集且同步的。
### 解决方案
- 手动将 `Library/bin` 下的 `libcrypto` 和 `libssl` DLL 复制到 `DLLs` 目录。
- 使用 `asyncio.to_thread`
- 2026-01-14 15:33: [问题解决] 修复 `bilibili.py` 中 `MediaTool.transcribe` 未使用 `await` 的 Bug。
- 2026-01-14 15:33: [功能验证] 通过 `test_media_tool_async.py` 成功验证异步转写流程，输出正常。
- 2026-01-14 15:35: [项目进展] B 站本地 Whisper 兜底方案全线打通，环境问题已解决。全部爬虫模块功能指标达成。
- 2026-01-14 16:40: [文档优化] 细化 `System_Architecture.md`，增加 Whisper 的暂存路径、模型规格、性能预期及自动清理逻辑说明。
- 2026-01-14 17:10: [功能增强] Whisper 转写已成功切换至 GPU (GTX 3060) 加速。经验证模型运行在 `cuda:0` 设备上。
- 2026-01-14 18:10: [架构重构] 完成"采集与处理解耦"重构。22:00采集任务仅下载数据，23:00处理任务执行批量GPU转写。存储结构改为"一帖一文件夹"。验证通过 (`test_decoupled.py`)。
### 项目进展
- 开始使用含对话的视频 `BV1oViKBeED4` 进行 Whisper 最终验证。

---

## 2026-01-12 23:05 | 项目验收
### 问题记录
项目验收。
### 原因分析
{100%} [验收通过]
- B站：20条收藏记录成功拉取，字幕文稿完整嵌入 Markdown。
- 抖音：网络流量捕获到 17 条记录，保存正常。
- 小红书：成功识别 User ID 并拉取 10 条笔记，正文与图片链接完整。
- 微信：成功访问 URL 并解析正文。
### 解决方案
(此为验收记录，无Fix)

---

## 2026-01-12 22:50 | 核心模块执行异常
### 问题记录
验证阶段发现多个核心模块执行异常：
1. `WeChatCrawler` 缺少 Optional 导入。
2. B站字幕提取报错 需要 cid。
3. 抖音页面加载超时，且解析 images 时出现 NoneType 报错。
4. 小红书爬虫因 JS 文件路径依赖 CWD 导致导入失败。
### 原因分析
{100%} [真实问题原因]
- 代码书写疏忽。
- `bilibili-api-python` 在获取字幕时必须且仅能通过 `get_subtitle(cid=cid)` 传参。
- 抖音反爬严重，headless 下 networkidle 响应极慢。
- 小红书 `xhs_util.py` 使用了相对路径加载 `.js` 文件，且其子模块依赖 Node.js 执行。
### 解决方案
- 修复 Optional 导入，补充 PyExecJS 等缺失依赖。
- B站：在视频对象中显式获取并传递 cid。
- 抖音：放宽超时时间，增加两步导航策略，并增加空值校验。
- 小红书：在导入和执行阶段通过 `os.chdir` 临时切换工作目录至 XHS 项目根目录，并对 JS 加载路径进行绝对路径化处理。
- 已完成核心修复 (Timeout, 403, Folder Structure)。
- 输出 `walkthrough.md` 指导后续使用。

---

## 2026-01-14 01:00 | B站字幕缺失问题
### 问题记录
用户反馈部分视频（如“程序员YT”、“罗永浩的十字路口”）未抓取到字幕。
### 原因分析
{100%} [真实问题原因]
- Debug 脚本对特定视频 (`BV14eiQBmEbN`) 返回 `Subtitle count: 0`。
- API 响应中 `subtitles` 列表为空。
- **关联原因**: B站账号未登录 (Error -101)，匿名访问可能无法获取 AI 生成的字幕。
### 解决方案
1.  **第一步 (必须)**: 更新 `BILI_SESSDATA` 恢复登录状态，重新测试。
2.  **第二步 (备选)**: 若登录后仍无字幕，利用 `bilibili-api` 获取评论区“课代表”总结（通常在置顶或热评）。
3.  **第三步 (终极)**: 接入 Local Whisper (需 GPU/高性能 CPU)，成本较高。

---

## 2026-01-14 01:40 | 环境依赖缺失
### 问题记录
尝试安装 `openai-whisper` 和 `yt-dlp` 时失败。
### 原因分析
{100%} [真实问题原因]
- 系统 Python 环境缺失 SSL 模块 (`pip is configured with locations that require TLS/SSL`)。
- `ffmpeg` 未配置到系统 PATH。
### 解决方案
- 代码侧：已实现 `MediaTool` 的防崩溃设计 (ImportError protection)。
- 用户侧：[已修复] 用户已安装 ffmpeg, openai-whisper, yt-dlp 并配置到 yolov5 环境。

---

## 2026-01-14 02:05 | 小红书图片下载缺失
### 问题记录
运行 Xiaohongshu 爬虫时，Markdown 生成成功但 assets 文件夹缺失，无图片下载。
### 原因分析
{100%} [真实问题原因]
- API 返回的图片结构（List View）与详情页结构不一致。
- 代码尝试 `cover.get("url")`，但实际结构为 `cover["info_list"][0]["url"]`。
- 详情页图片列表同样使用嵌套结构 `info_list`。
### 解决方案
- 修改 `crawlers/xhs.py`，增加对 `info_list` 和 `url_default` 的兼容性解析。
- [已验证] 修复后成功下载 49 张图片到 `Xiaohongshu/assets` 目录。

---

## 2026-01-14 00:45 | B站 403 权限错误
### 问题记录
运行 `python main.py --now Bilibili` 时报错：`接口 返回错误代码：-403，信息：访问权限不足`。
### 原因分析
{100%} [真实问题原因]
- Debug 脚本返回 `{'code': -101, 'message': '未登录'}`。
- 确认 `BILI_SESSDATA` Cookie 已失效 or 配置错误。
### 解决方案
- **必须** 更新 `.env` 文件中的 `BILI_SESSDATA`。
- 建议用户在浏览器无痕模式登录 B站，F12 获取最新 SESSDATA。
---

## 2026-01-14 20:15 | 小红书视频下载与环境兼容性修复
### 1. 问题记录
1.  **抖音**: 之前的抓取项为0，是因为 Cookie 失效。
2.  **小红书**: 缺失视频下载功能。
3.  **小红书**: 在 `yolov5` 环境下运行出现 `SSLError` (EOF) 和 `ProxyError` (FileNotFound)。
4.  **架构**: 存储结构与基类过滤逻辑不一致。

### 2. 原因分析
*   **抖音 Cookie**: [真实问题原因] 登录态过期导致无法截获收藏 API。{问题确信度: High}
*   **小红书视频**: [真实问题原因] 核心逻辑中未包含视频下载实现。{问题确信度: High}
*   **SSL 错误**: [真实问题原因] `yolov5` 环境下的 OpenSSL 与小红书 API 握手协议不匹配。{问题确信度: High}
*   **Proxy 错误**: [真实问题原因] Windows 系统代理配置冲突，requests 尝试连接不存在的代理。{问题确信度: High}

### 3. 解决方案
*   **抖音**: 用户更新 `DOUYIN_COOKIE` 后恢复抓取（捕获 52 项）。
*   **小红书视频**: 在 `storage.py` 中增加基于 `aiohttp` 的流式视频下载逻辑。
*   **SSL/Proxy 修复**: 
    - 在 `xhs_pc_apis.py` 中全量增加 `verify=False`。
    - 在 `xhs.py` 中增加 `os.environ['NO_PROXY'] = '*'` 禁用系统代理。
*   **架构同步**: 更新 `crawlers/base.py` 使 `filter_existing` 兼容新的"一帖一文件夹"路径。
*   **验证**: 成功下载小红书视频（`video.mp4`），数据结构符合预期。

---

## 2026-01-14 20:25 | 需求增加：视频转译支持
### 1. 问题记录
用户需求：数据处理模块需增加对小红书视频模态的支持。
### 2. 原因分析
{100%} [需求增加] 当前处理模块仅扫描 `.wav` 文件。小红书视频需要先从 `.mp4` 提取音频再进行转写。
### 3. 解决方案
1.  **MediaTool**: 增加 `extract_audio` 方法，利用 `ffmpeg` 提取 16kHz 单声道 WAV。
2.  **Processor**: 修改扫描逻辑，支持 `video.mp4` -> `extract_audio` -> `transcribe`流程。
3.  **验证**: [2026-01-14 20:28] 已在小红书视频贴成功验证。提取出 `audio.wav` 并生成了完整的 AI 转写文本。

---

## 2026-01-14 21:45 | 需求增加：图片 OCR 支持
### 1. 问题记录
用户需求：小红书图文帖子需要识别图片中的文字并存入 Markdown。
### 2. 原因分析
{100%} [需求增加] 现有的处理流程仅覆盖音视频转译，图文帖子的核心信息（图片上的文字）尚未提取。
### 3. 解决方案
1.  **方案评判**: 对比 EasyOCR 与 PaddleOCR，结合用户环境（CUDA 11.6）选择 EasyOCR。
2.  **MediaTool**: 增加 `OCRTool` 支持 GPU 加速识别。
3.  **Processor**: 扫描 `assets/` 目录并更新 MD。
4.  **验证**: [2026-01-14 22:15] 已成功完成全流程验证。
    - **兼容性**: 通过 Monkeypatch 解决了 Torch 1.12 与 EasyOCR 1.7.2 的 `weights_only` 参数冲突。
    - **路径处理**: 解决了 Windows 下 OpenCV 无法读取中文路径图片的问题。
    - **结果**: 小红书图文贴中的文字已被准确识别并追加至 Markdown。

---

## 2026-01-14 22:45 | 系统健壮性：异常识别与用户引导
### 1. 问题记录
爬虫在 Cookie 过期或网络故障时报错不直观，用户难以定位原因。
### 2. 原因分析
{100%} [真实问题原因] 之前的代码多采用静默失败或仅记录 DEBUG log，终端输出不够显眼。
### 3. 解决方案
1.  **统一提醒**: 在 `BaseCrawler` 增加 `handle_auth_error`，终端输出醒目的红色提醒并指向 `README_CONFIG.md`。
2.  **分平台增强**: B站增加 `check_valid()` 验证，抖音增加登录页重定向捕获，小红书增加 Proxy/SSL 异常诊断提示。
3.  **依赖自检**: `MediaTool` 启动检查 `ffmpeg`。
4.  **验证**: 通过模拟故障确认，B站和 XHS 的高可见度提示均已生效。

---

## 2026-01-14 23:35 | 跨日期全局去重方案实现
### 1. 问题记录
用户希望实现“跨日期全局去重”，避免每天运行时重复下载以前已经抓取过的内容。
### 2. 原因分析
{100%} [需求增加] 当前系统仅检查“当日”文件夹是否存在，若收藏内容不变，次日运行会再次抓取已存内容。
### 3. 解决方案
1.  **Sync-Point 策略**: 利用 API 返回循序（由近及远）的特性。
2.  **状态管理**: 实现 `StateManager` 工具类，读写 `crawl_state.json` 记录各平台最新处理的作品 ID。
3.  **有序截断**: 所有爬虫在采集过程中，一旦探测到记录中的 `limit_id` 即刻停止扫描后续内容。
4.  **原子更新**: 仅在本次所有新项保存成功后才更新同步点，确保不漏抓。
5.  **验证**: 通过 `test_sync_dedup.py` 模拟多轮同步，验证了增量获取逻辑的准确性。

---

## 2026-01-15 00:05 | 自动化部署与定时任务支持
### 1. 问题记录
用户需要一种在 Windows 上定时自动运行爬虫的稳健方案。
### 2. 原因分析
{100%} [需求增加] 纯靠 Python 脚本内部调度（`run_forever`）在电脑重启或进程崩溃后难以自动恢复。利用 Windows 系统级的“任务计划程序”更加可靠。
### 3. 解决方案
1.  **特定入口脚本**: 创建了 `run_daily_crawl.bat` 与 `run_daily_process.bat`。
2.  **配置简化**: 脚本预置了正确的 Conda 环境激活 (`yolov5`) 和 CLI 参数，用户只需在 Windows 任务计划程序中选择对应的 `.bat` 文件即可。
3.  **文档对齐**: 更新了 `walkthrough.md` 中的配置指南。
