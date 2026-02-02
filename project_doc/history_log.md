# History Record (history_log.md)

## 2026-02-02 11:45 | 添加法律免责声明与文档合规化
### 1. 问题记录
用户要求在 `README.md` 中增加免责条款，以规避开源爬虫项目被他人恶意使用可能带来的法律风险。
### 2. 原因分析
*   **法律合规**: [真实问题原因] 爬虫类项目天然具有法律敏感性。根据开源社区惯例及《网络安全法》等法律要求，必须明确告知用户仅限个人学习/研究使用，并界定责任边界。{问题确信度: High}
### 3. 解决方案
*   **README 更新**: 在 `README.md` 末尾增加“10. 免责声明 (Disclaimer)”章节，包含学习用途限定、法律合规要求、隐私版权说明及免责条款。
*   **文档同步**: 
    *   在 `SSRD.md` 中增加“法律合规与风险控制”章节。
    *   在 `SRS.md` 中增加“非功能需求 - 法律合规与免责”章节。

---

## 2026-01-29 11:30 | 优化 Bilibili 音频下载稳定性
### 1. 问题记录
用户反馈在爬取 Bilibili 时，部分视频音频下载正常，但部分出现 Read Timeout 导致下载失败。
### 2. 原因分析
*   **反爬策略 (Throttling)**: [真实问题原因] Bilibili 对未携带 Cookie 或 Referer 异常的流量进行限速或断连（Read Timeout）。`yt-dlp` 默认仅模拟浏览器 UA 但未复用爬虫的认证信息，被识别为异常流量。{问题确信度: High}
*   **网络参数**: 虽然之前增加了超时时间，但在低速限流状态下（如 10KB/s），大文件（Chunk Size 10MB）仍可能触发读取超时。
### 3. 解决方案
*   **Cookie 注入**: 修改 `utils/media_tool.py`，自动检测 Bilibili 链接并注入 `settings` 中的 `SESSDATA`, `bili_jct`, `buvid3` 到 HTTP Header 中。
*   **Referer 修正**: 将 Referer 从静态主页修改为具体的视频 URL，通过防盗链校验。

---

## 2026-01-27 18:30 | 文档完善：OCR 方案与选型
### 1. 问题记录
用户要求在系统架构和需求文档中补充 OCR 的工作流程及技术选型理由（EasyOCR）。
### 2. 原因分析
*   **文档缺失**: [真实问题原因] 之前仅在代码中实现了 OCR 功能，未在 `System_Architecture.md` 和 `SSRD.md` 中记录具体的技术决策和流程细节。{问题确信度: High}
### 3. 解决方案
*   **更新 SSRD**: 在“软件系统需求定义”中增加小红书图片 OCR 方案的选型理由（场景匹配、性能平衡、部署成本）。
*   **更新架构图**: 在“系统架构说明书”中详述 OCR 子模块的输入输出及懒加载工作流。
*   **同步 SRS/TestPlan**: 在需求规格说明书中补充媒体智能处理子系统需求，在测试计划中增加 OCR 单元测试项。

---

### 1. 问题记录
用户反馈使用代码下载小红书视频失败（HTTP 403 Forbidden），但使用 CLI 命令行直接下载可以成功。同时，Bilibili 下载偶发 Socket Timeout。
### 2. 原因分析
*   **小红书 403**: [真实问题原因] 代码中 `utils/media_tool.py` 之前硬编码了 `Referer: https://www.bilibili.com/`，导致下载小红书视频时因 Referer 跨域/防盗链校验失败被拒绝。CLI 成功是因为 CLI 默认不带此 Referer。{问题确信度: High}
*   **Bilibili 超时**: [真实问题原因] `yt-dlp` 默认优先使用 IPv6，且 B站 CDN 对 HTTP/2 或 IPv6 支持不稳定，导致握手阶段超时。{问题确信度: High}
### 3. 解决方案
*   **动态 Referer**: 修改 `utils/media_tool.py`，移除硬编码 Header，改为优先使用传入的 `headers` 参数。若无传入，才使用默认 B站 Referer。
*   **配置增强**: 在 `utils/media_tool.py` 的 `ydl_opts` 中增加：
    *   `force_ipv4: True`: 强制 IPv4 避免 IPv6 黑洞。
    *   `socket_timeout: 60`: 延长超时时间。
    *   `http_chunk_size: 10MB`: 优化分块下载稳定性。
*   **传递 Header**: 修改 `utils/storage.py`，在调用下载时将 `item.download_headers`（含正确 Referer）传递给 `MediaTool`。

---

## 2026-01-27 18:00 | 处理 B站失效视频逻辑
### 1. 问题记录
用户反馈遇到“啥都木有”或“稿件不可见”的 B站失效视频时，不应将其加入 `wait_ids` 进行无限重试。
### 2. 原因分析
*   **逻辑缺失**: [真实问题原因] 原逻辑仅判断是否成功获取字幕，若失败（含失效视频）则视为 incomplete，导致 ID 进入 `wait_ids`。{问题确信度: High}
### 3. 解决方案
*   **异常识别**: 修改 `crawlers/bilibili.py`，捕获特定错误信息（-404, 62002）并返回 `INVALID_VIDEO` 标记。
*   **状态豁免**: 修改 `backfill_favorites.py`，若检测到 `INVALID_VIDEO`，强制将状态标记为 `success` 并加入 `processed_ids`，从而在未来跳过该视频。

---

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
