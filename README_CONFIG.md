# 配置获取指南 (Configuration Guide)

本指南说明如何获取 `.env` 文件中所需的各项 Cookie 和 ID 配置。请使用 Chrome 或 Edge 浏览器按步骤操作。

.env文件内容示例（.env文件需要你自己在项目文件夹创建，并且填写你自己的配置）：?为你需要填写的内容
```
# Security
BILI_SESSDATA=?
BILI_JCT=?
BILI_BUVID3=?
BILI_MEDIA_ID=?

DOUYIN_COOKIE=?
# tt_webid, sessionid are crucial

XHS_COOKIE=?
# a1, web_session

WECHAT_URLS_FILE=？（例如：F:\DataInput\wechat_urls.txt）
# Optional: Path to local WeChat DB
WECHAT_DB_PATH=

# System
LOG_LEVEL=？（例如：INFO）
SAVE_PATH=？（例如：F:\DataInput）
CRON_TIME=？（例如：22:00）
```


## 1. Bilibili (B站)

我们需要获取 `SESSDATA`, `bili_jct`, `buvid3` 以及目标的 `media_id`。

### 获取 Cookie
1.  在浏览器登录 [Bilibili](https://www.bilibili.com)。
2.  按 `F12` 打开开发者工具，切换到 **Application** (应用程序) 标签页。
3.  在左侧栏找到 **Storage** -> **Cookies** -> `https://www.bilibili.com`。
4.  在右侧列表中找到以下 Key，并复制其 Value 到 `.env`：
    *   `SESSDATA` -> `BILI_SESSDATA`
    *   `bili_jct` -> `BILI_JCT`
    *   `buvid3` -> `BILI_BUVID3`

### 获取 Media ID (收藏夹 ID)
1.  进入您的个人空间 -> **收藏**。
2.  点击您想要抓取的目标收藏夹（例如“默认收藏夹”）。
3.  按 `F12` 打开开发者工具，切换到 **Network** (网络) 标签页。
4.  刷新页面。
5.  在过滤器中输入 `resource/list`。
6.  点击其中一个请求，查看 **Payload** (载荷) 或 **Query String Parameters**。
7.  找到 `media_id` 字段（通常是一串长数字，如 `12345678`），填入 `.env` 的 `BILI_MEDIA_ID`。
    *   *注意：URl 上的 `fid` 通常就是 `media_id`，但建议通过 Network 确认。*
    *   *如果不填，代码默认为空可能无法运行，必须填写。*

---

## 2. Douyin (抖音)

我们需要完整的 Cookie 字符串。

1.  在浏览器登录 [抖音网页版](https://www.douyin.com)。
2.  进入 **个人主页** -> **收藏** 标签。
3.  按 `F12` 打开开发者工具，切换到 **Network** (网络) 标签页，同时也选中 **Fetch/XHR** 过滤器。
4.  刷新页面，等待加载。
5.  找到任意一个发送给 `douyin.com` 的请求（例如 `favorite` 或 `user_info`）。
6.  点击该请求，在 **Headers** (标头) -> **Request Headers** (请求标头) 中找到 `Cookie`。
7.  复制 **整个 Cookie 字符串**（由于非常长，建议右键 -> Copy value），填入 `.env` 的 `DOUYIN_COOKIE`。
    *   *确保包含 `tt_webid` 和 `sessionid` 这两个关键字段。*

---

## 3. Xiaohongshu (小红书)

同样需要完整的 Cookie 字符串。

1.  在浏览器登录 [小红书网页版](https://www.xiaohongshu.com)。
2.  随意浏览或进入某个页面。
3.  按 `F12` 打开开发者工具，切换到 **Network** (网络) 标签页。
4.  刷新页面。
5.  找到任意 API 请求（如 `homefeed`, `user/me` 等）。
6.  在 **Request Headers** 中找到 `Cookie`。
7.  复制 **整个 Cookie 字符串**，填入 `.env` 的 `XHS_COOKIE`。
    *   *关键字段为 `web_session` 和 `a1`。*

---

## 4. WeChat (微信公众号)

微信公众号目前没有公开的 Web 收藏夹接口，我们使用“手动导出 URL”或“本地 DB”方案。

### 方案 A：URL 文件 (推荐，最稳定)
1.  在电脑上新建一个文本文件，路径为 `F:\DataInput\wechat_urls.txt` (与 `.env` 中 `WECHAT_URLS_FILE` 对应)。
2.  在手机微信或电脑微信中，打开您想要保存的公众号文章。
3.  复制文章链接（Copy Link）。
4.  将链接粘贴到 `wechat_urls.txt` 中，每行一个 URL。
    *   *爬虫将自动读取此文件并抓取内容。*

### 方案 B：本地数据库 (仅限高级用户)
1.  `.env` 中 `WECHAT_DB_PATH` 需指向 PC 版微信的 `Favorites.db` 或类似文件。
2.  由于涉及解密 (`SQLCipher`)，配置较为复杂，目前建议留空 (`WECHAT_DB_PATH=`)，优先使用方案 A。
