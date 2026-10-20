# -*- coding: utf-8 -*-
"""Generate index.html for 真卡奴就玩弗一把 — visual redesign (v4).

v3 fixed the crowding; v4 is about looks. What changed visually:
  * a real colour system: layered panels, hairline gradients, warm accent glow
  * the difficulty screen became a hero: big glowing crest, gradient title,
    two inviting option cards instead of two flat bars
  * cards get a top highlight, soft outer shadow and a subtle grain texture
  * every interactive element has hover / active / focus feedback
  * the avatar has a glow ring; hearts animate on change
  * typography has a proper scale and fallback stack (the web font often
    does not arrive, so the fallback has to look good on its own)
"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
DATA = os.path.join(ROOT, "data")

with io.open(os.path.join(ASSETS, "logo.b64"), "r", encoding="utf-8") as fh:
    LOGO = fh.read().strip()

with io.open(os.path.join(DATA, "chars.json"), "r", encoding="utf-8") as fh:
    RAW = json.load(fh)

HAIR = {
    "白墨": "绿色", "星绘": "白色", "奥黛丽": "金色", "玛德蕾娜": "棕色",
    "绯莎": "粉色", "汐": "橙色", "加拉蒂亚": "棕色",
    "蕾欧娜": "紫色", "米雪儿": "金色", "心夏": "棕色", "伊薇特": "黑色",
    "芙拉薇娅": "紫色", "千代": "黑色", "信": "白色", "艾卡": "红色",
    "明": "红色", "令": "黑色", "香奈美": "粉色", "诺诺": "白色", "玛拉": "绿色",
}
POP = {
    "白墨": 5, "星绘": 5, "奥黛丽": 3, "玛德蕾娜": 2, "绯莎": 1, "汐": 5,
    "加拉蒂亚": 3, "蕾欧娜": 4, "米雪儿": 3, "心夏": 4, "伊薇特": 2,
    "芙拉薇娅": 2, "千代": 4, "信": 3, "艾卡": 2, "明": 4, "令": 1,
    "香奈美": 5, "诺诺": 5, "玛拉": 1,
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
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=ZCOOL+KuaiLe&display=swap" media="print" onload="this.media='all'" />
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=ZCOOL+KuaiLe&display=swap" /></noscript>
<style>
  :root {
    /* 底色：比纯黑更有层次的冷调深蓝 */
    --bg-0: #07080c;
    --bg-1: #0b0d13;
    /* 面板：渐变而非纯色，才有体积感 */
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
    --font-ui: "ZCOOL KuaiLe", "PingFang SC", "Microsoft YaHei", "Noto Sans SC", system-ui, sans-serif;
    --font-num: "Orbitron", "SF Mono", ui-monospace, monospace;
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
  /* 背景光晕 + 极细噪点，避免大面积死黑 */
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
    padding: 2.6rem 2.2rem 2.1rem;
    text-align: center;
    border-radius: 0 40px 0 40px;
    background: linear-gradient(160deg, var(--panel-a), var(--panel-b));
    border: 1px solid var(--line);
    box-shadow:
      0 0 0 1px rgba(255,255,255,.03) inset,
      0 30px 70px -30px rgba(0,0,0,.9),
      0 0 90px -40px var(--accent-glow);
    animation: riseIn .45s cubic-bezier(.2,.8,.3,1) both;
  }
  /* 顶部高光细线 */
  .difficulty-box::before,
  .main-area::before,
  .panel::before {
    content: "";
    position: absolute; top: 0; left: 14%; right: 14%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.22), transparent);
    border-radius: 1px;
  }
  /* 左侧橙色光条 */
  .difficulty-box::after {
    content: "";
    position: absolute; left: 0; top: 18%; bottom: 18%; width: 3px;
    border-radius: 3px;
    background: linear-gradient(180deg, transparent, var(--accent), transparent);
    box-shadow: 0 0 16px var(--accent-glow);
  }

  .crest {
    width: 84px; height: 84px; margin: 0 auto 1.1rem;
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
    font-size: 1.5rem; font-weight: 400; letter-spacing: .04em;
    background: linear-gradient(100deg, #fff 10%, var(--accent-2) 55%, var(--accent) 95%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .difficulty-box > p {
    margin: 0 0 1.6rem; color: var(--muted); font-size: .84rem; letter-spacing: .06em;
  }

  .btn-group { display: grid; gap: 11px; }
  .diff-card {
    position: relative;
    display: grid; grid-template-columns: auto 1fr auto; align-items: center;
    gap: 13px; padding: .95rem 1.1rem;
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

  .diff-icon {
    width: 38px; height: 38px; display: grid; place-items: center;
    border-radius: 12px; font-size: 1.05rem;
    background: rgba(255,107,53,.1);
    border: 1px solid rgba(255,107,53,.22);
  }
  .diff-main { min-width: 0; display: flex; flex-direction: column; gap: 2px; }
  .diff-title { font-size: .96rem; letter-spacing: .03em; }
  .diff-sub {
    font-size: .68rem; color: var(--muted); letter-spacing: .05em;
  }
  .diff-arrow {
    color: var(--dim); font-size: .9rem; transition: transform .18s, color .18s;
  }
  .diff-card:hover .diff-arrow { transform: translateX(4px); color: var(--accent); }

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
  }
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
    font-size: .62rem; color: var(--dim); letter-spacing: .2em;
    text-transform: uppercase;
  }
  .score-line { display: flex; align-items: center; gap: 9px; flex-wrap: wrap; }
  .score {
    font-family: var(--font-num); font-size: 1.15rem; font-weight: 900;
    color: var(--accent-2); letter-spacing: .02em;
    text-shadow: 0 0 18px rgba(255,201,60,.28);
  }
  .title-badge {
    font-size: .68rem; padding: .18rem .62rem; border-radius: 999px;
    background: rgba(255,201,60,.09);
    border: 1px solid rgba(255,201,60,.24);
    color: var(--accent-2); letter-spacing: .04em; white-space: nowrap;
  }
  .attempts { display: flex; gap: 3px; font-size: .92rem; flex: 0 0 auto; }
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
  .riddle-head {
    display: flex; align-items: center; gap: .45rem;
    font-size: .68rem; color: var(--accent); letter-spacing: .14em;
    margin-bottom: .55rem; text-transform: uppercase;
  }
  .riddle-head .dot {
    width: 5px; height: 5px; border-radius: 50%; background: var(--accent);
    box-shadow: 0 0 8px var(--accent); flex: 0 0 auto;
    animation: pulse 2s ease-in-out infinite;
  }
  @keyframes pulse { 0%,100% { opacity: 1 } 50% { opacity: .35 } }

  .clue-list { display: grid; grid-template-columns: 1fr 1fr; gap: 5px 16px; }
  .clue {
    display: flex; align-items: baseline; gap: .5rem;
    font-size: .8rem; min-width: 0;
  }
  .clue .k {
    color: var(--muted); flex: 0 0 2.9em; font-size: .74rem; letter-spacing: .05em;
  }
  .clue .v {
    color: var(--text); font-weight: 400; overflow: hidden;
    text-overflow: ellipsis; white-space: nowrap;
  }
  .clue.wide { grid-column: 1 / -1; }
  .clue.wide .v { color: var(--accent-2); }

  .hint-area {
    font-size: .68rem; color: var(--dim); margin-bottom: .75rem;
    letter-spacing: .04em; display: flex; align-items: center; gap: .35rem;
  }

  /* ---------------------------------------------------------- 作答 */
  .input-group { display: grid; gap: 8px; margin-bottom: .85rem; }
  .field { display: grid; gap: 5px; }
  .field-label {
    display: flex; align-items: center; gap: .4rem;
    font-size: .66rem; color: var(--muted); letter-spacing: .1em;
    text-transform: uppercase;
  }
  .field-label .req {
    font-size: .54rem; color: var(--accent); letter-spacing: .08em;
    padding: .06rem .3rem; border-radius: 3px;
    background: rgba(255,107,53,.1); border: 1px solid rgba(255,107,53,.2);
  }

  .choice-row { display: flex; flex-wrap: wrap; gap: 5px; }
  .choice {
    position: relative;
    padding: .3rem .74rem;
    font-family: inherit; font-size: .78rem; line-height: 1.35;
    color: var(--text-2);
    background: linear-gradient(160deg, var(--panel-2), var(--panel-b));
    border: 1px solid var(--line);
    border-radius: 999px;
    cursor: pointer;
    white-space: nowrap;
    transition: transform .13s, border-color .13s, color .13s, background .13s, box-shadow .13s;
  }
  /* 发色那一排：固定 9 列，正好一行放下，不会孤零零掉一个 */
  .choice-row.hair-row {
    display: grid;
    grid-template-columns: repeat(9, minmax(0, 1fr));
    gap: 4px;
  }
  .choice-row.hair-row .choice {
    padding: .3rem .2rem; text-align: center; font-size: .72rem;
  }
  /* 人气：5 个等分 */
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
    color: #0a0c10; font-weight: 400;
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

  /* 角色名下拉 */
  .select-shell { position: relative; }
  .select-shell::after {
    content: "▾"; position: absolute; right: .85rem; top: 50%;
    transform: translateY(-50%); pointer-events: none;
    color: var(--muted); font-size: .7rem;
  }
  select.name-select {
    width: 100%; appearance: none; -webkit-appearance: none;
    padding: .42rem 2rem .42rem .8rem;
    font-family: inherit; font-size: .82rem; color: var(--text-2);
    background: linear-gradient(160deg, var(--panel-2), var(--panel-b));
    border: 1px solid var(--line); border-radius: 9px;
    cursor: pointer; outline: none;
    transition: border-color .14s, color .14s, box-shadow .14s;
  }
  select.name-select:hover:not(:disabled) { border-color: rgba(255,107,53,.35); }
  select.name-select:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(255,107,53,.12); }
  select.name-select.picked { color: var(--accent-2); border-color: rgba(255,201,60,.45); }
  select.name-select.correct { color: var(--ok); border-color: rgba(52,217,155,.55); }
  select.name-select.wrong { color: var(--bad); border-color: rgba(255,95,109,.5); }
  select.name-select:disabled { opacity: .5; cursor: not-allowed; }
  select.name-select option { background: #171c26; color: var(--text); }

  /* ---------------------------------------------------------- 提交 */
  .submit-row { display: flex; gap: 8px; }
  #submitBtn {
    position: relative; flex: 1 1 auto; overflow: hidden;
    padding: .6rem 1.2rem;
    font-family: var(--font-num); font-weight: 700; font-size: .82rem;
    letter-spacing: .16em; color: #0a0c10;
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
    font-family: inherit; font-size: .76rem; color: var(--muted);
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
    padding: .26rem .62rem; font-size: .74rem;
    background: rgba(26,32,43,.7);
    border: 1px solid var(--line); border-radius: 7px;
    animation: riseIn .22s ease both;
  }
  .feedback-item .label { color: var(--muted); letter-spacing: .06em; }
  .feedback-item .correct { color: var(--ok); }
  .feedback-item .wrong { color: var(--bad); }

  .message {
    margin-top: .6rem; font-size: .8rem; line-height: 1.55;
    min-height: 1.35em; letter-spacing: .02em;
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
    font-size: .72rem; font-weight: 400; color: var(--text-2);
    letter-spacing: .12em; text-transform: uppercase;
  }

  .ref-box summary {
    display: flex; align-items: center; justify-content: space-between;
    list-style: none; cursor: pointer;
    font-size: .72rem; color: var(--text-2);
    letter-spacing: .12em; text-transform: uppercase;
    transition: color .15s;
  }
  .ref-box summary:hover { color: var(--accent); }
  .ref-box summary::-webkit-details-marker { display: none; }
  .ref-box summary .chev {
    color: var(--muted); font-size: .62rem;
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
    padding: .16rem .1rem; font-size: .69rem; color: var(--muted);
    border-bottom: 1px solid rgba(255,255,255,.035);
  }
  .ref-grid .item .highlight { color: var(--text-2); flex: 0 0 auto; }

  .rank-item {
    display: flex; justify-content: space-between; align-items: baseline;
    padding: .24rem 0; font-size: .75rem; color: var(--muted);
  }
  .rank-item .value {
    font-family: var(--font-num); color: var(--accent-2); font-size: .82rem;
  }
  #clearRankBtn {
    width: 100%; margin-top: .6rem; padding: .38rem .8rem;
    font-family: inherit; font-size: .68rem; color: #d45a6a;
    background: rgba(212,90,106,.08);
    border: 1px solid rgba(212,90,106,.22);
    border-radius: 0 16px 0 16px; cursor: pointer;
    transition: background .15s, border-color .15s;
  }
  #clearRankBtn:hover { background: rgba(212,90,106,.18); border-color: rgba(212,90,106,.4); }

  .watermark {
    position: fixed; bottom: 8px; left: 50%; transform: translateX(-50%);
    z-index: 1; pointer-events: none;
    font-size: .6rem; color: rgba(111,125,144,.42); letter-spacing: .14em;
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
    .choice { font-size: .74rem; padding: .26rem .62rem; }
    /* 窄屏放不下 9 列，改回自动换行，文字才不会被截断 */
    .choice-row.hair-row { display: flex; flex-wrap: wrap; gap: 5px; }
    .choice-row.hair-row .choice { padding: .28rem .6rem; font-size: .74rem; }
    .difficulty-box { padding: 1.9rem 1.3rem 1.5rem; }
    .crest { width: 68px; height: 68px; }
  }

  /* 尊重系统的减少动效设置 */
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

<div id="difficultyOverlay">
  <div class="difficulty-box">
    <img class="crest" src="data:image/jpeg;base64,__LOGO__" alt="" />
    <h1>真卡奴就玩弗一把</h1>
    <p>选几条命，开始你的挑战</p>
    <div class="btn-group">
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
  </div>
</div>

<div class="game-container" id="gameContainer">
  <div class="main-area" id="mainArea">

    <div class="topbar">
      <div class="avatar-wrap">
        <img class="logo" src="data:image/jpeg;base64,__LOGO__" alt="" />
      </div>
      <div class="topbar-mid">
        <div class="eyebrow">🐾 卡奴请输入</div>
        <div class="score-line">
          <span class="score">🏆 <span id="currentScore">0</span></span>
          <span class="title-badge" id="titleBadge">杂鱼猫娘</span>
        </div>
      </div>
      <div class="attempts" id="attemptsDisplay"></div>
    </div>

    <div class="riddle">
      <div class="riddle-head"><span class="dot"></span>谜面 · 这位超弦体是</div>
      <div class="clue-list" id="riddleText"></div>
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
    <details class="panel ref-box" id="refBox">
      <summary>📋 参考信息 <span class="chev">▶</span></summary>
      <div class="ref-grid" id="refGrid"></div>
    </details>

    <div class="panel rank-box">
      <h3>🏅 排行榜</h3>
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

  var RANK_KEY = "karabiyo_rank_v7";

  var current = null;
  var score = 0, streak = 0, bestStreak = 0;
  var maxAttempts = 4, attempts = 4;
  var answered = false, gameOver = false, isHard = false;
  var picked = {};
  var difficultyChosen = false;
  var lastIndex = -1;

  var $ = function (id) { return document.getElementById(id); };
  var mainArea = $("mainArea"), currentScoreEl = $("currentScore"), titleBadge = $("titleBadge");
  var attemptsDisplay = $("attemptsDisplay"), riddleText = $("riddleText"), hintArea = $("hintArea");
  var inputGroup = $("inputGroup"), submitBtn = $("submitBtn"), restartBtn = $("restartBtn");
  var feedbackArea = $("feedbackArea"), message = $("message"), refGrid = $("refGrid");
  var bestScoreEl = $("bestScore"), bestStreakEl = $("bestStreak");
  var recent1 = $("recent1"), recent2 = $("recent2"), recent3 = $("recent3");

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

  /* -------------------------------------------------------- 排行榜 */
  function readRank() {
    try {
      var d = JSON.parse(localStorage.getItem(RANK_KEY) || "null") || {};
      return {
        best: Number(d.best) || 0,
        bestStreak: Number(d.bestStreak) || 0,
        recent: Array.isArray(d.recent) ? d.recent.slice(0, 3) : []
      };
    } catch (e) { return { best: 0, bestStreak: 0, recent: [] }; }
  }
  function writeRank(d) { try { localStorage.setItem(RANK_KEY, JSON.stringify(d)); } catch (e) {} }
  function renderRank() {
    var d = readRank();
    bestScoreEl.textContent = d.best > 0 ? d.best : "-";
    bestStreakEl.textContent = d.bestStreak > 0 ? d.bestStreak : "-";
    var s = [recent1, recent2, recent3];
    for (var i = 0; i < 3; i++) s[i].textContent = d.recent[i] !== undefined ? d.recent[i] : "-";
  }
  function commitScore() {
    var d = readRank();
    if (score > d.best) d.best = score;
    if (bestStreak > d.bestStreak) d.bestStreak = bestStreak;
    d.recent.unshift(score);
    if (d.recent.length > 3) d.recent = d.recent.slice(0, 3);
    writeRank(d); renderRank();
  }

  /* ------------------------------------------------------------ 渲染 */
  function renderAttempts() {
    var h = "";
    for (var i = 0; i < maxAttempts; i++) {
      h += '<span class="heart" style="animation-delay:' + (i * 40) + 'ms">' +
           (i < attempts ? "❤️" : "🖤") + "</span>";
    }
    attemptsDisplay.innerHTML = h;
  }
  function renderTitle() { titleBadge.textContent = titleFor(score); }

  function renderRef() {
    var h = "";
    for (var i = 0; i < CHARS.length; i++) {
      var c = CHARS[i];
      h += '<div class="item"><span class="highlight">' + esc(c.name) + "</span> · " +
           esc(c.faction) + " · " + esc(c.role) + " · " + esc(c.hair) + "</div>";
    }
    refGrid.innerHTML = h;
  }

  /* 谜面：交叉线索，绝不含答案字段 */
  function renderRiddle() {
    var c = current;
    var clues = [
      ["年龄", c.age + " 岁"],
      ["身高", c.height + " cm"],
      ["生日", c.birthday],
      ["武器", c.weapon + "（" + c.wtype + "）"]
    ];
    if (!isHard) clues.push(["性别", c.gender]);
    var h = "";
    for (var i = 0; i < clues.length; i++) {
      var wide = (clues[i][0] === "武器") ? " wide" : "";
      h += '<div class="clue' + wide + '"><span class="k">' + clues[i][0] +
           '</span><span class="v">' + esc(clues[i][1]) + "</span></div>";
    }
    riddleText.innerHTML = h;
    hintArea.textContent = isHard
      ? "🔒 硬核：线索更少，多答武器类型与人气"
      : "💡 参考表在右侧，可展开查看阵营与发色";
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

  function makeNameSelect() {
    var wrap = document.createElement("div");
    wrap.className = "field";
    var lab = document.createElement("span");
    lab.className = "field-label";
    lab.innerHTML = '角色名 <span class="req">必答</span>';
    wrap.appendChild(lab);

    var shell = document.createElement("div");
    shell.className = "select-shell";

    var sel = document.createElement("select");
    sel.className = "name-select";
    sel.id = "nameSelect";
    var ph = document.createElement("option");
    ph.value = ""; ph.textContent = "— 请选择角色 —"; ph.disabled = true; ph.selected = true;
    sel.appendChild(ph);
    CHARS.forEach(function (c) {
      var o = document.createElement("option");
      o.value = c.name; o.textContent = c.name;
      sel.appendChild(o);
    });
    sel.addEventListener("change", function () {
      if (answered || gameOver) return;
      if (!sel.value) return;
      picked.name = sel.value;
      sel.classList.add("picked");
      message.textContent = "";
      message.className = "message";
    });
    shell.appendChild(sel);
    wrap.appendChild(shell);
    return wrap;
  }

  function buildInputs() {
    inputGroup.innerHTML = "";
    picked = {};
    inputGroup.appendChild(makePills("阵营", "faction", FACTIONS, null, true));
    inputGroup.appendChild(makeNameSelect());
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
    var all = inputGroup.querySelectorAll(".choice, .name-select");
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
    var sel = $("nameSelect");
    if (sel) {
      sel.classList.remove("picked");
      if (picked.name === c.name) sel.classList.add("correct");
      else sel.classList.add("wrong");
    }
  }

  /* ------------------------------------------------------------- 回合 */
  function loadNewRound() {
    if (gameOver) return;
    var idx;
    do { idx = randInt(0, CHARS.length - 1); } while (CHARS.length > 1 && idx === lastIndex);
    lastIndex = idx;
    current = CHARS[idx];

    attempts = maxAttempts;
    answered = false;
    picked = {};

    renderAttempts();
    renderRiddle();
    buildInputs();
    feedbackArea.innerHTML = "";
    message.textContent = "";
    message.className = "message";
    submitBtn.disabled = false;
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
      var combo = streak >= 3 ? " 🔥" + streak + " 连击！" : "";
      message.textContent = "🎉 完美！就是 " + current.name + " 喵～" + combo;
      message.className = "message success";
      setTimeout(loadNewRound, 1000);
    } else {
      attempts--;
      streak = 0;
      renderAttempts();
      markAnswers(current);

      if (attempts <= 0) {
        answered = true;
        gameOver = true;
        disableChoices();
        message.textContent = "❌ 机会用尽。正确答案：" + current.name + " · " + current.faction +
          " · " + current.hair + " · " + current.wtype + " 喵～";
        message.className = "message fail";
        commitScore();
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
    currentScoreEl.textContent = "0";
    renderTitle();
    feedbackArea.innerHTML = "";
    message.textContent = "🔄 新挑战开始喵～";
    message.className = "message info";
    loadNewRound();
  }

  function startGame(n) {
    if (difficultyChosen) return;
    difficultyChosen = true;
    maxAttempts = n;
    isHard = (n === 3);
    score = 0; streak = 0; bestStreak = 0;
    gameOver = false; answered = false;
    currentScoreEl.textContent = "0";
    renderTitle();
    $("difficultyOverlay").classList.add("hidden");
    $("gameContainer").style.display = "grid";
    renderRef();
    renderRank();
    loadNewRound();
  }

  $("diff3").addEventListener("click", function () { startGame(3); });
  $("diff4").addEventListener("click", function () { startGame(4); });
  submitBtn.addEventListener("click", handleSubmit);
  restartBtn.addEventListener("click", restartGame);
  $("clearRankBtn").addEventListener("click", function () {
    if (confirm("确定要清空所有排行榜记录吗喵？")) {
      try { localStorage.removeItem(RANK_KEY); } catch (e) {}
      renderRank();
      message.textContent = "🗑️ 排行榜已重置喵～";
      message.className = "message info";
    }
  });

  document.addEventListener("keydown", function (e) {
    if (!difficultyChosen) return;
    if (e.key === "Enter" && !gameOver) { e.preventDefault(); handleSubmit(); }
  });

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
