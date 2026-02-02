# 测试计划 (Test Plan)

## 1. 验证清单

### 1.1 单元测试
#### 小红书模块
- `get_my_user_id`: 验证 Cookie 是否有效并拉取 ID。
- `get_user_collect_note_info`: 能否获取收藏夹数据。
- `get_note_info`: 能否提取详情、正文、图片链接。
#### B站模块
- `get_video_favorite_list_content`: 能否获取列表。
- `_get_subtitle_text`:验证 cid 传参及字幕下载。
#### 抖音模块
- `handle_response`: 验证网络请求捕获。
- `parse_capture`: 验证数据字段映射。
#### 存储模块
- `save_content`: 验证 Markdown 格式与 YAML Frontmatter。
#### 媒体处理模块
- `extract_audio`: 验证能否从 MP4 提取音频。
- `OCRTool`: 验证 EasyOCR 模型加载及图片文字识别准确率。

### 1.2 集成测试
#### 全流程运行
- `python main.py --now`: 触发即时任务。
- 验证 `F:\DataInput\{Date}` 目录结构。
- 验证跨平台数据一致性。
- `python main.py --now [Platform]`: 验证单平台触发逻辑。

## 2. 自动化测试脚本
- 编写 `tests/test_crawlers.py` 使用 pytest 运行基础连接测试。

## 3. 验收标准
- [✓] 1.3 **Xiaohongshu 图片下载**：MD 文件中图片链接有效，Assets 文件夹内有本地文件。
- [✓] 1.4 **Bilibili 无字幕转写**：无字幕视频触发 Whisper，生成 Markdown 包含转写文本。
- [✓] 1.5 **小红书视频转译**：视频触发音频提取并转写，更新 Markdown。
- [✓] 1.6 **小红书图片 OCR**：识别图片文字，更新 Markdown。
- [✓] 生成的 Markdown 文件能被 Obsidian 或 VSCode 正确预览。
- [✓] 图片/视频链接在本地能正常打开（或已有缓存）。
- [✓] 操作日志 `history_log.md` 准确记录了运行结果。