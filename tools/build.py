# -*- coding: utf-8 -*-
"""v5 功能升级：音效 + 连击特效 + 每日挑战。

在 v4 基础上增加：
  1. WebAudio 合成音效（零文件、零网络）——答对/答错/连击/失败
  2. 连击特效——连击数越高，屏幕边框光晕越强，并弹出连击数字
  3. 每日挑战——用日期做种子，全球同一天同一套题，成绩单独记录
"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
DATA = os.path.join(ROOT, "data")
ART = os.path.join(ASSETS, "art")

with io.open(os.path.join(ASSETS, "logo.b64"), "r", encoding="utf-8") as fh:
    LOGO = fh.read().strip()

with io.open(os.path.join(DATA, "chars.json"), "r", encoding="utf-8") as fh:
    RAW = json.load(fh)

# ---------------------------------------------------------------- 立绘
# assets/art/<角色>.webp 由 tools/fetch-art.mjs 抓取并压缩。
# 构建时内联成 data URI，保证 index.html 依然是单文件。
def load_art(name):
    for ext, mime in (("webp", "image/webp"), ("jpg", "image/jpeg"), ("png", "image/png")):
        p = os.path.join(ART, name + "." + ext)
        if os.path.exists(p):
            import base64
            with open(p, "rb") as fh:
                b64 = base64.b64encode(fh.read()).decode("ascii")
            return "data:" + mime + ";base64," + b64
    return None

ART_URIS = {}
if os.path.isdir(ART):
    for fn in os.listdir(ART):
        stem, _, ext = fn.rpartition(".")
        if ext.lower() in ("webp", "jpg", "jpeg", "png"):
            ART_URIS[stem] = load_art(stem)

HAIR = {
    "白墨": "绿色", "星绘": "白色", "奥黛丽": "金色", "玛德蕾娜": "棕色",
    "绯莎": "粉色", "汐": "橙色", "加拉蒂亚": "棕色",
    "蕾欧娜": "紫色", "米雪儿": "金色", "心夏": "棕色", "伊薇特": "黑色",
    "芙拉薇娅": "紫色", "千代": "黑色", "信": "白色", "艾卡": "红色",
    "明": "红色", "令": "黑色", "香奈美": "粉色", "诺诺": "白色", "玛拉": "绿色",
    "忧雾": "白色", "拉薇": "黑色", "梅瑞狄斯": "棕色", "珐格兰丝": "金色",
}
POP = {
    "白墨": 5, "星绘": 5, "奥黛丽": 3, "玛德蕾娜": 2, "绯莎": 1, "汐": 5,
    "加拉蒂亚": 3, "蕾欧娜": 4, "米雪儿": 3, "心夏": 4, "伊薇特": 2,
    "芙拉薇娅": 2, "千代": 4, "信": 3, "艾卡": 2, "明": 4, "令": 1,
    "香奈美": 5, "诺诺": 5, "玛拉": 1,
    "忧雾": 4, "拉薇": 4, "梅瑞狄斯": 3, "珐格兰丝": 3,
}
WEAPON_ORDER = ["自动步枪", "精确射手步枪", "微型冲锋枪", "霰弹枪", "机枪",
                "狙击步枪", "近战武器"]

CHARS = []
for c in RAW:
    name = c["name"]
    try:
        age = int(str(c.get("年龄", "")).strip())
    except ValueError:
        age = 0
    try:
        height = int(str(c.get("身高", "")).upper().replace("CM", ""))
    except ValueError:
        height = 0
    CHARS.append({
        "name": name,
        "faction": c.get("阵营", ""),
        "role": c.get("定位", ""),
        "gender": c.get("性别", ""),
        "age": age,
        "weapon": c.get("武器名称", ""),
        "wtype": c.get("武器类型", ""),
        "height": height,
        "birthday": c.get("生日", ""),
        "hair": HAIR.get(name, "未知"),
        "pop": POP.get(name, 3),
        "art": ART_URIS.get(name),
    })

FACTIONS = sorted({c["faction"] for c in CHARS})
WTYPES = [w for w in WEAPON_ORDER if any(c["wtype"] == w for c in CHARS)]
HAIRS = [("绿色", "🟢"), ("白色", "⚪"), ("金色", "🟡"), ("棕色", "🟤"),
         ("粉色", "🩷"), ("橙色", "🟠"), ("紫色", "🟣"), ("黑色", "⚫"), ("红色", "🔴")]

TITLES = [
    [0, "入门卡卫兵"], [3, "猫娘躯体化"], [7, "难道你真是奇点猫？"],
    [12, "我去卡奴！"], [18, "允许启动"], [999999, "永久月卡猫娘！"],
]


def js(v):
    return json.dumps(v, ensure_ascii=False).replace("</", "<\\/")


JS_CHARS = ",\n".join("    " + js(c) for c in CHARS)

HTML = u"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="theme-color" content="#0a0b0f" />
<meta name="description" content="真卡奴就玩弗一把 —— 面向卡拉彼丘玩家的角色猜谜小游戏，题目数据取自卡拉彼丘 WIKI" />
<title>真卡奴就玩弗一把</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Rajdhani:wght@600;700&display=swap" media="print" onload="this.media='all'" />
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Rajdhani:wght@600;700&display=swap" /></noscript>
<style>
  :root {
    --bg-0: #07080c;
    --bg-1: #0b0d13;
    --panel-a: #171c26;
    --panel-b: #11151d;
    --panel-2: #1a202b;
    --panel-3: #212837;

    --line: rgba(255, 255, 255, .07);
    --line-2: rgba(255, 255, 255, .12);

    --text: #eef2f8;
    --text-2: #aab6c6;
    --muted: #6f7d90;
    --dim: #4a5568;

    --accent: #ff6b35;
    --accent-2: #ffc93c;
    --accent-glow: rgba(255, 107, 53, .35);

    --ok: #34d99b;
    --bad: #ff5f6d;
    --info: #5aa9ff;

    --radius: 22px;
    --font-ui: "Inter", "HarmonyOS Sans SC", "PingFang SC", "Microsoft YaHei UI", "Microsoft YaHei", "Noto Sans SC", system-ui, sans-serif;
    --font-num: "Rajdhani", "SF Mono", ui-monospace, monospace;
  }

  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }

  body {
    background: var(--bg-0);
    color: var(--text);
    font-family: var(--font-ui);
    min-height: 100vh;
    display: flex; align-items: center; justify-content: center;
    padding: 16px;
    position: relative;
    overflow-x: hidden;
    -webkit-font-smoothing: antialiased;
  }
  body::before {
    content: "";
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background:
      radial-gradient(ellipse 60% 50% at 15% 0%, rgba(255,107,53,.10), transparent 60%),
      radial-gradient(ellipse 55% 45% at 85% 100%, rgba(90,169,255,.08), transparent 60%),
      radial-gradient(ellipse 40% 30% at 50% 50%, rgba(255,201,60,.03), transparent 70%);
  }
  body::after {
    content: "";
    position: fixed; inset: 0; z-index: 0; pointer-events: none; opacity: .35;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='120' height='120' filter='url(%23n)' opacity='.055'/%3E%3C/svg%3E");
  }

  /* ======================================================== 难度选择页 */
  #difficultyOverlay {
    position: fixed; inset: 0; z-index: 50;
    display: flex; align-items: center; justify-content: center;
    padding: 20px;
    background: rgba(7, 8, 12, .88);
    backdrop-filter: blur(14px) saturate(120%);
    -webkit-backdrop-filter: blur(14px) saturate(120%);
    animation: fadeIn .35s ease both;
    overflow-y: auto;
  }
  #difficultyOverlay.hidden { display: none; }
  @keyframes fadeIn { from { opacity: 0 } to { opacity: 1 } }
  @keyframes riseIn {
    from { opacity: 0; transform: translateY(18px) scale(.98); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
  }

  .difficulty-box {
    position: relative;
    max-width: 460px; width: 100%;
    padding: 2.2rem 2.2rem 1.9rem;
    text-align: center;
    border-radius: 0 40px 0 40px;
    background: linear-gradient(160deg, var(--panel-a), var(--panel-b));
    border: 1px solid var(--line);
    box-shadow:
      0 0 0 1px rgba(255,255,255,.03) inset,
      0 30px 70px -30px rgba(0,0,0,.9),
      0 0 90px -40px var(--accent-glow);
    animation: riseIn .45s cubic-bezier(.2,.8,.3,1) both;
    margin: auto;
  }
  .difficulty-box::before,
  .main-area::before,
  .panel::before {
    content: "";
    position: absolute; top: 0; left: 14%; right: 14%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.22), transparent);
    border-radius: 1px;
  }
  .difficulty-box::after {
    content: "";
    position: absolute; left: 0; top: 18%; bottom: 18%; width: 3px;
    border-radius: 3px;
    background: linear-gradient(180deg, transparent, var(--accent), transparent);
    box-shadow: 0 0 16px var(--accent-glow);
  }

  .crest {
    width: 76px; height: 76px; margin: 0 auto .9rem;
    border-radius: 50%; object-fit: cover; display: block;
    border: 2px solid rgba(255,255,255,.12);
    box-shadow:
      0 0 0 6px rgba(255,107,53,.08),
      0 0 34px -6px var(--accent-glow);
    animation: breathe 4s ease-in-out infinite;
  }
  @keyframes breathe {
    0%, 100% { box-shadow: 0 0 0 6px rgba(255,107,53,.08), 0 0 34px -6px var(--accent-glow); }
    50%      { box-shadow: 0 0 0 10px rgba(255,107,53,.05), 0 0 46px -4px var(--accent-glow); }
  }

  .difficulty-box h1 {
    margin: 0 0 .3rem;
    font-size: 1.45rem; font-weight: 600; letter-spacing: .02em;
    background: linear-gradient(100deg, #fff 10%, var(--accent-2) 55%, var(--accent) 95%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .difficulty-box > p {
    margin: 0 0 1.3rem; color: var(--muted); font-size: .82rem; letter-spacing: .04em;
  }

  .btn-group { display: grid; gap: 10px; }
  .diff-card {
    position: relative;
    display: grid; grid-template-columns: auto 1fr auto; align-items: center;
    gap: 12px; padding: .85rem 1.05rem;
    text-align: left; font-family: inherit; color: var(--text);
    background: linear-gradient(160deg, var(--panel-2), var(--panel-b));
    border: 1px solid var(--line);
    border-radius: 0 20px 0 20px;
    cursor: pointer;
    transition: transform .18s cubic-bezier(.2,.8,.3,1),
                border-color .18s, box-shadow .18s, background .18s;
  }
  .diff-card:hover {
    transform: translateY(-3px);
    border-color: rgba(255,107,53,.45);
    background: linear-gradient(160deg, #1f2734, #141922);
    box-shadow: 0 14px 32px -14px rgba(0,0,0,.9), 0 0 26px -12px var(--accent-glow);
  }
  .diff-card:active { transform: translateY(-1px) scale(.995); }
  .diff-card:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }
  .diff-card.daily { border-color: rgba(90,169,255,.28); }
  .diff-card.daily:hover { border-color: rgba(90,169,255,.6); box-shadow: 0 14px 32px -14px rgba(0,0,0,.9), 0 0 26px -12px rgba(90,169,255,.5); }
  .diff-card.daily .diff-icon { background: rgba(90,169,255,.1); border-color: rgba(90,169,255,.25); }

  .diff-icon {
    width: 36px; height: 36px; display: grid; place-items: center;
    border-radius: 11px; font-size: 1rem;
    background: rgba(255,107,53,.1);
    border: 1px solid rgba(255,107,53,.22);
  }
  .diff-main { min-width: 0; display: flex; flex-direction: column; gap: 2px; }
  .diff-title { font-size: .94rem; letter-spacing: .02em; }
  .diff-sub { font-size: .67rem; color: var(--muted); letter-spacing: .04em; }
  .diff-arrow { color: var(--dim); font-size: .9rem; transition: transform .18s, color .18s; }
  .diff-card:hover .diff-arrow { transform: translateX(4px); color: var(--accent); }
  .diff-card.daily:hover .diff-arrow { color: var(--info); }

  .diff-sep {
    display: flex; align-items: center; gap: .6rem;
    margin: .3rem 0 .1rem; color: var(--dim); font-size: .62rem;
    letter-spacing: .16em; text-transform: uppercase;
  }
  .diff-sep::before, .diff-sep::after {
    content: ""; flex: 1 1 auto; height: 1px; background: var(--line);
  }

  /* 设置行：音效开关 */
  .opt-row {
    display: flex; align-items: center; justify-content: space-between;
    margin-top: 1rem; padding-top: .85rem; border-top: 1px solid var(--line);
    font-size: .72rem; color: var(--muted);
  }
  .switch {
    position: relative; width: 40px; height: 22px; flex: 0 0 auto;
    background: var(--panel-3); border: 1px solid var(--line-2);
    border-radius: 999px; cursor: pointer; transition: background .18s, border-color .18s;
    padding: 0;
  }
  .switch::after {
    content: ""; position: absolute; top: 2px; left: 2px;
    width: 16px; height: 16px; border-radius: 50%;
    background: var(--muted); transition: transform .18s, background .18s;
  }
  .switch[aria-checked="true"] { background: rgba(52,217,155,.18); border-color: rgba(52,217,155,.45); }
  .switch[aria-checked="true"]::after { transform: translateX(18px); background: var(--ok); }

  /* ============================================================== 主界面 */
  .game-container {
    position: relative; z-index: 1;
    display: none; grid-template-columns: minmax(0,1fr) 292px; gap: 16px;
    width: 100%; max-width: 960px; align-items: start;
  }

  .main-area {
    position: relative;
    padding: 1.35rem 1.5rem;
    border-radius: 0 34px 0 34px;
    background: linear-gradient(160deg, var(--panel-a), var(--panel-b));
    border: 1px solid var(--line);
    box-shadow:
      0 0 0 1px rgba(255,255,255,.025) inset,
      0 24px 60px -30px rgba(0,0,0,.9);
    transition: box-shadow .4s ease, border-color .4s ease;
  }
  /* 连击时整块发光，连击越高越亮 */
  .main-area[data-combo="1"] { box-shadow: 0 0 0 1px rgba(52,217,155,.18), 0 0 30px -12px rgba(52,217,155,.5), 0 24px 60px -30px rgba(0,0,0,.9); }
  .main-area[data-combo="2"] { box-shadow: 0 0 0 1px rgba(52,217,155,.3), 0 0 44px -10px rgba(52,217,155,.65), 0 24px 60px -30px rgba(0,0,0,.9); }
  .main-area[data-combo="3"] { box-shadow: 0 0 0 1px rgba(255,201,60,.35), 0 0 56px -8px rgba(255,201,60,.7), 0 24px 60px -30px rgba(0,0,0,.9); }
  .main-area::after {
    content: "";
    position: absolute; left: 0; top: 16%; bottom: 16%; width: 3px;
    border-radius: 3px;
    background: linear-gradient(180deg, transparent, var(--accent), transparent);
    box-shadow: 0 0 14px var(--accent-glow);
  }
  .side-area { display: grid; gap: 12px; }

  /* ---------------------------------------------------------- 顶栏 */
  .topbar { display: flex; align-items: center; gap: 12px; margin-bottom: .9rem; }
  .back-btn {
    flex: 0 0 auto;
    width: 30px; height: 30px;
    display: grid; place-items: center;
    font-family: inherit; font-size: .95rem; line-height: 1;
    color: var(--muted);
    background: rgba(255,255,255,.03);
    border: 1px solid var(--line); border-radius: 9px;
    cursor: pointer;
    transition: color .15s, border-color .15s, background .15s, transform .15s;
  }
  .back-btn:hover {
    color: var(--accent); border-color: rgba(255,107,53,.45);
    background: rgba(255,107,53,.1); transform: translateX(-2px);
  }
  .back-btn:active { transform: translateX(-1px) scale(.95); }
  .back-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  .avatar-wrap { position: relative; flex: 0 0 auto; }
  .avatar-wrap::after {
    content: ""; position: absolute; inset: -3px; border-radius: 50%;
    background: conic-gradient(from 0deg, var(--accent), var(--accent-2), var(--accent));
    opacity: .5; z-index: -1; filter: blur(5px);
  }
  .logo {
    width: 44px; height: 44px; object-fit: cover; border-radius: 50%;
    border: 1.5px solid rgba(255,255,255,.14); display: block;
  }
  .topbar-mid { flex: 1 1 auto; min-width: 0; display: grid; gap: 3px; }
  .eyebrow {
    font-size: .62rem; color: var(--dim); letter-spacing: .18em;
    text-transform: uppercase;
  }
  .score-line { display: flex; align-items: center; gap: 9px; flex-wrap: wrap; }
  .score {
    font-family: var(--font-num); font-size: 1.15rem; font-weight: 700;
    color: var(--accent-2); letter-spacing: .02em;
    text-shadow: 0 0 18px rgba(255,201,60,.28);
  }
  .title-badge {
    font-size: .68rem; padding: .18rem .62rem; border-radius: 999px;
    background: rgba(255,201,60,.09);
    border: 1px solid rgba(255,201,60,.24);
    color: var(--accent-2); letter-spacing: .03em; white-space: nowrap;
  }
  .attempts { display: flex; gap: 3px; font-size: .92rem; flex: 0 0 auto; align-items: center; }
  .daily-tag {
    font-size: .64rem; letter-spacing: .1em; color: var(--info);
    padding: .18rem .6rem; border-radius: 999px;
    background: rgba(90,169,255,.1); border: 1px solid rgba(90,169,255,.25);
    white-space: nowrap;
  }
  .heart { animation: heartPop .3s cubic-bezier(.2,1.4,.4,1); display: inline-block; }
  @keyframes heartPop { from { transform: scale(.5); opacity: 0 } to { transform: scale(1); opacity: 1 } }

  /* ---------------------------------------------------------- 谜面 */
  .riddle {
    position: relative;
    padding: .8rem .95rem; margin-bottom: .55rem;
    border-radius: 0 16px 0 16px;
    background: linear-gradient(160deg, rgba(26,32,43,.9), rgba(17,21,29,.9));
    border: 1px solid var(--line);
    overflow: hidden;
  }
  .riddle::before {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 2px;
    background: linear-gradient(180deg, var(--accent), transparent);
  }
  .riddle-body { display: flex; gap: 12px; align-items: stretch; }
  .riddle-text { flex: 1 1 auto; min-width: 0; }

  /* 立绘：未答对时是剪影+问号，答对后揭晓 */
  .portrait {
    position: relative; flex: 0 0 auto;
    width: 96px; height: 132px;
    border-radius: 12px; overflow: hidden;
    border: 1px solid var(--line-2);
    background: radial-gradient(circle at 50% 30%, #202838, #0e1219 75%);
  }
  .portrait img {
    width: 100%; height: 100%; object-fit: cover; object-position: top center;
    display: block;
    filter: brightness(.25) saturate(0) blur(3px);
    opacity: .85;
    transform: scale(1.2);
    transition: filter .5s ease, opacity .5s ease, transform .5s ease;
  }
  .portrait.revealed img {
    filter: none; opacity: 1; transform: scale(1);
  }
  .portrait-veil {
    position: absolute; inset: 0;
    display: grid; place-items: center;
    font-family: var(--font-num); font-size: 2rem; font-weight: 700;
    color: rgba(255,201,60,.75);
    text-shadow: 0 0 20px rgba(255,201,60,.65);
    background: radial-gradient(circle at 50% 50%, rgba(10,12,16,.15), rgba(10,12,16,.55));
    transition: opacity .3s ease;
  }
  .portrait.revealed .portrait-veil { opacity: 0; }
  .portrait.revealed { border-color: rgba(52,217,155,.5); box-shadow: 0 0 22px -6px rgba(52,217,155,.65); }
  .riddle-head {
    display: flex; align-items: center; gap: .45rem;
    font-size: .66rem; color: var(--accent); letter-spacing: .13em;
    margin-bottom: .55rem; text-transform: uppercase;
  }
  .riddle-head .dot {
    width: 5px; height: 5px; border-radius: 50%; background: var(--accent);
    box-shadow: 0 0 8px var(--accent); flex: 0 0 auto;
    animation: pulse 2s ease-in-out infinite;
  }
  @keyframes pulse { 0%,100% { opacity: 1 } 50% { opacity: .35 } }

  .clue-list { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 18px; }
  .clue {
    display: flex; align-items: baseline; gap: .5rem;
    font-size: .8rem; min-width: 0;
  }
  .clue .k {
    color: var(--muted); flex: 0 0 auto; min-width: 3.6em;
    font-size: .73rem; letter-spacing: .04em; white-space: nowrap;
  }
  .clue .v {
    color: var(--text); font-weight: 400; overflow: hidden;
    text-overflow: ellipsis; white-space: nowrap;
  }
  .clue.wide { grid-column: 1 / -1; }
  .clue.wide .v { color: var(--accent-2); }

  .hint-area {
    font-size: .67rem; color: var(--dim); margin-bottom: .75rem;
    letter-spacing: .03em; display: flex; align-items: center; gap: .35rem;
  }

  /* 每日挑战进度条 */
  .daily-progress { margin: 0 0 .7rem; }
  .dp-top {
    display: flex; justify-content: space-between; align-items: baseline;
    font-size: .66rem; color: var(--muted); letter-spacing: .08em;
    margin-bottom: .3rem;
  }
  .dp-top #dailyStep {
    font-family: var(--font-num); color: var(--info); font-size: .78rem;
  }
  .dp-track {
    height: 4px; border-radius: 2px; overflow: hidden;
    background: rgba(255,255,255,.06);
  }
  .dp-bar {
    height: 100%; width: 0%;
    background: linear-gradient(90deg, var(--info), var(--accent-2));
    border-radius: 2px;
    transition: width .4s cubic-bezier(.2,.8,.3,1);
    box-shadow: 0 0 10px rgba(90,169,255,.5);
  }

  /* ---------------------------------------------------------- 作答 */
  .input-group { display: grid; gap: 8px; margin-bottom: .85rem; }
  .field { display: grid; gap: 5px; }
  .field-label {
    display: flex; align-items: center; gap: .4rem;
    font-size: .65rem; color: var(--muted); letter-spacing: .09em;
    text-transform: uppercase;
  }
  .field-label .req {
    font-size: .53rem; color: var(--accent); letter-spacing: .07em;
    padding: .06rem .3rem; border-radius: 3px;
    background: rgba(255,107,53,.1); border: 1px solid rgba(255,107,53,.2);
  }

  .choice-row { display: flex; flex-wrap: wrap; gap: 5px; }
  .choice {
    position: relative;
    padding: .3rem .74rem;
    font-family: inherit; font-size: .77rem; line-height: 1.35;
    color: var(--text-2);
    background: linear-gradient(160deg, var(--panel-2), var(--panel-b));
    border: 1px solid var(--line);
    border-radius: 999px;
    cursor: pointer;
    white-space: nowrap;
    transition: transform .13s, border-color .13s, color .13s, background .13s, box-shadow .13s;
  }
  .choice-row.hair-row {
    display: grid;
    grid-template-columns: repeat(9, minmax(0, 1fr));
    gap: 4px;
  }
  .choice-row.hair-row .choice {
    padding: .3rem .2rem; text-align: center; font-size: .71rem;
  }
  .choice-row.pop-row {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 4px;
  }
  .choice-row.pop-row .choice { padding: .3rem .2rem; text-align: center; }
  .choice:hover:not(:disabled) {
    transform: translateY(-1px);
    border-color: rgba(255,107,53,.4);
    color: var(--text);
  }
  .choice:active:not(:disabled) { transform: translateY(0) scale(.97); }
  .choice:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  .choice[aria-pressed="true"] {
    color: #0a0c10; font-weight: 500;
    background: linear-gradient(160deg, var(--accent-2), var(--accent));
    border-color: transparent;
    box-shadow: 0 4px 16px -4px var(--accent-glow);
  }
  .choice.correct {
    color: var(--ok); border-color: rgba(52,217,155,.55);
    background: rgba(52,217,155,.12);
    box-shadow: 0 0 14px -4px rgba(52,217,155,.4);
  }
  .choice.wrong {
    color: var(--bad); border-color: rgba(255,95,109,.5);
    background: rgba(255,95,109,.1);
  }
  .choice:disabled { opacity: .45; cursor: not-allowed; }

  /* 角色名：输入联想 */
  .combo { position: relative; }
  .combo input {
    width: 100%;
    padding: .44rem .8rem;
    font-family: inherit; font-size: .83rem; color: var(--text);
    background: linear-gradient(160deg, var(--panel-2), var(--panel-b));
    border: 1px solid var(--line); border-radius: 9px;
    outline: none; transition: border-color .14s, box-shadow .14s, color .14s;
  }
  .combo input::placeholder { color: var(--dim); }
  .combo input:hover:not(:disabled) { border-color: rgba(255,107,53,.35); }
  .combo input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(255,107,53,.12);
  }
  .combo input.picked { color: var(--accent-2); border-color: rgba(255,201,60,.45); }
  .combo input.correct { color: var(--ok); border-color: rgba(52,217,155,.55); }
  .combo input.wrong { color: var(--bad); border-color: rgba(255,95,109,.5); }
  .combo input:disabled { opacity: .5; cursor: not-allowed; }

  .combo-list {
    position: absolute; left: 0; right: 0; top: calc(100% + 4px); z-index: 20;
    max-height: 208px; overflow-y: auto;
    padding: 4px;
    background: #171c26;
    border: 1px solid var(--line-2); border-radius: 10px;
    box-shadow: 0 16px 40px -12px rgba(0,0,0,.9);
    display: none;
  }
  .combo-list.open { display: block; animation: riseIn .14s ease both; }
  .combo-list::-webkit-scrollbar { width: 4px; }
  .combo-list::-webkit-scrollbar-thumb { background: var(--line-2); border-radius: 2px; }
  .combo-item {
    display: flex; align-items: center; justify-content: space-between;
    gap: .5rem; padding: .34rem .55rem;
    font-size: .79rem; color: var(--text-2);
    border-radius: 6px; cursor: pointer;
  }
  .combo-item .meta { font-size: .65rem; color: var(--dim); }
  .combo-item:hover,
  .combo-item.active {
    background: rgba(255,107,53,.14);
    color: var(--accent);
  }
  .combo-item.active .meta { color: rgba(255,107,53,.7); }
  .combo-empty {
    padding: .5rem .55rem; font-size: .73rem; color: var(--dim); text-align: center;
  }

  /* ---------------------------------------------------------- 提交 */
  .submit-row { display: flex; gap: 8px; }
  #submitBtn {
    position: relative; flex: 1 1 auto; overflow: hidden;
    padding: .6rem 1.2rem;
    font-family: var(--font-num); font-weight: 700; font-size: .84rem;
    letter-spacing: .14em; color: #0a0c10;
    background: linear-gradient(100deg, var(--accent-2), var(--accent));
    border: none; border-radius: 0 20px 0 20px; cursor: pointer;
    transition: transform .15s, box-shadow .15s, filter .15s;
    box-shadow: 0 8px 24px -10px var(--accent-glow);
  }
  #submitBtn::after {
    content: ""; position: absolute; inset: 0;
    background: linear-gradient(100deg, transparent 30%, rgba(255,255,255,.35) 50%, transparent 70%);
    transform: translateX(-120%);
    transition: transform .55s ease;
  }
  #submitBtn:hover:not(:disabled) { transform: translateY(-2px); filter: brightness(1.06); }
  #submitBtn:hover:not(:disabled)::after { transform: translateX(120%); }
  #submitBtn:active:not(:disabled) { transform: translateY(0); }
  #submitBtn:disabled { opacity: .35; cursor: not-allowed; box-shadow: none; }

  .restart-btn {
    flex: 0 0 auto; padding: .6rem 1rem;
    font-family: inherit; font-size: .75rem; color: var(--muted);
    background: transparent; border: 1px solid var(--line);
    border-radius: 0 20px 0 20px; cursor: pointer;
    transition: color .15s, border-color .15s, transform .15s;
  }
  .restart-btn:hover {
    color: var(--accent); border-color: rgba(255,107,53,.4); transform: translateY(-1px);
  }

  .feedback-area { display: grid; gap: 3px; margin-top: .65rem; }
  .feedback-item {
    display: flex; justify-content: space-between; align-items: center;
    padding: .26rem .62rem; font-size: .73rem;
    background: rgba(26,32,43,.7);
    border: 1px solid var(--line); border-radius: 7px;
    animation: riseIn .22s ease both;
  }
  .feedback-item .label { color: var(--muted); letter-spacing: .05em; }
  .feedback-item .correct { color: var(--ok); }
  .feedback-item .wrong { color: var(--bad); }

  .message {
    margin-top: .6rem; font-size: .79rem; line-height: 1.55;
    min-height: 1.35em; letter-spacing: .01em;
  }
  .message.success { color: var(--ok); }
  .message.fail    { color: var(--bad); }
  .message.info    { color: var(--info); }

  /* ---------------------------------------------------------- 侧栏 */
  .panel {
    position: relative;
    padding: .85rem .95rem;
    border-radius: 0 22px 0 22px;
    background: linear-gradient(160deg, var(--panel-a), var(--panel-b));
    border: 1px solid var(--line);
    box-shadow: 0 18px 44px -26px rgba(0,0,0,.9);
  }
  .panel h3 {
    margin: 0 0 .6rem;
    font-size: .7rem; font-weight: 500; color: var(--text-2);
    letter-spacing: .11em; text-transform: uppercase;
  }

  .ref-box summary {
    display: flex; align-items: center; justify-content: space-between;
    gap: .5rem;
    list-style: none; cursor: pointer;
    font-size: .7rem; color: var(--text-2);
    letter-spacing: .1em; text-transform: uppercase;
    transition: color .15s;
  }
  .ref-box summary:hover { color: var(--accent); }
  .ref-box summary::-webkit-details-marker { display: none; }
  .ref-box .ref-count {
    font-size: .62rem; color: var(--dim); letter-spacing: .02em;
    text-transform: none; margin-left: auto; margin-right: .4rem;
  }
  .ref-box .ref-count b { color: var(--accent-2); font-family: var(--font-num); }
  .ref-box summary .chev {
    color: var(--muted); font-size: .6rem;
    transition: transform .22s cubic-bezier(.2,.8,.3,1);
  }
  .ref-box[open] summary .chev { transform: rotate(90deg); }
  .ref-grid {
    display: grid; gap: 1px; margin-top: .65rem;
    max-height: 296px; overflow-y: auto; padding-right: .25rem;
    animation: riseIn .22s ease both;
  }
  .ref-grid::-webkit-scrollbar { width: 4px; }
  .ref-grid::-webkit-scrollbar-thumb {
    background: var(--line-2); border-radius: 2px;
  }
  .ref-grid .item {
    display: flex; gap: .4rem; align-items: baseline;
    padding: .16rem .1rem; font-size: .68rem; color: var(--muted);
    border-bottom: 1px solid rgba(255,255,255,.035);
  }
  .ref-grid .item .highlight { color: var(--text-2); flex: 0 0 auto; }

  .rank-item {
    display: flex; justify-content: space-between; align-items: baseline;
    padding: .24rem 0; font-size: .74rem; color: var(--muted);
  }
  .rank-item .value {
    font-family: var(--font-num); color: var(--accent-2); font-size: .84rem;
  }
  #clearRankBtn {
    width: 100%; margin-top: .6rem; padding: .38rem .8rem;
    font-family: inherit; font-size: .67rem; color: #d45a6a;
    background: rgba(212,90,106,.08);
    border: 1px solid rgba(212,90,106,.22);
    border-radius: 0 16px 0 16px; cursor: pointer;
    transition: background .15s, border-color .15s;
  }
  #clearRankBtn:hover { background: rgba(212,90,106,.18); border-color: rgba(212,90,106,.4); }

  /* ============================================================ 连击特效 */
  .combo-burst {
    position: fixed; left: 50%; top: 22%; z-index: 60;
    transform: translate(-50%, -50%);
    pointer-events: none; text-align: center;
    animation: burst 1s cubic-bezier(.2,.8,.3,1) forwards;
  }
  .combo-burst .num {
    font-family: var(--font-num); font-weight: 700;
    font-size: 4.2rem; line-height: 1;
    background: linear-gradient(160deg, var(--accent-2), var(--accent));
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 24px rgba(255,201,60,.55));
  }
  .combo-burst .lbl {
    font-size: .8rem; letter-spacing: .3em; color: var(--accent-2);
    margin-top: .2rem; text-transform: uppercase;
  }
  @keyframes burst {
    0%   { opacity: 0; transform: translate(-50%, -50%) scale(.5); }
    25%  { opacity: 1; transform: translate(-50%, -50%) scale(1.12); }
    60%  { opacity: 1; transform: translate(-50%, -50%) scale(1); }
    100% { opacity: 0; transform: translate(-50%, -90%) scale(1); }
  }

  /* 屏幕边缘光晕，随连击增强 */
  .combo-vignette {
    position: fixed; inset: 0; z-index: 55; pointer-events: none;
    opacity: 0; transition: opacity .35s ease;
    box-shadow: inset 0 0 90px -20px rgba(52,217,155,.7);
  }
  .combo-vignette.on { opacity: 1; }
  .combo-vignette.hot { box-shadow: inset 0 0 110px -14px rgba(255,201,60,.85); }

  .watermark {
    position: fixed; bottom: 8px; left: 50%; transform: translateX(-50%);
    z-index: 1; pointer-events: none;
    font-size: .6rem; color: rgba(111,125,144,.42); letter-spacing: .12em;
    white-space: nowrap;
  }

  /* ---------------------------------------------------------- 响应式 */
  @media (max-width: 860px) {
    .game-container { grid-template-columns: 1fr; }
    .main-area { padding: 1.15rem 1.05rem; border-radius: 0 26px 0 26px; }
    .side-area { grid-template-columns: 1fr 1fr; }
    .clue-list { grid-template-columns: 1fr; }
  }
  @media (max-width: 560px) {
    body { padding: 10px; }
    .side-area { grid-template-columns: 1fr; }
    .logo { width: 38px; height: 38px; }
    .choice { font-size: .73rem; padding: .26rem .6rem; }
    .choice-row.hair-row { display: flex; flex-wrap: wrap; gap: 5px; }
    .choice-row.hair-row .choice { padding: .28rem .6rem; font-size: .73rem; }
    .difficulty-box { padding: 1.7rem 1.2rem 1.4rem; }
    .crest { width: 62px; height: 62px; }
    .combo-burst .num { font-size: 3rem; }
  }

  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: .01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: .01ms !important;
    }
  }
</style>
</head>
<body>

<div class="combo-vignette" id="comboVignette"></div>

<div id="difficultyOverlay">
  <div class="difficulty-box">
    <img class="crest" src="data:image/jpeg;base64,__LOGO__" alt="" />
    <h1>真卡奴就玩弗一把</h1>
    <p>看线索，猜超弦体</p>
    <div class="btn-group">
      <button class="diff-card daily" id="diffDaily">
        <span class="diff-icon">📅</span>
        <span class="diff-main">
          <span class="diff-title">每日挑战</span>
          <span class="diff-sub" id="dailySub">今天的 10 题 · 全服同一套</span>
        </span>
        <span class="diff-arrow">→</span>
      </button>
      <div class="diff-sep">或 自由练习</div>
      <button class="diff-card" id="diff3">
        <span class="diff-icon">🔥</span>
        <span class="diff-main">
          <span class="diff-title">3 条命</span>
          <span class="diff-sub">卡奴专用 · 四词条 · 硬核</span>
        </span>
        <span class="diff-arrow">→</span>
      </button>
      <button class="diff-card" id="diff4">
        <span class="diff-icon">🌱</span>
        <span class="diff-main">
          <span class="diff-title">4 条命</span>
          <span class="diff-sub">mmr 适用 · 三词条 · 轻松</span>
        </span>
        <span class="diff-arrow">→</span>
      </button>
    </div>
    <div class="opt-row">
      <span>🔊 音效</span>
      <button class="switch" id="soundToggle" role="switch" aria-checked="true" aria-label="音效开关"></button>
    </div>
  </div>
</div>

<div class="game-container" id="gameContainer">
  <div class="main-area" id="mainArea">

    <div class="topbar">
      <button class="back-btn" id="backBtn" title="返回首页" aria-label="返回首页">←</button>
      <div class="avatar-wrap">
        <img class="logo" src="data:image/jpeg;base64,__LOGO__" alt="" />
      </div>
      <div class="topbar-mid">
        <div class="eyebrow" id="modeLabel">🐾 卡奴请输入</div>
        <div class="score-line">
          <span class="score">🏆 <span id="currentScore">0</span></span>
          <span class="title-badge" id="titleBadge">杂鱼猫娘</span>
        </div>
      </div>
      <div class="attempts" id="attemptsDisplay"></div>
    </div>

    <div class="riddle">
      <div class="riddle-body">
        <div class="riddle-text">
          <div class="riddle-head"><span class="dot"></span>谜面 · 这位超弦体是</div>
          <div class="clue-list" id="riddleText"></div>
        </div>
        <div class="portrait" id="portrait">
          <img id="portraitImg" alt="" />
          <div class="portrait-veil" id="portraitVeil">?</div>
        </div>
      </div>
    </div>

    <div class="daily-progress" id="dailyProgress" style="display:none">
      <div class="dp-top"><span>📅 今日进度</span><span id="dailyStep">1 / 10</span></div>
      <div class="dp-track"><div class="dp-bar" id="dailyBar"></div></div>
    </div>

    <div class="hint-area" id="hintArea"></div>
    <div class="input-group" id="inputGroup"></div>

    <div class="submit-row">
      <button id="submitBtn">确认</button>
      <button class="restart-btn" id="restartBtn">🔄 重开</button>
    </div>

    <div class="feedback-area" id="feedbackArea"></div>
    <div class="message" id="message"></div>
  </div>

  <div class="side-area">
    <details class="panel ref-box" id="refBox" open>
      <summary>📋 候选参考 <span class="ref-count">本轮池子 <b id="refCount">0</b> 人</span><span class="chev">▶</span></summary>
      <div class="ref-grid" id="refGrid"></div>
    </details>

    <div class="panel rank-box">
      <h3 id="rankTitle">🏅 排行榜</h3>
      <div class="rank-item"><span>🥇 最好</span><span class="value" id="bestScore">-</span></div>
      <div class="rank-item"><span>🔥 最长连击</span><span class="value" id="bestStreak">-</span></div>
      <div class="rank-item"><span>🔄 最近1</span><span class="value" id="recent1">-</span></div>
      <div class="rank-item"><span>🔄 最近2</span><span class="value" id="recent2">-</span></div>
      <div class="rank-item"><span>🔄 最近3</span><span class="value" id="recent3">-</span></div>
      <button id="clearRankBtn">🗑️ 重置排行榜</button>
    </div>
  </div>
</div>

<div class="watermark">// 少爷专属 · 点击作答 · 数据取自卡拉彼丘 WIKI</div>

<script>
(function () {
  "use strict";

  var CHARS = [
__CHARS__
  ];

  var FACTIONS = __FACTIONS__;
  var WTYPES = __WTYPES__;
  var HAIRS = __HAIRS__;
  var TITLES = __TITLES__;

  var RANK_KEY = "karabiyo_rank_v8";
  var DAILY_KEY = "karabiyo_daily_v1";
  var SOUND_KEY = "karabiyo_sound_v1";
  var DAILY_SIZE = 10;

  var current = null;
  var score = 0, streak = 0, bestStreak = 0;
  var maxAttempts = 4, attempts = 4;
  var answered = false, gameOver = false, isHard = false;
  var picked = {};
  var difficultyChosen = false;
  var lastIndex = -1;
  var isDaily = false;
  var dailyQueue = [];
  var dailyIndex = 0;

  var $ = function (id) { return document.getElementById(id); };
  var mainArea = $("mainArea"), currentScoreEl = $("currentScore"), titleBadge = $("titleBadge");
  var attemptsDisplay = $("attemptsDisplay"), riddleText = $("riddleText"), hintArea = $("hintArea");
  var inputGroup = $("inputGroup"), submitBtn = $("submitBtn"), restartBtn = $("restartBtn");
  var feedbackArea = $("feedbackArea"), message = $("message"), refGrid = $("refGrid");
  var bestScoreEl = $("bestScore"), bestStreakEl = $("bestStreak");
  var recent1 = $("recent1"), recent2 = $("recent2"), recent3 = $("recent3");
  var vignette = $("comboVignette");

  function randInt(a, b) { return Math.floor(Math.random() * (b - a + 1)) + a; }
  function titleFor(s) {
    for (var i = 0; i < TITLES.length; i++) if (s <= TITLES[i][0]) return TITLES[i][1];
    return TITLES[TITLES.length - 1][1];
  }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  /* ============================================================ 音效
     全部用 WebAudio 现场合成，不加载任何音频文件。 */
  var actx = null;
  var soundOn = true;
  try { soundOn = localStorage.getItem(SOUND_KEY) !== "0"; } catch (e) {}

  function audio() {
    if (!soundOn) return null;
    if (!actx) {
      var C = window.AudioContext || window.webkitAudioContext;
      if (!C) return null;
      try { actx = new C(); } catch (e) { return null; }
    }
    if (actx.state === "suspended") { try { actx.resume(); } catch (e) {} }
    return actx;
  }

  function tone(freq, start, dur, type, gain, slideTo) {
    var a = audio();
    if (!a) return;
    var t0 = a.currentTime + (start || 0);
    var osc = a.createOscillator();
    var g = a.createGain();
    osc.type = type || "sine";
    osc.frequency.setValueAtTime(freq, t0);
    if (slideTo) osc.frequency.exponentialRampToValueAtTime(slideTo, t0 + dur);
    g.gain.setValueAtTime(0.0001, t0);
    g.gain.exponentialRampToValueAtTime(gain || 0.12, t0 + 0.012);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
    osc.connect(g); g.connect(a.destination);
    osc.start(t0); osc.stop(t0 + dur + 0.02);
  }

  var SFX = {
    correct: function (combo) {
      // 连击越高，音阶越高
      var base = 523.25 * Math.pow(1.0595, Math.min(combo || 0, 12) * 2);
      tone(base, 0, .12, "triangle", .10);
      tone(base * 1.5, .07, .16, "triangle", .08);
    },
    wrong: function () {
      tone(196, 0, .16, "sawtooth", .07, 130);
    },
    combo: function (n) {
      tone(783.99, 0, .09, "square", .06);
      tone(1046.5, .06, .12, "square", .05);
      if (n >= 5) tone(1318.5, .13, .18, "triangle", .06);
    },
    over: function () {
      tone(392, 0, .18, "sine", .09, 261);
      tone(261, .14, .3, "sine", .08, 174);
    },
    daily: function () {
      tone(659.25, 0, .1, "triangle", .07);
      tone(880, .08, .14, "triangle", .07);
    }
  };

  /* ============================================================ 连击特效 */
  function showComboBurst(n) {
    var el = document.createElement("div");
    el.className = "combo-burst";
    el.innerHTML = '<div class="num">' + n + '</div><div class="lbl">COMBO</div>';
    document.body.appendChild(el);
    setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, 1000);
  }

  function updateComboVisual() {
    // 0 = 无, 1 = 3~4 连, 2 = 5~7 连, 3 = 8+ 连
    var lvl = streak >= 8 ? 3 : streak >= 5 ? 2 : streak >= 3 ? 1 : 0;
    mainArea.setAttribute("data-combo", String(lvl));
    if (lvl === 0) {
      vignette.classList.remove("on", "hot");
    } else {
      vignette.classList.add("on");
      vignette.classList.toggle("hot", lvl >= 3);
    }
  }

  /* ============================================================ 排行榜 */
  function rankKey() { return isDaily ? DAILY_KEY : RANK_KEY; }

  function readRank() {
    try {
      var d = JSON.parse(localStorage.getItem(rankKey()) || "null") || {};
      return {
        best: Number(d.best) || 0,
        bestStreak: Number(d.bestStreak) || 0,
        recent: Array.isArray(d.recent) ? d.recent.slice(0, 3) : [],
        day: d.day || null
      };
    } catch (e) { return { best: 0, bestStreak: 0, recent: [], day: null }; }
  }
  function writeRank(d) { try { localStorage.setItem(rankKey(), JSON.stringify(d)); } catch (e) {} }
  function renderRank() {
    var d = readRank();
    bestScoreEl.textContent = d.best > 0 ? d.best : "-";
    bestStreakEl.textContent = d.bestStreak > 0 ? d.bestStreak : "-";
    var s = [recent1, recent2, recent3];
    for (var i = 0; i < 3; i++) s[i].textContent = d.recent[i] !== undefined ? d.recent[i] : "-";
    $("rankTitle").textContent = isDaily ? "📅 今日战绩" : "🏅 排行榜";
  }
  function commitScore() {
    var d = readRank();
    if (isDaily) {
      var today = todayStr();
      if (d.day !== today) { d.best = 0; d.bestStreak = 0; d.recent = []; d.day = today; }
    }
    if (score > d.best) d.best = score;
    if (bestStreak > d.bestStreak) d.bestStreak = bestStreak;
    d.recent.unshift(score);
    if (d.recent.length > 3) d.recent = d.recent.slice(0, 3);
    writeRank(d); renderRank();
  }

  /* ============================================================ 每日挑战 */
  function todayStr() {
    var d = new Date();
    var m = String(d.getMonth() + 1);
    var day = String(d.getDate());
    if (m.length < 2) m = "0" + m;
    if (day.length < 2) day = "0" + day;
    return d.getFullYear() + "-" + m + "-" + day;
  }

  // 日期 -> 稳定随机种子（同一个日期，全世界算出同一套题）
  function hashStr(s) {
    var h = 2166136261;
    for (var i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = (h * 16777619) >>> 0;
    }
    return h >>> 0;
  }

  function mulberry32(seed) {
    return function () {
      seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
      var t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function buildDailyQueue() {
    var rnd = mulberry32(hashStr(todayStr()));
    var idx = [];
    for (var i = 0; i < CHARS.length; i++) idx.push(i);
    // Fisher-Yates，用种子随机
    for (var j = idx.length - 1; j > 0; j--) {
      var k = Math.floor(rnd() * (j + 1));
      var t = idx[j]; idx[j] = idx[k]; idx[k] = t;
    }
    dailyQueue = idx.slice(0, Math.min(DAILY_SIZE, CHARS.length));
    dailyIndex = 0;
  }

  /* ------------------------------------------------------------ 渲染 */
  function renderAttempts() {
    // 每日挑战没有「命」的概念（答错继续下一题），这里改为显示进度
    if (isDaily) {
      attemptsDisplay.innerHTML = '<span class="daily-tag">📅 每日</span>';
      return;
    }
    var h = "";
    for (var i = 0; i < maxAttempts; i++) {
      h += '<span class="heart" style="animation-delay:' + (i * 40) + 'ms">' +
           (i < attempts ? "❤️" : "🖤") + "</span>";
    }
    attemptsDisplay.innerHTML = h;
  }
  function renderTitle() { titleBadge.textContent = titleFor(score); }

  /* 参考信息：给「候选池」，不是答案表。
     严格按线索匹配会把候选压到 1 人，那就等于直接给答案了。
     所以这里只按「定位」筛，再随机混入干扰项，保证答案在池子里但要自己排。 */
  function renderRef() {
    if (!current) { refGrid.innerHTML = ""; return; }
    var pool = CHARS.filter(function (c) { return c.role === current.role; });
    var others = CHARS.filter(function (c) { return c.role !== current.role; });
    for (var i = others.length - 1; i > 0; i--) {
      var j = randInt(0, i);
      var t = others[i]; others[i] = others[j]; others[j] = t;
    }
    var need = Math.max(0, 6 - pool.length);
    pool = pool.concat(others.slice(0, need));
    for (var k = pool.length - 1; k > 0; k--) {
      var m = randInt(0, k);
      var tmp = pool[k]; pool[k] = pool[m]; pool[m] = tmp;
    }
    var h = "";
    for (var n = 0; n < pool.length; n++) {
      var c = pool[n];
      h += '<div class="item"><span class="highlight">' + esc(c.name) + "</span> · " +
           esc(c.faction) + " · " + esc(c.role) + " · " + esc(c.wtype) + "</div>";
    }
    refGrid.innerHTML = h;
    $("refCount").textContent = pool.length;
  }

  /* 谜面线索必须与「要答的字段」完全不重叠，否则等于白送分。
       轻松（4命）要答：阵营 / 角色名 / 发色  -> 线索可用 定位、性别、武器类型
       硬核（3命）要答：阵营 / 角色名 / 发色 / 武器类型 / 人气
                       -> 线索绝不能再给武器类型，只给 定位、性别 */
  function renderRiddle() {
    var c = current;
    var clues = [["定位", c.role], ["性别", c.gender]];
    if (!isHard) clues.push(["武器类型", c.wtype]);
    var h = "";
    for (var i = 0; i < clues.length; i++) {
      h += '<div class="clue"><span class="k">' + clues[i][0] +
           '</span><span class="v">' + esc(clues[i][1]) + "</span></div>";
    }
    riddleText.innerHTML = h;
    hintArea.innerHTML = isHard
      ? '<span class="hint-text">🔍 宗教度提示：角色人气也是衡量的标准！</span>'
      : '<span class="hint-text">💡 经典模式，无额外提示</span>';
    renderPortrait(false);
  }

  /* 立绘：默认是模糊剪影 + 问号，答对后揭晓原图 */
  function renderPortrait(reveal) {
    var box = $("portrait"), img = $("portraitImg"), veil = $("portraitVeil");
    if (!box || !img) return;
    var src = current && current.art ? current.art : null;
    if (!src) {
      box.style.display = "none";
      return;
    }
    box.style.display = "";
    img.src = src;
    img.alt = reveal ? (current ? current.name : "") : "";
    if (reveal) {
      box.classList.add("revealed");
      if (veil) veil.textContent = "";
    } else {
      box.classList.remove("revealed");
      if (veil) veil.textContent = "?";
    }
  }

  function makePills(label, field, options, render, required) {
    var wrap = document.createElement("div");
    wrap.className = "field";
    var lab = document.createElement("span");
    lab.className = "field-label";
    lab.innerHTML = label + (required ? ' <span class="req">必答</span>' : "");
    wrap.appendChild(lab);
    var row = document.createElement("div");
    row.className = "choice-row";
    if (field === "hair") row.className += " hair-row";
    if (field === "pop") row.className += " pop-row";
    options.forEach(function (opt) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "choice";
      b.textContent = render ? render(opt) : String(opt);
      b.dataset.field = field;
      b.dataset.value = String(opt);
      b.setAttribute("aria-pressed", "false");
      b.addEventListener("click", function () { pick(field, String(opt), b); });
      row.appendChild(b);
    });
    wrap.appendChild(row);
    return wrap;
  }

  function makeNameInput() {
    var wrap = document.createElement("div");
    wrap.className = "field";
    var lab = document.createElement("span");
    lab.className = "field-label";
    lab.innerHTML = '角色名 <span class="req">必答</span>';
    wrap.appendChild(lab);

    var combo = document.createElement("div");
    combo.className = "combo";

    var input = document.createElement("input");
    input.type = "text";
    input.id = "nameInput";
    input.autocomplete = "off";
    input.spellcheck = false;
    input.placeholder = "输入角色名，如「白」";
    combo.appendChild(input);

    var list = document.createElement("div");
    list.className = "combo-list";
    list.id = "nameList";
    combo.appendChild(list);

    var active = -1;
    var shown = [];

    function renderList(q) {
      var key = q.trim().toLowerCase();
      shown = CHARS.filter(function (c) {
        if (!key) return true;
        return c.name.toLowerCase().indexOf(key) >= 0;
      });
      if (shown.length === 0) {
        list.innerHTML = '<div class="combo-empty">没有匹配的角色</div>';
      } else {
        var h = "";
        for (var i = 0; i < shown.length; i++) {
          var c = shown[i];
          h += '<div class="combo-item' + (i === active ? " active" : "") +
               '" data-name="' + esc(c.name) + '">' +
               '<span>' + esc(c.name) + "</span>" +
               '<span class="meta">' + esc(c.faction) + " · " + esc(c.role) + "</span></div>";
        }
        list.innerHTML = h;
      }
      list.classList.add("open");
    }

    function closeList() {
      list.classList.remove("open");
      active = -1;
    }

    function commit(name) {
      if (answered || gameOver) return;
      input.value = name;
      picked.name = name;
      input.classList.add("picked");
      message.textContent = "";
      message.className = "message";
      closeList();
    }

    function move(delta) {
      if (!list.classList.contains("open")) { renderList(input.value); return; }
      if (shown.length === 0) return;
      active = (active + delta + shown.length) % shown.length;
      var items = list.querySelectorAll(".combo-item");
      for (var i = 0; i < items.length; i++) items[i].classList.toggle("active", i === active);
      if (items[active] && items[active].scrollIntoView) {
        items[active].scrollIntoView({ block: "nearest" });
      }
    }

    input.addEventListener("input", function () {
      if (answered || gameOver) return;
      delete picked.name;
      input.classList.remove("picked", "correct", "wrong");
      active = -1;
      renderList(input.value);
      message.textContent = "";
      message.className = "message";
    });

    input.addEventListener("focus", function () {
      if (answered || gameOver) return;
      renderList(input.value);
    });

    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); e.stopPropagation(); move(1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); e.stopPropagation(); move(-1); }
      else if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); closeList(); }
      else if (e.key === "Enter") {
        // 必须阻止冒泡：document 上还有一个 Enter=提交 的全局快捷键，
        // 否则「确认选名」会连带触发一次提交，白扣一条命。
        e.preventDefault();
        e.stopPropagation();
        if (active >= 0 && shown[active]) commit(shown[active].name);
        else if (shown.length >= 1) commit(shown[0].name);
        else handleSubmit();
      }
    });

    list.addEventListener("mousedown", function (e) {
      var item = e.target.closest(".combo-item");
      if (!item) return;
      e.preventDefault();
      commit(item.dataset.name);
    });

    input.addEventListener("blur", function () {
      var v = input.value.trim();
      for (var i = 0; i < CHARS.length; i++) {
        if (CHARS[i].name === v) { picked.name = v; input.classList.add("picked"); break; }
      }
      setTimeout(closeList, 120);
    });

    wrap.appendChild(combo);
    return wrap;
  }

  function buildInputs() {
    inputGroup.innerHTML = "";
    picked = {};
    inputGroup.appendChild(makePills("阵营", "faction", FACTIONS, null, true));
    inputGroup.appendChild(makeNameInput());
    inputGroup.appendChild(makePills("发色", "hair", HAIRS.map(function (p) { return p[0]; }),
      function (v) {
        for (var i = 0; i < HAIRS.length; i++) if (HAIRS[i][0] === v) return HAIRS[i][1] + " " + v;
        return v;
      }, true));
    if (isHard) {
      inputGroup.appendChild(makePills("武器类型", "wtype", WTYPES, null, true));
      inputGroup.appendChild(makePills("人气星级", "pop", [1, 2, 3, 4, 5],
        function (v) { return v + "★"; }, true));
    }
  }

  function pick(field, value, btn) {
    if (answered || gameOver) return;
    picked[field] = value;
    var sibs = btn.parentNode.querySelectorAll(".choice");
    for (var i = 0; i < sibs.length; i++) sibs[i].setAttribute("aria-pressed", "false");
    btn.setAttribute("aria-pressed", "true");
    message.textContent = "";
    message.className = "message";
  }

  function disableChoices() {
    var all = inputGroup.querySelectorAll(".choice, .combo input");
    for (var i = 0; i < all.length; i++) all[i].disabled = true;
    submitBtn.disabled = true;
  }

  function markAnswers(c) {
    var want = { faction: c.faction, hair: c.hair };
    if (isHard) { want.wtype = c.wtype; want.pop = String(c.pop); }
    var all = inputGroup.querySelectorAll(".choice");
    for (var i = 0; i < all.length; i++) {
      var b = all[i];
      if (want[b.dataset.field] === b.dataset.value) b.classList.add("correct");
      else if (b.getAttribute("aria-pressed") === "true") b.classList.add("wrong");
    }
    var nameEl = $("nameInput");
    if (nameEl) {
      nameEl.classList.remove("picked");
      if (picked.name === c.name) nameEl.classList.add("correct");
      else nameEl.classList.add("wrong");
    }
  }

  /* ------------------------------------------------------------- 回合 */
  function nextChar() {
    if (isDaily) {
      if (dailyIndex >= dailyQueue.length) return null;
      return CHARS[dailyQueue[dailyIndex++]];
    }
    var idx;
    do { idx = randInt(0, CHARS.length - 1); } while (CHARS.length > 1 && idx === lastIndex);
    lastIndex = idx;
    return CHARS[idx];
  }

  function loadNewRound() {
    if (gameOver) return;
    var next = nextChar();
    if (!next) { finishDaily(); return; }
    current = next;

    attempts = maxAttempts;
    answered = false;
    picked = {};

    renderAttempts();
    renderRiddle();
    renderRef();
    buildInputs();
    feedbackArea.innerHTML = "";
    message.textContent = "";
    message.className = "message";
    submitBtn.disabled = false;
    updateComboVisual();
    updateProgress();
  }

  /* 每日挑战的进度条：第几题 / 共几题 */
  function updateProgress() {
    var el = $("dailyProgress");
    if (!el) return;
    if (!isDaily) { el.style.display = "none"; return; }
    el.style.display = "flex";
    var done = Math.min(dailyIndex - (current ? 1 : 0), DAILY_SIZE);
    $("dailyStep").textContent = Math.max(1, dailyIndex) + " / " + DAILY_SIZE;
    $("dailyBar").style.width = Math.round((Math.max(0, dailyIndex - 1) / DAILY_SIZE) * 100) + "%";
  }

  function finishDaily() {
    gameOver = true;
    disableChoices();
    var wrong = DAILY_SIZE - score;
    var rank = score >= 10 ? "满分卡奴！" :
               score >= 8 ? "相当可以" :
               score >= 5 ? "还行吧" : "再练练喵";
    message.textContent = "📅 今日挑战完成！" + score + " / " + DAILY_SIZE +
      " 题（错 " + wrong + " 题）· " + rank + " · 明天再来～";
    message.className = "message success";
    commitScore();
    SFX.daily();
  }

  function handleSubmit() {
    if (answered || gameOver || !current) return;

    var need = isHard ? ["faction", "name", "hair", "wtype", "pop"] : ["faction", "name", "hair"];
    for (var i = 0; i < need.length; i++) {
      if (picked[need[i]] === undefined) {
        message.textContent = "🐾 还有词条没选喵～";
        message.className = "message info";
        return;
      }
    }

    var checks = [
      ["阵营", picked.faction, picked.faction === current.faction],
      ["角色", picked.name, picked.name === current.name],
      ["发色", picked.hair, picked.hair === current.hair]
    ];
    if (isHard) {
      checks.push(["武器", picked.wtype, picked.wtype === current.wtype]);
      checks.push(["人气", picked.pop + "★", picked.pop === String(current.pop)]);
    }

    var allOk = true;
    for (var j = 0; j < checks.length; j++) if (!checks[j][2]) allOk = false;

    var html = "";
    for (var k = 0; k < checks.length; k++) {
      html += '<div class="feedback-item"><span class="label">' + checks[k][0] + "</span>" +
              '<span class="' + (checks[k][2] ? "correct" : "wrong") + '">' +
              (checks[k][2] ? "✅" : "❌") + " " + esc(checks[k][1]) + "</span></div>";
    }
    feedbackArea.innerHTML = html;

    if (allOk) {
      answered = true;
      score++; streak++;
      if (streak > bestStreak) bestStreak = streak;
      currentScoreEl.textContent = score;
      renderTitle();
      markAnswers(current);
      disableChoices();
      renderPortrait(true);
      SFX.correct(streak);
      if (streak >= 3) {
        showComboBurst(streak);
        SFX.combo(streak);
      }
      updateComboVisual();
      var combo = streak >= 3 ? " 🔥" + streak + " 连击！" : "";
      message.textContent = "🎉 完美！就是 " + current.name + " 喵～" + combo;
      message.className = "message success";
      setTimeout(loadNewRound, 1000);
    } else {
      attempts--;
      streak = 0;
      renderAttempts();
      markAnswers(current);
      renderPortrait(true);   // 答错也揭晓，反正答案马上就说出来了
      SFX.wrong();
      updateComboVisual();

      if (isDaily) {
        // 每日挑战：答错不结束，直接进下一题，最后统一结算
        answered = true;
        disableChoices();
        message.textContent = "❌ 错了喵～正确答案：" + current.name + " · " + current.faction +
          " · " + current.hair;
        message.className = "message fail";
        setTimeout(function () {
          if (!gameOver) { loadNewRound(); }
        }, 1400);
      } else if (attempts <= 0) {
        answered = true;
        gameOver = true;
        disableChoices();
        message.textContent = "❌ 机会用尽。正确答案：" + current.name + " · " + current.faction +
          " · " + current.hair + " · " + current.wtype + " 喵～";
        message.className = "message fail";
        commitScore();
        SFX.over();
      } else {
        message.textContent = "❌ 卡奴再试试！还剩 " + attempts + " 次机会";
        message.className = "message fail";
        setTimeout(function () {
          if (!answered && !gameOver) {
            buildInputs();
            submitBtn.disabled = false;
          }
        }, 950);
      }
    }
  }

  function restartGame() {
    if (score > 0) commitScore();
    score = 0; streak = 0; bestStreak = 0;
    gameOver = false; answered = false;
    if (isDaily) { buildDailyQueue(); }
    currentScoreEl.textContent = "0";
    renderTitle();
    feedbackArea.innerHTML = "";
    message.textContent = isDaily ? "📅 重新开始今日挑战喵～" : "🔄 新挑战开始喵～";
    message.className = "message info";
    loadNewRound();
  }

  function startGame(mode) {
    if (difficultyChosen) return;
    difficultyChosen = true;

    isDaily = (mode === "daily");
    isHard = (mode === 3);
    // 每日挑战是「10 题连答」，没有命的概念；maxAttempts 只用于普通模式
    maxAttempts = isDaily ? 1 : mode;
    score = 0; streak = 0; bestStreak = 0;
    gameOver = false; answered = false;

    if (isDaily) { buildDailyQueue(); }

    $("modeLabel").textContent = isDaily ? "📅 每日挑战 · " + todayStr() : "🐾 卡奴请输入";
    currentScoreEl.textContent = "0";
    renderTitle();
    $("difficultyOverlay").classList.add("hidden");
    $("gameContainer").style.display = "grid";
    renderRank();
    loadNewRound();
  }

  $("diff3").addEventListener("click", function () { startGame(3); });
  $("diff4").addEventListener("click", function () { startGame(4); });
  $("diffDaily").addEventListener("click", function () { startGame("daily"); });
  submitBtn.addEventListener("click", handleSubmit);
  restartBtn.addEventListener("click", restartGame);

  /* 返回首页：结束当前局（有分就记），回到难度选择页 */
  $("backBtn").addEventListener("click", function () {
    if (score > 0) commitScore();
    gameOver = true;
    answered = false;
    difficultyChosen = false;
    $("gameContainer").style.display = "none";
    $("difficultyOverlay").classList.remove("hidden");
    var ov = $("difficultyOverlay");
    ov.style.animation = "none";
    void ov.offsetWidth;
    ov.style.animation = "";
    vignette.classList.remove("on", "hot");
  });
  $("clearRankBtn").addEventListener("click", function () {
    if (confirm("确定要清空所有排行榜记录吗喵？")) {
      try { localStorage.removeItem(rankKey()); } catch (e) {}
      renderRank();
      message.textContent = "🗑️ 排行榜已重置喵～";
      message.className = "message info";
    }
  });

  /* 音效开关 */
  var soundBtn = $("soundToggle");
  soundBtn.setAttribute("aria-checked", soundOn ? "true" : "false");
  soundBtn.addEventListener("click", function () {
    soundOn = !soundOn;
    soundBtn.setAttribute("aria-checked", soundOn ? "true" : "false");
    try { localStorage.setItem(SOUND_KEY, soundOn ? "1" : "0"); } catch (e) {}
    if (soundOn) SFX.correct(0);
  });

  document.addEventListener("keydown", function (e) {
    if (!difficultyChosen) return;
    // 输入框内的 Enter 由输入框自己处理（已 stopPropagation）
    if (e.target && e.target.id === "nameInput") return;
    if (e.key === "Enter" && !gameOver) { e.preventDefault(); handleSubmit(); }
  });

  // 每日挑战副标题显示今天日期
  (function () {
    var el = $("dailySub");
    if (el) el.textContent = todayStr() + " · " + DAILY_SIZE + " 题 · 全服同一套";
  })();

  renderRank();
})();
</script>
</body>
</html>
"""

html = (HTML
        .replace("__LOGO__", LOGO)
        .replace("__CHARS__", JS_CHARS)
        .replace("__FACTIONS__", js(FACTIONS))
        .replace("__WTYPES__", js(WTYPES))
        .replace("__HAIRS__", js(HAIRS))
        .replace("__TITLES__", js(TITLES)))

out = os.path.join(ROOT, "index.html")
with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(html)

print("written:", out)
print("bytes:", len(html.encode("utf-8")))
print("chars:", len(CHARS), "factions:", len(FACTIONS), "wtypes:", len(WTYPES))
