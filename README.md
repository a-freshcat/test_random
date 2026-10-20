# 真卡奴就玩弗一把 🐾

面向**卡拉彼丘（Strinova）**玩家的角色猜谜小游戏。看线索，猜超弦体。

**在线游玩** → https://a-freshcat.github.io/test_random/

---

## 这是什么

一道题给你两条线索——**定位**和**性别**——你要猜出这是哪位超弦体，并答出她的阵营、发色（硬核模式还要答武器类型和人气）。

谜面**刻意不给**角色名、阵营、发色，否则就不叫猜了。

线索只用来**收窄范围**，具体是谁得靠你对角色的印象。数据算过：定位+性别把 24 人分成 8 组，最大一组 7 人——够缩小范围，但猜不出来。

## 三种模式

| 模式 | 生命 | 要答的词条 | 线索 | 说明 |
|---|---|---|---|---|
| **每日挑战** | 1 | 阵营 · 角色名 · 发色 | 定位 · 性别 · 武器类型 | 每天 10 题，全服同一套 |
| **4 条命** | 4 | 阵营 · 角色名 · 发色 | 定位 · 性别 · 武器类型 | mmr 适用，轻松 |
| **3 条命** | 3 | 阵营 · 角色名 · 发色 · 武器类型 · 人气 | 定位 · 性别 | 卡奴专用，硬核 |

命少但要求多，这就是「卡奴」和「mmr」的区别。

> **线索绝不与答案重叠。** 硬核模式要答武器类型，所以谜面就不给武器类型——否则等于白送一分。这条有自动化测试盯着。

## 玩法

1. 选模式
2. 读谜面线索，参考右侧「候选参考」缩小范围
3. 阵营/发色**点按钮**，角色名**打字联想**（↑↓ 选择，Enter 确认）
4. 答错扣一条命，扣光就结束，成绩自动记录
5. 连续答对 3 次以上触发 🔥 连击特效，越高越亮
6. 左上角 `←` 随时返回模式选择

## 功能

- **角色立绘** —— 24 个角色的初始立绘全部来自 WIKI。题目进行中是模糊剪影 + 问号，答完揭晓
- **每日挑战** —— 用日期做随机种子，同一天所有人拿到同一套题。成绩单独存，隔天自动重置
- **连击系统** —— 3 连屏幕泛绿光，5 连加强，8 连变金光，并弹出连击数字
- **音效** —— 答对/答错/连击/失败都有音，用 WebAudio 现场合成，不加载任何音频文件。首页可一键关闭
- **候选参考** —— 只给一个候选池（至少 6 人），不是答案表

## 数据来源

角色数据全部来自 **[卡拉彼丘 WIKI](https://wiki.biligame.com/klbq/)**，通过 MediaWiki API 抓取 `{{超弦体}}` 模板：

- 阵营、定位、性别、年龄、身高、生日、武器名称与类型 —— **24 个角色，字段全齐**
- 发色和人气星级 WIKI 没有结构化字段，为手工维护
- **立绘** —— 抓 `初始立绘` 原图（1080×1920 PNG），压到 340px WebP/JPEG

抓取脚本：`tools/fetch-wiki.mjs`（带限流重试，站点会返回 HTTP 567）

立绘流程分四步：

```bash
node tools/fetch-art.mjs data/art-list.json      # 找到每个角色的立绘文件名
node tools/resolve-art.mjs ... data/art-urls.json # 文件名 -> 下载 URL
node tools/download-art.mjs ... art-raw/          # 下载原图
python tools/compress-art.py                      # 压缩到 assets/art/
```

> 有 7 个角色（汐、蕾欧娜、千代、诺诺、玛拉、忧雾、珐格兰丝）WIKI 上没有「初始立绘」，用其默认皮肤立绘代替。

## 技术说明

**单文件，零依赖，零构建。** `index.html` 拖到浏览器就能跑，也能直接部署到任何静态托管。

- 纯原生 JS，无框架、无 npm
- 无网络请求（除了可选的 Google Fonts）
- 音效由 WebAudio 合成，不占体积
- **立绘内联成 data URI**：24 张压到 0.73 MB，整个页面 1.06 MB
- 数据存 `localStorage`：`karabiyo_rank_v8`（练习）、`karabiyo_daily_v1`（每日）
- 字体异步加载 —— `<link rel=stylesheet>` 在断网时会阻塞整个页面 2.8 秒

## 本地开发

```bash
# 直接打开
start index.html

# 或者起个静态服务器
python -m http.server 8000
```

重新抓取角色数据：

```bash
node tools/fetch-wiki.mjs data/chars.json
```

改完数据重新生成页面：

```bash
python tools/build.py
```

## 文件结构

```
index.html                游戏本体（自包含单文件，含立绘）
data/chars.json           24 个角色的 WIKI 数据
data/art-manifest.json    立绘清单（尺寸、字节数）
data/art-urls.json        立绘原始下载地址
assets/art/               24 张压缩后的立绘
assets/logo.b64           内嵌 logo
tools/fetch-wiki.mjs      角色数据抓取
tools/fetch-art.mjs       查找立绘文件名
tools/resolve-art.mjs     文件名 -> URL
tools/download-art.mjs    下载原图
tools/compress-art.py     压缩并生成 manifest
tools/build.py            从 chars.json + assets/art 生成 index.html
```

## 已知限制

- **24 个角色**，WIKI 上还有其它超弦体未收录，可按同样方式补充
- 人气星级是主观的，不是官方数据
- 发色按立绘目测，可能有争议
- 7 个角色没有官方「初始立绘」，用的是默认皮肤立绘
- 排行榜是本地的，换设备就没了
- 页面 1.06 MB，首次加载稍慢（立绘全部内联）

## 贡献

想加角色的话：

1. 在 `data/chars.json` 里加一条（再补 `tools/build.py` 里的 `HAIR` / `POP`）
2. 把立绘放进 `assets/art/<角色名>.webp`
3. 跑 `python tools/build.py`

---

*本项目纯属娱乐，与官方无关。角色版权归库洛游戏所有。*
