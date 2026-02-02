# 需求规格说明书 (SRS)

## 1. 功能需求

### 1.1 统一调度控制
- **1.1.1 定义时触发**:
    - **采集任务**: 每日 22:00 自动启动。负责从各平台拉取元数据及媒体文件。
    - **处理任务**: 每日 23:00 自动启动。负责扫描本地已下载的媒体文件，进行 AI 转写或 OCR 处理。
        - **OCR 范围**: 仅限小红书 (Xiaohongshu)。
        - **转写范围**: 仅限 B站 (Bilibili) 和 小红书 (Xiaohongshu)。
- **1.1.2 增量检测 (Sync-Point)**: 
    - 系统不再全量扫描，而是通过 `StateManager` 记录各平台上次成功抓取的最新作品 ID。
    - 采集过程中一旦探测到该 ID，立即停止向下扫描，确保仅抓取新加入收藏的内容。
    - 同步点仅在整个平台内容保存成功后才会更新，确保原子性。

### 1.4 媒体智能处理子系统 (Media Intelligence)

#### 1.4.1 图片 OCR (Optical Character Recognition)
- **目标**: 提取图片中的文字信息，增强 RAG 检索的语义覆盖度。
- **适用范围**: 仅限小红书 (Xiaohongshu) 的图片资源。
- **输入**: 
    - 本地 `assets` 目录下的 `.jpg` / `.png` 图片文件。
- **处理流程**:
    - **调度**: 每日 23:00 批处理任务触发。
    - **引擎**: 调用 EasyOCR (本地 GPU/CPU)。
    - **逻辑**: 遍历未处理的图片 -> 识别文本 -> 拼接文本块。
- **输出**: 
    - 将识别到的文本以 `[OCR Content]` 标签包裹，追加到对应 Markdown 文件的末尾。

#### 1.4.2 音视频转写 (ASR)

#### 1.2.1 小红书 (XHS)
- **输入**:
    - `cookie`: 包含 `web_session`, `a1` 等关键字段。
    - `user_id`: 目标用户的 ID。
    - `collect_id`: 收藏夹 ID（若为空则抓取“所有收藏”）。
- **处理**:
    - *接口*: 调用 `Spider_XHS` 封装的 API。
    - *范围*: 仅抓取收藏夹内容。
    - *去重*: 采用 Sync-Point 策略。匹配 `crawl_state.json` 中的 `note_id` 后截断。
    - *详情*: `get_note_info(note_id)` 获取 `title`, `desc`, `images_list`, `video_url`。
    - *视频下载*: 识别 `video_url` 并通过 `aiohttp` 下载 `video.mp4` 至内容文件夹。
    - *环境兼容性*: 增加 `verify=False` 和 `NO_PROXY` 环境变量以绕过特定网络/SSL 限制。
    - *特殊逻辑*: 识别并跳过“评论区”抓取。
- **输出**: JSON 对象
  ```json
  { "id": "note_123", "title": "...", "content": "...", "images": ["url1"], "author": "..." }
  ```

#### 1.2.2 B站 (Bilibili)
- **输入**:
    - `SESSDATA`: 核心认证 Cookie。
    - `media_id`: 收藏夹 ID。
- **处理**:
    - *列表 API*: `GET https://api.bilibili.com/x/v3/fav/resource/list?media_id={id}& pn={page}&ps=20`
    - *范围*: 仅抓取收藏夹内容。
    - *去重*: 采用 Sync-Point 策略。匹配 `crawl_state.json` 中的 `bv_id` 后截断。
    - *字幕 API*: 使用 `bilibili-api-python` 的 `get_subtitle(bvid)`。
        - 优先: `lang=zh-CN` (官方CC)。
        - 再次: `lang=ai-zh` (AI生成)。
        - 失败: **下载音频**。调用 `MediaTool.download_audio` 将音频保存至该视频的专属存储目录，并在 Markdown 中标记 `[PENDING_TRANSCRIPTION]`。
- **输出**:
  ```json
  { "bvid": "BV...", "title": "...", "subtitle_text": null, "audio_file": "BV...wav", "author": "...", "video_url": "..." }
  ```

### 1.5 非功能需求 (Non-functional Requirements)

#### 1.5.1 法律合规与免责
- **免责声明展示**: 在项目根目录 README.md 中必须包含显著的免责声明章节。
- **使用限制**:
    - 必须在文档中明确禁止商业使用。
    - 代码逻辑中应包含基本的防滥用措施（如默认的请求间隔）。
- **隐私合规**: 所有抓取数据仅限本地存储 (`F:\DataInput`), 禁止任何形式的自动上传或共享。

#### 1.2.3 抖音 (Douyin)
- **输入**:
    - `cookie`: 必须包含 `tt_webid`, `sessionid`。建议从 Chrome 插件或浏览器直接提取。
- **处理**:
    - *策略*: 使用 Playwright 启动浏览器 -> 注入 Stealth 脚本 -> 访问收藏页。
    - *抓取*: 拦截网络请求响应 `web/aweme/list` 或解析 DOM 元素。
    - *签名*: 若使用 API 请求，需注入 JS 执行 `window.byted_acrawler.sign(url)` 获取 `a_bogus`。
    - *字幕*: 解析视频详情 JSON 中的 `video.caption_info`。
- **输出**: 标准化视频对象。

#### 1.2.4 微信公众号 (WeChat)
- **输入**:
    - `db_path` (可选): PC 端 `Favorites.db` 路径。
    - `urls_file`: `F:\DataInput\wechat_urls.txt` (作为备用输入源)。
- **处理**:
    - *优先方案 (本地数据库)*: 尝试连接 SQLite，若无法解密则报错提示用户。
    - *备选方案 (URL 列表)*:
        1. 读取 TXT 文件中的 URL。
        2. Playwright 访问 URL。
        3. 提取 `#activity-name` (标题), `#js_content` (正文), `#js_name` (公众号名称)。
        4. 将 HTML 正文转换为 Markdown (使用 `html2text` 库)。
- **输出**:
  ```json
  { "title": "...", "author": "公众号名", "content_md": "...", "url": "..." }
  ```

### 1.3 数据存储与格式输出

#### 1.3.1 目录结构 (Update: One Folder Per Post)
```text
F:\DataInput\
    YYYY-MM-DD\
        [Platform]\[Platform]_[Author]_[Title]\
             [Platform]_[Author]_[Title].md
             assets\
                 [Image_ID].jpg
             video.mp4      # (可选)
             audio.wav      # (可选，仅B站兜底)
```

#### 1.3.2 存储格式 (Markdown)
采用 YAML Frontmatter + 标准 Markdown 格式，同时满足机器解析 (RAG) 和人类阅读需求。

- **RAG 友好性**: 所有元数据在 Frontmatter 中，正文结构清晰，便于 Splitter 分割。
- **人类可读性**: 包含一级标题、作者信息块，图片使用标准 Markdown 图片语法嵌入，正文段落分明。

**Markdown 模板示例**:
```markdown
---
title: [标题]
url: [原始链接]
author: [作者]
platform: [Bilibili/Douyin/XHS/WeChat]
publish_time: [发布时间]
crawl_time: [抓取时间]
tags: [标签]
---
# [标题]
> 作者: [作者]  发布时间: [发布时间]  [查看原文]([原始链接])

![封面图](assets/cover.jpg)

## 简介/正文
[正文内容]

(若是图文，图片按顺序插入)
![图1](assets/img1.jpg)

## 字幕/文稿
[字幕文本内容]
```

### 1.4 媒体智能处理子系统 (Media Intelligence)

#### 1.4.1 图片 OCR (Optical Character Recognition)
- **目标**: 提取图片中的文字信息，增强 RAG 检索的语义覆盖度。
- **适用范围**: 仅限小红书 (Xiaohongshu) 的图片资源。
- **输入**: 
    - 本地 `assets` 目录下的 `.jpg` / `.png` 图片文件。
- **处理流程**:
    - **调度**: 每日 23:00 批处理任务触发。
    - **引擎**: 调用 EasyOCR (本地 GPU/CPU)。
    - **逻辑**: 遍历未处理的图片 -> 识别文本 -> 拼接文本块。
- **输出**: 
    - 将识别到的文本以 `[OCR Content]` 标签包裹，追加到对应 Markdown 文件的末尾。

#### 1.4.2 音视频转写 (ASR)
- **目标**: 将 B站视频的音频流或小红书的短视频音频转换为文本。
- **引擎**: OpenAI Whisper (Local).

## 2. 非功能需求 (NFR)
- **稳定性**: 爬虫需具备重试机制 (Retry 3 times)。
- **防封控**:
    - 请求间隔随机化 (Random delay 2-5s)。
    - 支持 Cookie 失效报警（如通过 Log 输出）。
- **性能**: 单次运行应在 30 分钟内完成（视当日更新量而定）。

## 3. 用例详情 (Use Cases)
| ID | 用例名称 | 角色 | 前置条件 | 流程简述 | 结果 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| UC-01 | 每日自动抓取 | System | 22:00 到达，Config配置正确 | 1. 启动调度器<br>2. 依次运行各平台模块<br>3. 汇总数据<br>4. 保存文件 | 数据写入 F:\DataInput |
| UC-02 | 获取B站字幕 | System | 拥有有效SESSDATA | 1. 获取视频CID<br>2. 请求字幕API<br>3. 解析JSON转文本 | 获得字幕文本 |

## 4. 需求追踪
- [✓] UC-01 每日调度实现
- [✓] UC-02 B站 API 对接
- [✓] XHS 模块迁移与测试（包含视频下载）
- [✓] RAG 格式模板设计（包含子文件夹结构）