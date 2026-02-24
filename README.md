[中文](README.md) | [English](README_EN.md)

# CyberMe

> **创造你的一个赛博分身，既拥有大模型的通用知识，又拥有你的所有信息（没错，是所有，不止是表层的知识比如你的银行卡密码doge，更是你的内在，只要你愿意分享），并且接入了各种工具，使得你只需要发出指令，cyberme就可以像你一样（或者说就是你）在赛博世界做任何事（没错，任何事，只要你愿意）**

![CyberMe Header Image](pictures/github_demo_picture.jpg)

**Long-Term目标和进度**：
- [ ] **第一阶段：信息同步（S-project）**---从现在开始，你获取的所有信息，AI也会同步获取一份(cyberme和你一起共同成长from now)
	- [x]  网络社交媒体的高质量数据同步：小红书，哔哩哔哩，微信公众号，抖音所有存在收藏夹里的信息（你认为有一定价值的信息，你关注的信息）
  - [ ] 信息源扩展：
- [ ] **第二阶段：记忆数据库**（[M-project](https://github.com/Ebwai/M-project)）【数据存储与检索】--- “AI终于开始理解你了”  (🚧 仍在建设中)
  - [x] 框架的选型和搭建，详情见[M-project](https://github.com/Ebwai/M-project)
  - [ ] 评估体系的构建：（换句话说，就是你的世界观、人生观、价值观，以及对某些具体场景的评价准则）
- [ ] **第三阶段：行为同步**（[A-project](https://github.com/Ebwai/A-project)）【工具&应用场景工作流】--- “AI的行事风格也慢慢像你了”  (🚧 仍在建设中)
  - [x] 社交行为：Bilibili，小红书，抖音，微信公众号的个性化风格分享
  - [x] 代替你去阅读随时发来的邮箱，处理并推送到你常用的社交平台上。
- [ ] **第四阶段：身体独立** (H-project)【计算本地化+物理世界**实践**与交互的能力】--- (🚧 仍在建设中，雏形可以参考我的本科毕设[Smart_Home_Agent](https://github.com/Ebwai/Smart_Home_Agent)（虽然极度粗糙，并且构想远远不止于此，成熟的时候会开源出来）)
  - [x] 前期先使用内网穿透的方案，以N8N为中转站去控制连接所有的系统和硬件。

❗❗❗目前项目中最简单部署且对效率提升最大的部分见[A-project](https://github.com/Ebwai/A-project) ，已实现对邮箱的自动阅读-->处理-->通知-->重要事项加入日历，效率提升显著，欢迎尝试。[EduEmail_WorkFlow](https://github.com/Ebwai/A-project/tree/main/EduEmail%20Workflow) ，同时另一个A-project的demo是将粗糙的原始文本-->AI针对不同社交平台就行风格化+补全元素-->自动分发到指定的社交平台[Social_Spread](https://github.com/Ebwai/A-project/tree/main/SocialSpread_Workflow)

**CyberMe存在的意义：**
- 背景：最近有很多很火的产品（比如豆包手机, OpenClawd, Kimi Agent集群），这个项目是不是和他们有重复呢？
- 回答：有相似之处，但是底层出发点不一样，上述的这些项目都是让你去把一个任务分配给别人去做。而Cyber Me的宗旨是创建一个你的数字本身,
- **项目的起源：在我们每次在app或者网页使用各种大语言模型的时候，总是发现AI给我们的回复，不是我们想要的。那么其实这里直接的原因，是因为你没有给他提供足够的信息，AI不了解你他自然就不能理解你的全部需求，为了解决这个这大体就两种思路。第一个是你让AI，去随时问你问题，从而可以更好的获取你的需求，跟你的需求对齐。第二个思路就是不断的去维护一个个人信息库。AI越了解你，它的输出越能符合你的心意。而这个理解，不仅仅是一个RAG知识库那么简单，因此为了实现AI更好用的目标。首先，需要AI成为自己，为了成为自己，CyberMe通过四个阶段的模块来不断的构建出一个你**



## S-project项目概览

本项目是一个面向个人知识管理与内容采集的 主要由2个需求组成：
1️⃣**多平台多模态高质量信息获取**  
2️⃣**多模态信息处理**
支持从以下平台的“收藏夹”或指定列表中自动拉取内容（包括文字，图片，视频【音频】等多模态信息）并将所有模态的信息转化为文字进行本地化存储（用文字表示所有模态的信息是为了后续的高性价比RAG建库和处理）
- Bilibili（B站）
- Douyin（抖音）
- Xiaohongshu（小红书）
- WeChat 公众号（通过 URL 列表）

系统每天分两阶段运行：
- **22:00 采集任务**：从各平台抓取当日新增收藏内容，保存为 Markdown + 媒体文件。
- **23:00 处理任务**：对已下载的多媒体进行离线处理（语音转文字、图片 OCR），并把结果写回 Markdown。

所有输出统一存放在 `F:\DataInput\YYYY-MM-DD\...` 目录，既方便 RAG 建库，又适合直接阅读。

**项目存在的意义**： 现在也有很多其他的方案去实现信息的获取，但是为什么需要本项目呢？
- 和利用agent去操作浏览器爬取信息相比（比如最近很火的OpenClawd和之前的豆包手机）：
	- 成本低：不需要部署浏览器，也不需要购买昂贵的API服务
	- 效率高：可以在短时间内获取大量信息
  - 隐私保护：所有信息都在本地存储，不会上传到任何服务器
  - 本项目和agent操作浏览器的原理上是一样的，只是没有AI参与决策的过程。
- 还有一些比较不太好说出来，反正用了就知道了，你关注的信息（本身）会大部分保留下来（以适合构建AI知识库的形式，并不是为了自媒体数据分析的用途）



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
.env文件需要你自己在项目文件夹创建，并且填写你自己的配置。详细教程请参考 [README_CONFIG.md](file:///f:/project/spider_TRAE/README_CONFIG.md)。

关键字段包括：
- B站：`BILI_SESSDATA`, `BILI_JCT`, `BILI_BUVID3`, `BILI_MEDIA_ID`
- 抖音：`DOUYIN_COOKIE`
- 小红书：`XHS_COOKIE`
- 微信：`WECHAT_URLS_FILE`（默认 `F:\DataInput\wechat_urls.txt`），`WECHAT_DB_PATH`（可选）

详细获取步骤（如何在浏览器中复制 Cookie / media_id），请参考 [README_CONFIG.md](file:///f:/project/spider_TRAE/README_CONFIG.md)。

多久需要去更换一次文件中的关键字段？（经过我一个月来的使用经验来看）
- B站：每 3 天更换一次（根据 B站 登录过期时间）
- 抖音：每 10 天更换一次（根据抖音 登录过期时间）
- 小红书：每 7 天更换一次（根据小红书 登录过期时间）
- 微信：根据需要添加或删除 URL（一般不常更换）

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

### 4. 历史收藏回填任务（backfill_favorites.py）

在日常 22:00 增量采集之外，你可以使用 [backfill_favorites.py](file:///f:/project/spider_TRAE/backfill_favorites.py) 对“历史收藏夹”进行补抓，适合以下场景：
- 项目刚部署，需要把过往收藏一次性补齐；
- 已经跑了一段时间的每日增量任务，但中间有一段时间未运行，需要补那段时间的收藏；
- 只想对某个平台做历史补抓，而其他平台维持现状。

#### 4.1 基本用法

在 Conda 环境 `yolov5` 中，进入项目根目录：

```bash
conda activate yolov5
cd f:\project\spider_TRAE
python backfill_favorites.py
```

- 默认会同时回填：`Bilibili, Xiaohongshu, Douyin, WeChat` 四个平台；
- 每个平台都有独立的“每次最多抓取条数”：
  - `--limit-bili`：单次 B站最多抓取多少条（默认 30）；
  - `--limit-xhs`：单次小红书最多抓取多少条（默认 30）；
  - `--limit-douyin`：单次抖音最多抓取多少条（默认 10）；
  - `--limit-wechat`：单次微信最多抓取多少条（默认 30）。

你也可以只回填部分平台，例如：

```bash
# 仅回填 B站与小红书（适合先补这两个平台）
python backfill_favorites.py --platforms Bilibili,Xiaohongshu

# 仅补抖音，且每次只补 5 条，方便观察效果

```

脚本运行日志会写入 `logs/backfill_YYYY-MM-DD.log`，方便你观察进度。

#### 4.2 各平台回填策略概览

- Bilibili  
  - 使用官方 Web 收藏夹接口（`/x/v3/fav/resource/list`）获取总数与分页数据；  
  - 每次从“最旧的一页”开始向前补抓，并在本次运行中按收藏时间从旧到新依次保存；  
  - 通过 `backfill_state.json` 记录已经处理过的 `bvid`、当前页码 `pn` 和页内索引 `idx`，支持多次分批运行。

- Xiaohongshu  
  - 基于 `local_knowledge_base/Spider_XHS` 提供的 API 读取收藏夹笔记列表；  
  - 会先尝试统计收藏总数（日志中显示“Xiaohongshu 收藏夹总数: N 条”），统计失败时会以“总数未知”模式运行；  
  - 按接口返回的光标（cursor）向更早的收藏推进，并记录 `cursor` 与已处理的 `note_id` 集合，支持多次分批补抓。

- Douyin  
  - 复用日常爬虫中的 `fetch_new_contents` 能力，获取当前收藏夹中的所有可见内容；  
  - 按 `publish_time` 从旧到新排序后，仅对尚未出现在回填状态中的内容执行保存；  
  - 由于抖音收藏接口本身不提供稳定的“总数”字段，所以日志中会显示“总数未知”。

- WeChat  
  - 从 `.env` 中配置的 `WECHAT_URLS_FILE` 读取文章 URL 列表；  
  - 仅对从未处理过的 URL 执行抓取与保存，已处理 URL 会在回填状态中标记。

所有平台的回填状态统一保存在 `SAVE_PATH` 根目录下的 `backfill_state.json`（默认路径：`F:\DataInput\backfill_state.json`）。

#### 4.3 与每日增量去重的关系与最佳实践

日常 22:00 采集任务通过两层机制保证增量去重：
- 每个平台内部的 Sync-Point（最后一次成功抓取的收藏 ID）；  
- 当日目录下基于“文件是否已存在”的兜底检查（见 [crawlers/base.py](file:///f:/project/spider_TRAE/crawlers/base.py#L46-L88)）。

回填脚本则采用“平台内已处理 ID 集合”的方式进行去重：
- B站 / 小红书 / 抖音：在 `backfill_state.json` 中维护 `processed_ids` 集合；  
- 微信：在 `backfill_state.json` 中维护 `processed_urls` 集合；  
- 同一平台的同一条收藏，只要已经出现在对应集合中，再次运行回填脚本时就会被跳过。

需要注意的是：**回填脚本不会复用日常任务的 Sync-Point**，两者的状态是彼此独立的。这意味着：
- 若同一个收藏已被“日常任务”抓取过，但尚未出现在回填脚本的 `processed_ids` 中，回填脚本会再次对其发起抓取请求；  
- 在磁盘层面，由于输出路径按“日期/平台/作者_标题”分层，相同帖子如果在不同日期被抓取，会分别出现在不同日期的目录下；同一天内不会生成多份相同帖子的 Markdown；  
- 在网络请求与平台风控层面，这是一次“重复抓取”，会消耗额外的请求额度。

为了尽可能减少与每日增量任务的重复抓取，推荐如下实践顺序：
- **首次部署项目**  
  1. 先完成 `.env` 配置与环境验证；  
  2. 暂时不要开启 Windows 计划任务；  
  3. 多次运行 `backfill_favorites.py`，适当调整 `--limit-*` 参数，直到日志中显示 B站 / 小红书等平台“累计已爬取收藏夹内容”已经基本覆盖历史收藏；  
  4. 再开启 22:00 / 23:00 的每日增量任务。

- **已经运行了一段时间的老项目**  
  - 若只是偶尔补一小段历史（例如你在某个平台新建了一个收藏夹，并希望把旧内容也补上），可以：  
    - 在当天任意时间手动运行 `backfill_favorites.py`，并把对应平台的 `--limit-*` 参数设置得较小（如 5~20 条）；  
    - 观察 `logs/backfill_*.log` 中的“累计已爬取”进度，分多次补完；  
    - 即使个别内容与日常任务有交集，也只是覆盖写入同一份 Markdown，不会在磁盘上产生大量重复文件。

- **避免严重重复抓取的几个不要**  
  - 不要随意删除 `backfill_state.json`，除非你明确希望“从头重新回填”；  
  - 不要在同一天频繁切换 `.env` 中的收藏夹 ID（例如频繁改动 `BILI_MEDIA_ID`），否则可能导致状态与实际收藏范围不一致；  
  - 不要在多台机器上同时对同一份收藏运行回填脚本而共享同一个输出目录，否则会互相覆盖。

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

---

## 10. 免责声明 (Disclaimer)

> **请在使用本项目前仔细阅读以下条款。使用本项目即表示您同意以下所有条款。**

1.  **仅供学习与研究**：本项目（CyberMe / S-project）仅作为个人技术研究与学习的实验性工具，旨在探索数据采集、多模态处理与知识管理技术。
2.  **合法合规使用**：
    *   用户在使用本项目时，必须严格遵守当地法律法规（包括但不限于《中华人民共和国网络安全法》、《中华人民共和国数据安全法》等）。
    *   用户应遵守目标网站的 Robots 协议及服务条款（Terms of Service）。
    *   **严禁**将本项目用于任何非法用途，包括但不限于：大规模爬取导致服务器拒绝服务（DDoS）、侵犯个人隐私、窃取商业机密、绕过付费墙获取受版权保护的内容等。
3.  **数据隐私与版权**：
    *   本项目仅供用户抓取**其拥有合法访问权**（如自己的收藏夹）的内容。
    *   抓取的数据仅限用户个人本地离线使用，**严禁**未经授权的公开传播、售卖或用于商业盈利。
    *   项目作者不持有任何抓取数据的版权，所有内容版权归原作者及原平台所有。
4.  **免责条款**：
    *   本项目按“原样”提供，不提供任何明示或暗示的保证。
    *   对于因使用本项目而导致的任何直接或间接损失（包括但不限于账号被封禁、IP 被拉黑、法律诉讼等），**项目作者不承担任何法律责任**。
    *   若目标网站要求停止相关抓取行为，请立即停止使用本项目。
5.  **关于移除**：若本项目内容无意侵犯了您的权益，请通过 GitHub Issue 联系作者，我们将及时处理。

---
