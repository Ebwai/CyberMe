# CyberMe

> **创造你的一个赛博分身，既拥有大模型的通用知识，又拥有你的所有信息（没错，是所有，不止是表层的知识比如你的银行卡密码doge，更是你的内在，只要你愿意分享），并且接入了各种工具，使得你只需要发出指令，cyberme就可以像你一样（或者说就是你）在赛博世界做任何事（没错，任何事，只要你愿意）**

![CyberMe Header Image](pictures/github_demo_picture.jpg)

宏大目标和进度：
- [ ] 第一阶段：从现在开始，你获取的所有信息，AI也会同步获取一份(cyberme和你一起共同成长from now)
	- [x]  【S-project】网络社交媒体的高质量数据同步：小红书，哔哩哔哩，微信公众号，抖音所有存在收藏夹里的信息（你认为有一定价值的信息，你关注的信息）

## S-project项目概览

本项目是一个面向个人知识管理与内容采集的 **多平台收藏夹聚合与离线处理系统**，支持从以下平台的“收藏夹”或指定列表中自动拉取内容并本地化存储：
- Bilibili（B站）
- Douyin（抖音）
- Xiaohongshu（小红书）
- WeChat 公众号（通过 URL 列表）

系统每天分两阶段运行：
- **22:00 采集任务**：从各平台抓取当日新增收藏内容，保存为 Markdown + 媒体文件。
- **23:00 处理任务**：对已下载的多媒体进行离线处理（语音转文字、图片 OCR），并把结果写回 Markdown。

所有输出统一存放在 `F:\DataInput\YYYY-MM-DD\...` 目录，既方便 RAG 建库，又适合直接阅读。

---

## 目录结构（树状图说明）

项目根目录（`f:\project\spider_TRAE`）的核心结构如下：

```text
spider_TRAE/
├─ main.py                         # 入口：采集任务调度器（22:00）
├─ processor/
│  └─ main.py                      # 入口：处理任务（23:00：语音转写 & OCR）
├─ crawlers/
│  ├─ base.py                      # 爬虫基类 & ContentItem 数据结构
│  ├─ bilibili.py                  # B站收藏夹爬虫（字幕 + 音频兜底）
│  ├─ douyin.py                    # 抖音收藏夹爬虫（Playwright 反爬对抗）
│  ├─ xhs.py                       # 小红书收藏夹爬虫（复用 Spider_XHS）
│  └─ wechat.py                    # 微信公众号内容爬虫（基于 URL 文件）
├─ utils/
│  ├─ storage.py                   # 统一存储：Markdown 渲染 + 媒体下载
│  ├─ media_tool.py                # 媒体工具：yt-dlp + Whisper + OCR
│  └─ state_manager.py             # Sync-Point 状态管理（跨日期去重）
├─ project_doc/
│  ├─ SSRD.md                      # 软件系统需求定义
│  ├─ SRS.md                       # 需求规格说明书
│  ├─ System_Architecture.md       # 系统架构说明书
│  ├─ testplan.md                  # 测试计划
│  └─ history_log.md               # 历史问题与修复记录
├─ local_knowledge_base/
│  ├─ Spider_XHS/                  # 外部小红书项目（复用其签名与 API）
│  ├─ B 站无字幕视频字幕识别方案深度解析（2025-2026 最新）.md
│  ├─ B站字幕提取的调研.md
│  └─ 调研.md
├─ logs/
│  └─ spider_*.log                 # 爬虫运行日志（按日期自动轮转）
├─ run_daily_crawl.bat             # Windows 定时任务：启动采集任务
├─ run_daily_process.bat           # Windows 定时任务：启动处理任务
├─ config.py                       # 全局配置 & .env 读取（路径、Cookie 等）
├─ .env                            # 私密配置（Cookie、收藏夹 ID 等）
├─ README_CONFIG.md                # 各平台配置（Cookie/ID）获取指南
├─ requirements.txt                # Python 依赖清单
└─ 各类 test_*.py / debug_*.py      # 环境验证与功能测试脚本
```

采集出的数据目录结构示例（位于 `F:\DataInput` 下）：

```text
F:\DataInput\
└─ YYYY-MM-DD\
   ├─ Bilibili\
   │  └─ Bilibili_作者_标题\
   │     ├─ Bilibili_作者_标题.md
   │     └─ assets/ & audio.wav (可选)
   ├─ Douyin\
   │  └─ Douyin_作者_标题\
   │     ├─ Douyin_作者_标题.md
   │     └─ assets/ & video/audio（按平台能力）
   ├─ Xiaohongshu\
   │  └─ Xiaohongshu_作者_标题\
   │     ├─ Xiaohongshu_作者_标题.md
   │     └─ assets/ & video.mp4 & audio.wav
   └─ WeChat\
      └─ WeChat_公众号_标题\
         ├─ WeChat_公众号_标题.md
         └─ assets/（若有图片）
```

---

## 环境准备与依赖安装

项目默认运行在 Conda 环境 `yolov5` 中（已在实际使用中验证）。推荐步骤：

1. **创建 / 使用 Conda 环境**

   ```bash
   conda create -n yolov5 python=3.9  # 如已有可跳过
   conda activate yolov5
   ```

2. **安装 Python 依赖**

   在项目根目录 `f:\project\spider_TRAE` 下：

   ```bash
   pip install -r requirements.txt
   ```

3. **安装浏览器 & Playwright 驱动（用于抖音）**

   ```bash
   playwright install
   ```

4. **安装 FFmpeg**

   - Windows 上建议通过 `choco` 或官方安装包安装 FFmpeg，并确保 `ffmpeg` 在系统 PATH 中。
   - 可通过以下命令检查：

     ```bash
     ffmpeg -version
     ```

5. **准备 Whisper 模型目录（可选）**

   在 `config.py` 中已约定：
   - `WHISPER_MODEL_DIR`: 模型存放路径（默认 `F:\Spider_proj\models`）
   - `TEMP_AUDIO_DIR`: 音频临时路径（默认 `F:\Spider_proj\temp`）

   若默认路径不存在，首次运行会自动创建文件夹。

---

## 配置说明（.env 与 Cookie）

所有敏感配置通过 `.env` 文件注入，字段定义见 [config.py](file:///f:/project/spider_TRAE/config.py) 和 [README_CONFIG.md](file:///f:/project/spider_TRAE/README_CONFIG.md)。

关键字段包括：
- B站：`BILI_SESSDATA`, `BILI_JCT`, `BILI_BUVID3`, `BILI_MEDIA_ID`
- 抖音：`DOUYIN_COOKIE`
- 小红书：`XHS_COOKIE`
- 微信：`WECHAT_URLS_FILE`（默认 `F:\DataInput\wechat_urls.txt`），`WECHAT_DB_PATH`（可选）

详细获取步骤（如何在浏览器中复制 Cookie / media_id），请参考 [README_CONFIG.md](file:///f:/project/spider_TRAE/README_CONFIG.md)。

---

## 使用方法

### 1. 手动运行采集任务（22:00 逻辑）

在 Conda 环境 `yolov5` 中，进入项目根目录：

```bash
conda activate yolov5
cd f:\project\spider_TRAE
python main.py --now
```

- 默认会执行所有已配置平台的采集（Bilibili / Douyin / Xiaohongshu / WeChat）。
- 如需只采集某个平台（例如仅 B站），可使用：

```bash
python main.py --now Bilibili
python main.py --now Douyin
python main.py --now Xiaohongshu
python main.py --now WeChat
```

采集完成后，可在 `F:\DataInput\YYYY-MM-DD\...` 目录中看到对应的 Markdown 与媒体文件。

### 2. 手动运行处理任务（23:00 逻辑）

```bash
conda activate yolov5
cd f:\project\spider_TRAE
python -m processor.main
```

该任务会：
- 扫描当日目录 `F:\DataInput\YYYY-MM-DD`。
- 对符合范围的音频 / 视频执行 Whisper 语音转文字：
  - **仅 B站 + 小红书** 会做语音转译。
- 对符合范围的图片执行 OCR（EasyOCR）：
  - **仅小红书** 会做 OCR 识别。
- 将转写结果和 OCR 结果自动追加到对应 Markdown 文件中：
  - 字幕/文稿部分：`## 字幕/文稿` 下 `[AI-Generated Transcript]` 段落。
  - 图片 OCR 部分：`## 图片 OCR 结果` 段落。

### 3. Windows 任务计划程序一键自动化

项目已经准备了两个 `.bat` 脚本：
- [run_daily_crawl.bat](file:///f:/project/spider_TRAE/run_daily_crawl.bat) ：每日 22:00 采集任务。
- [run_daily_process.bat](file:///f:/project/spider_TRAE/run_daily_process.bat) ：每日 23:00 处理任务。

在 Windows“任务计划程序”中：
1. 创建任务 -> 触发器设定时间（22:00 / 23:00）。
2. 操作中选择“启动程序”，指向对应 `.bat` 文件。
3. 确保任务运行账户有访问 `F:\DataInput` 和 Conda 环境的权限。

---

## 模块功能速览

- [main.py](file:///f:/project/spider_TRAE/main.py)
  - 负责初始化日志、调度 APScheduler、按平台启动各爬虫。
  - 支持命令行参数 `--now [platform]` 实时触发。

- [crawlers/base.py](file:///f:/project/spider_TRAE/crawlers/base.py)
  - 定义 `ContentItem` 数据结构。
  - 实现跨平台的去重策略（Sync-Point + 本地文件存在性检查）。
  - 提供认证失败统一提示 `handle_auth_error`。

- [crawlers/bilibili.py](file:///f:/project/spider_TRAE/crawlers/bilibili.py)
  - 调用 `bilibili-api-python` 获取收藏夹列表与视频详情。
  - 优先拉取官方 / AI 字幕；若缺失，则通过 `MediaTool` 下载音频，后续由处理任务转写。

- [crawlers/douyin.py](file:///f:/project/spider_TRAE/crawlers/douyin.py)
  - 使用 Playwright 启动浏览器，从收藏页面拦截 `favorite` 接口。
  - 处理抖音特有加密参数与风控；对部分 Protocol Error 做降噪处理。

- [crawlers/xhs.py](file:///f:/project/spider_TRAE/crawlers/xhs.py)
  - 复用 `local_knowledge_base/Spider_XHS` 的 API 与签名逻辑。
  - 解决图片 403、防代理/SSL 问题，并将结果统一落地为 Markdown + assets。

- [crawlers/wechat.py](file:///f:/project/spider_TRAE/crawlers/wechat.py)
  - 从 `WECHAT_URLS_FILE` 读取 URL 列表。
  - 使用 Playwright / requests 抓取文章 HTML，并通过 `html2text` 转 Markdown。

- [utils/storage.py](file:///f:/project/spider_TRAE/utils/storage.py)
  - 根据 `ContentItem` 渲染 YAML Frontmatter + Markdown 正文。
  - 负责下载图片/音频/视频到对应的帖子目录。

- [utils/media_tool.py](file:///f:/project/spider_TRAE/utils/media_tool.py)
  - 封装 `yt-dlp` 下载音频 / 视频。
  - 集成 `openai-whisper` 进行音频转文字（支持 GPU）。
  - 集成 OCR 工具，对图片进行文字识别（主要服务于小红书图文）。

- [processor/main.py](file:///f:/project/spider_TRAE/processor/main.py)
  - 遍历每日目录，执行三阶段处理：
    1. 视频提取音频（仅对小红书等需要转写的平台）。
    2. 音频转写（仅 B站 + 小红书）。
    3. 图片 OCR（仅小红书）。

- 各类 `test_*.py`
  - `test_media_tool.py` / `test_media_tool_async.py`：验证 MediaTool 集成与异步转写。
  - `test_whisper_env.py` / `test_whisper_standalone.py`：验证 Whisper 与 FFmpeg 环境。
  - `test_decoupled.py`：验证“采集”和“处理”解耦后的完整流。
  - 其它 `debug_*.py`：用于定位特定平台或依赖问题。

---

## 已实现功能清单

- 多平台收藏夹采集
  - [x] B站：收藏夹列表拉取、元数据提取、字幕获取。
  - [x] 抖音：收藏夹列表拉取、视频信息获取。
  - [x] 小红书：收藏夹笔记抓取（图文 + 视频），图片下载。
  - [x] 微信公众号：基于 URL 列表的正文抓取与 Markdown 转换。

- 多模态处理能力
  - [x] B站 & 小红书：音频转文字（Whisper，本地 GPU 优先）。
  - [x] 小红书：图片 OCR 识别并写入 Markdown。
  - [x] B站无字幕兜底：当官方字幕缺失时，自动下载音频，交由处理任务转写。

- 存储与结构
  - [x] 一帖一文件夹，统一的 Frontmatter + Markdown 模板。
  - [x] 资源按平台 / 日期分层存储，方便检索与 RAG 建库。

- 调度与去重
  - [x] 22:00 / 23:00 双任务调度（支持 Windows 任务计划程序）。
  - [x] Sync-Point 增量去重，保证跨日期不重复抓取旧内容。
  - [x] 本地文件存在性检查作为兜底去重机制。

- 健壮性与可维护性
  - [x] 详细日志（loguru），日志文件按天轮转。
  - [x] 针对 Cookie 失效、网络异常、反爬等场景的诊断提示。
  - [x] 独立的配置指南 README_CONFIG.md，降低重复配置成本。

---

## 主要参考项目与资料

本项目在设计与实现过程中参考了以下项目与文档（部分仅作为思路/架构参考）：

- 小红书相关
  - `local_knowledge_base/Spider_XHS`：小红书 Web 端 API 与签名逻辑（本项目直接复用）。
  - 行业讨论与项目：如 `xhshow`、`MediaCrawler` 等（参考其 JS 逆向与 Playwright 注入思路）。

- B站字幕与音频识别
  - `local_knowledge_base/B站字幕提取的调研.md`
  - `local_knowledge_base/B 站无字幕视频字幕识别方案深度解析（2025-2026 最新）.md`
  - `bilibili-api-python`：官方/第三方 B站 API 封装，提供字幕与收藏夹接口。
  - 业界工具：`BBDown`（C#）等，作为 API 行为与策略参考。

- OCR 与 ASR
  - `openai-whisper`：本地语音识别核心库。
  - `yt-dlp`：多站点音视频下载工具，作为音频源头。
  - EasyOCR / PaddleOCR：作为图像文字识别的方案参考。

- 通用架构与实践
  - 项目中 `project_doc/` 下的 SSRD / SRS / System_Architecture / testplan 文档。
  - 社区关于 Windows 任务计划程序、Conda 环境管理、日志与监控等最佳实践。

---

## 开发与调试建议

- 在修改爬虫逻辑前，优先查看：
  - [SSRD.md](file:///f:/project/spider_TRAE/project_doc/SSRD.md)：整体需求与行业方案调研。
  - [SRS.md](file:///f:/project/spider_TRAE/project_doc/SRS.md)：详细功能拆解与用例。
  - [System_Architecture.md](file:///f:/project/spider_TRAE/project_doc/System_Architecture.md)：架构分层与模块边界。

- 出现问题时：
  - 先查看 [history_log.md](file:///f:/project/spider_TRAE/project_doc/history_log.md)，确认是否为已知问题。
  - 再结合 `logs/spider_*.log` 定位具体平台与模块。

如需扩展到新的平台或引入新的处理流程，可以复用 `BaseCrawler` + `MediaTool` + `processor/main.py` 的现有模式进行迭代。
