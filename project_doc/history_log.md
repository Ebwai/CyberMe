# History Record (history_log.md)

## 2026-01-20 16:50 | 引入"Wait"状态优化回填逻辑
### 1. 问题记录
用户指出之前的修复（失败即重试）不够完美，希望对于“元数据抓取成功但资源下载失败”的任务，引入一个中间状态（Wait），在下次运行时跳过元数据抓取，仅重试资源下载。
### 2. 原因分析
*   **状态粒度不足**: [需求增加] 仅有“已处理”和“未处理”两种状态无法区分“部分成功”的情况，导致重复进行不必要的元数据抓取（如 API 请求、字幕提取等）。{问题确信度: High}
### 3. 解决方案
*   **状态定义扩展**: 在 `utils/storage.py` 中，`save_content` 现在返回三种状态：`success`（全成功）、`partial`（元数据成功但资源失败）、`fail`（关键失败）。
*   **存储逻辑增强**: `save_content` 增加 `skip_markdown` 参数。若设为 `True`，则跳过 Markdown 生成与写入，仅尝试下载缺失的资源。
*   **回填策略升级**: 更新 `backfill_favorites.py`：
    *   在 `backfill_state.json` 中增加 `wait_ids` / `wait_urls` 列表。
    *   遍历时，若 ID 在 `wait_ids` 中，则标记为 `is_wait`。
    *   对于 B站，若 `is_wait` 为真，跳过字幕提取 API 调用。
    *   调用 `save_content(item, skip_markdown=is_wait)`。
    *   根据返回状态动态维护 `processed_ids` 和 `wait_ids`：成功则移入 processed，部分成功则移入/保留在 wait。

---

## 2026-01-20 16:30 | 修复 B站音频下载超时与回填逻辑优化
### 1. 问题记录
用户反馈 `backfill_favorites.py` 运行时出现 `_ssl.c:1112: The handshake operation timed out` 错误，导致 B站音频下载失败。且用户担心因下载失败而导致的不完整内容在未来不会被重试。
### 2. 原因分析
*   **SSL 超时**: [真实问题原因] `yt-dlp` 默认配置在网络不稳定或特定服务器握手时超时时间过短（默认较短），且缺少模拟浏览器的 Headers 导致连接不稳定。{问题确信度: High}
*   **状态记录逻辑**: [真实问题原因] 原有的 `backfill_favorites.py` 在调用 `save_content` 后无论成功与否都将 ID 标记为 `processed_ids`，导致失败的任务被永久跳过。{问题确信度: High}
### 3. 解决方案
*   **优化 MediaTool**: 在 `utils/media_tool.py` 中将 `yt-dlp` 的 `socket_timeout` 增加至 60秒，并添加 User-Agent 和 Referer 请求头。
*   **状态反馈机制**: 修改 `utils/storage.py` 的 `save_content` 函数，使其在音频/视频下载失败时返回 `False`。
*   **回填逻辑调整**: 修改 `backfill_favorites.py`，仅当 `save_content` 返回 `True` 时才将 ID 加入 `processed_ids`，确保失败任务在下次运行时重试。

---

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
