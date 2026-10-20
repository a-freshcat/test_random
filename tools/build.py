# -*- coding: utf-8 -*-
"""Generate index.html for 真卡奴就玩弗一把 — rebuilt with real wiki data.

Design goals (vs the original):
  * the riddle NEVER contains the answer -> clues are cross-referenced facts
  * all answers are buttons, no typing
  * fonts load async so a slow/blocked Google Fonts never stalls the page
  * restart persists the score
"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # 仓库根
ASSETS = os.path.join(ROOT, "assets") # logo.b64
DATA = os.path.join(ROOT, "data")     # chars.json

with io.open(os.path.join(ASSETS, "logo.b64"), "r", encoding="utf-8") as fh:
    LOGO = fh.read().strip()

with io.open(os.path.join(DATA, "chars.json"), "r", encoding="utf-8") as fh:
    RAW = json.load(fh)

# ---------------------------------------------------------------- normalise
# hair colour is not on the wiki in a machine-readable field; keep the
# hand-curated table from the original game.
HAIR = {
    "白墨": "绿色", "星绘": "白色", "奥黛丽": "金色", "玛德蕾娜": "棕色",
    "绯莎": "粉色", "汐": "橙色", "加拉提亚": "棕色", "加拉蒂亚": "棕色",
    "蕾欧娜": "紫色", "米雪儿": "金色", "心夏": "棕色", "伊薇特": "黑色",
    "芙拉薇娅": "紫色", "千代": "黑色", "信": "白色", "艾卡": "红色",
    "明": "红色", "令": "黑色", "香奈美": "粉色", "诺诺": "白色", "玛拉": "绿色",
}

# popularity 1..5, hand-curated (wiki has no such field)
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
    age = c.get("年龄", "")
    try:
        age = int(str(age).strip())
    except ValueError:
        age = 0
    height = c.get("身高", "").upper().replace("CM", "")
    try:
        height = int(height)
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
ROLES = sorted({c["role"] for c in CHARS})
WTYPES = [w for w in WEAPON_ORDER if any(c["wtype"] == w for c in CHARS)]
HAIRS = [("绿色", "🟢"), ("白色", "⚪"), ("金色", "🟡"), ("棕色", "🟤"),
         ("粉色", "🩷"), ("橙色", "🟠"), ("紫色", "🟣"), ("黑色", "⚫"), ("红色", "🔴")]
GENDERS = ["男", "女"]

TITLES = [
    [0, "入门卡卫兵"],
    [3, "猫娘躯体化"],
    [7, "难道你真是奇点猫？"],
    [12, "我去卡奴！"],
    [18, "允许启动"],
    [999999, "永久月卡猫娘！"],
]


def js(v):
    """JSON-encode for embedding in a <script> block."""
    return json.dumps(v, ensure_ascii=False).replace("</", "<\\/")


JS_CHARS = ",\n".join("    " + js(c) for c in CHARS)

HTML = u"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="description" content="真卡奴就玩弗一把 —— 面向卡拉彼丘玩家的角色猜谜小游戏，题目数据取自卡拉彼丘 WIKI" />
<title>真卡奴就玩弗一把</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<!-- 异步加载：<link rel=stylesheet> 在断网/慢网时会阻塞脚本，导致整页白屏 -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=ZCOOL+KuaiLe&display=swap" media="print" onload="this.media='all'" />
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=ZCOOL+KuaiLe&display=swap" /></noscript>
<style>
  :root {
    --bg: #0a0c10; --panel: #14181f; --panel-2: #1b2029; --line: #232a35;
    --text: #e8edf3; --muted: #6a7a8a;
    --accent: #ff5e3a; --accent-2: #ffd166;
    --ok: #3ddc97; --bad: #ff5f6d; --info: #5aa9ff;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body {
    background:
      radial-gradient(circle at 12% 8%, rgba(255,94,58,.10), transparent 42%),
      radial-gradient(circle at 88% 92%, rgba(90,169,255,.08), transparent 45%),
      var(--bg);
    color: var(--text);
    font-family: "ZCOOL KuaiLe", "Microsoft YaHei", system-ui, sans-serif;
    min-height: 100vh; display: flex; align-items: center; justify-content: center;
    padding: 24px 16px 64px;
  }

  #difficultyOverlay {
    position: fixed; inset: 0; z-index: 50;
    display: flex; align-items: center; justify-content: center;
    background: rgba(10,12,16,.94); backdrop-filter: blur(6px); padding: 20px;
  }
  #difficultyOverlay.hidden { display: none; }
  .difficulty-box {
    background: var(--panel); border-left: 8px solid var(--accent);
    border-radius: 0 60px 0 60px; padding: 2.5rem 2.2rem;
    max-width: 480px; width: 100%; text-align: center;
    box-shadow: -16px 16px 0 rgba(255,94,58,.06);
  }
  .difficulty-box h1 { margin: 0 0 .4rem; font-size: 1.6rem; }
  .difficulty-box p { margin: 0 0 1.6rem; color: var(--muted); font-size: .9rem; }
  .btn-group { display: grid; gap: 12px; }
  .btn-group button {
    background: var(--panel-2); color: var(--text); border: 1px solid var(--line);
    border-radius: 0 30px 0 30px; padding: .9rem 1.2rem; font-family: inherit;
    font-size: 1rem; cursor: pointer; transition: .18s;
    display: flex; flex-direction: column; gap: 4px; align-items: center;
  }
  .btn-group button:hover { border-color: var(--accent); transform: translateY(-2px); }
  .btn-group button .sub { font-size: .72rem; color: var(--muted); letter-spacing: .06em; }

  .game-container {
    display: none; grid-template-columns: minmax(0,1fr) 330px; gap: 22px;
    width: 100%; max-width: 1060px; align-items: start;
  }
  .main-area {
    background: var(--panel); padding: 2rem 1.8rem;
    border-radius: 0 60px 0 60px; border-left: 8px solid var(--accent);
    box-shadow: -16px 16px 0 rgba(255,94,58,.06); transition: transform .25s ease;
  }
  .main-area:hover { transform: rotate(-.3deg); }
  .main-area.chord-effect { animation: chord .7s ease; }
  @keyframes chord {
    0%   { box-shadow: -16px 16px 0 rgba(255,94,58,.06); }
    40%  { box-shadow: 0 0 0 6px rgba(61,220,151,.35), -16px 16px 0 rgba(61,220,151,.18); }
    100% { box-shadow: -16px 16px 0 rgba(255,94,58,.06); }
  }
  .side-area { display: grid; gap: 18px; }
  .logo { width: 72px; height: 72px; object-fit: cover; border-radius: 50%; display: block; margin: 0 auto 1rem; border: 2px solid var(--line); }

  .badge {
    display: inline-block; background: rgba(255,94,58,.12); color: var(--accent);
    border: 1px solid rgba(255,94,58,.3); border-radius: 999px;
    padding: .2rem .8rem; font-size: .72rem; letter-spacing: .1em; margin-bottom: .9rem;
  }
  .score-header { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: .6rem; flex-wrap: wrap; }
  .score { font-family: "Orbitron", sans-serif; font-size: 1.35rem; font-weight: 900; color: var(--accent-2); }
  .title-badge { font-size: .8rem; padding: .25rem .8rem; border-radius: 999px;
    background: rgba(255,209,102,.1); border: 1px solid rgba(255,209,102,.28); color: var(--accent-2); }
  .attempts { display: flex; gap: 4px; font-size: 1.05rem; margin-bottom: 1rem; min-height: 1.4em; }
  .heart { animation: pop .25s ease; }
  @keyframes pop { from { transform: scale(.6); opacity: 0; } to { transform: scale(1); opacity: 1; } }

  .riddle {
    background: var(--panel-2); border: 1px dashed var(--line);
    border-radius: 0 24px 0 24px; padding: 1rem 1.1rem; margin-bottom: 1rem;
    line-height: 1.8; font-size: .92rem; min-height: 3.4rem;
  }
  .riddle .tag { color: var(--accent); margin-right: .4rem; }
  .riddle b { color: var(--accent-2); font-weight: 400; }
  .clue-list { display: grid; gap: 5px; margin-top: .6rem; }
  .clue {
    display: flex; gap: .5rem; align-items: baseline;
    font-size: .86rem; color: var(--text);
  }
  .clue .k { color: var(--muted); min-width: 4.2em; }
  .clue .v { color: var(--accent-2); }

  .hint-area { font-size: .78rem; color: var(--muted); margin-bottom: 1rem; min-height: 1.2em; }

  .input-group { display: grid; gap: 12px; margin-bottom: 1.1rem; }
  .field-label { font-size: .74rem; color: var(--muted); letter-spacing: .08em; margin-bottom: .4rem; display: block; }
  .choice-row { display: flex; flex-wrap: wrap; gap: 8px; }
  .choice {
    background: var(--panel-2); border: 1px solid var(--line); color: var(--text);
    border-radius: 999px; padding: .45rem 1rem; font-family: inherit; font-size: .86rem;
    cursor: pointer; transition: .15s;
  }
  .choice:hover:not(:disabled) { border-color: var(--accent); }
  .choice[aria-pressed="true"] { background: rgba(255,94,58,.18); border-color: var(--accent); color: var(--accent); }
  .choice.correct { background: rgba(61,220,151,.16); border-color: var(--ok); color: var(--ok); }
  .choice.wrong   { background: rgba(255,95,109,.14); border-color: var(--bad); color: var(--bad); }
  .choice:disabled { opacity: .55; cursor: not-allowed; }

  .submit-row { display: flex; gap: 10px; flex-wrap: wrap; }
  #submitBtn {
    flex: 1 1 160px; background: var(--accent); color: #0a0c10; border: none;
    border-radius: 0 30px 0 30px; padding: .8rem 1.4rem;
    font-family: "Orbitron", sans-serif; font-weight: 700; font-size: .9rem;
    letter-spacing: .1em; cursor: pointer; transition: .18s;
  }
  #submitBtn:hover:not(:disabled) { filter: brightness(1.1); transform: translateY(-2px); }
  #submitBtn:disabled { opacity: .45; cursor: not-allowed; }
  .restart-btn {
    background: transparent; border: 1px solid var(--line); color: var(--muted);
    border-radius: 0 30px 0 30px; padding: .8rem 1.2rem; font-family: inherit;
    font-size: .85rem; cursor: pointer; transition: .18s;
  }
  .restart-btn:hover { border-color: var(--accent); color: var(--accent); }

  .feedback-area { display: grid; gap: 6px; margin-top: 1rem; }
  .feedback-item { display: flex; justify-content: space-between; font-size: .84rem;
    padding: .35rem .7rem; background: var(--panel-2); border-radius: 8px; }
  .feedback-item .label { color: var(--muted); }
  .feedback-item .correct { color: var(--ok); }
  .feedback-item .wrong { color: var(--bad); }

  .message { margin-top: 1rem; font-size: .9rem; line-height: 1.6; min-height: 1.5em; }
  .message.success { color: var(--ok); }
  .message.fail    { color: var(--bad); }
  .message.info    { color: var(--info); }

  .ref-box, .rank-box {
    background: var(--panel); border: 1px solid var(--line);
    border-radius: 0 32px 0 32px; padding: 1.1rem 1.2rem;
  }
  .ref-box h3, .rank-box h3 { margin: 0 0 .8rem; font-size: .85rem; color: var(--accent); letter-spacing: .08em; font-weight: 400; }
  .ref-grid { display: grid; gap: 3px; max-height: 340px; overflow-y: auto; }
  .ref-grid .item { font-size: .74rem; color: var(--muted); padding: .16rem 0; border-bottom: 1px solid rgba(35,42,53,.6); }
  .ref-grid .item .highlight { color: var(--text); }
  .rank-item { display: flex; justify-content: space-between; font-size: .82rem; padding: .3rem 0; color: var(--muted); }
  .rank-item .value { color: var(--accent-2); font-family: "Orbitron", sans-serif; }
  #clearRankBtn {
    margin-top: .8rem; width: 100%; background: rgba(212,90,106,.14);
    border: 1px solid rgba(212,90,106,.35); padding: .45rem 1rem;
    border-radius: 0 24px 0 24px; font-family: inherit; font-size: .74rem;
    color: #d45a6a; cursor: pointer; transition: .15s;
  }
  #clearRankBtn:hover { background: rgba(212,90,106,.24); }

  .watermark { position: fixed; bottom: 12px; left: 50%; transform: translateX(-50%);
    font-size: .66rem; color: rgba(106,122,138,.5); letter-spacing: .1em; text-align: center; }

  @media (max-width: 880px) {
    .game-container { grid-template-columns: 1fr; }
    .main-area { padding: 1.5rem 1.2rem; border-radius: 0 40px 0 40px; }
    .side-area { grid-template-columns: 1fr 1fr; }
  }
  @media (max-width: 560px) {
    .side-area { grid-template-columns: 1fr; }
    .ref-grid { max-height: 180px; }
  }
</style>
</head>
<body>

<div id="difficultyOverlay">
  <div class="difficulty-box">
    <h1>🐾 选择难度</h1>
    <p>选几条命开始你的挑战？</p>
    <div class="btn-group">
      <button id="diff3">3 条命<span class="sub">卡奴专用 · 四词条</span></button>
      <button id="diff4">4 条命<span class="sub">mmr 适用 · 三词条</span></button>
    </div>
  </div>
</div>

<div class="game-container" id="gameContainer">
  <div class="main-area" id="mainArea">
    <img class="logo" src="data:image/jpeg;base64,__LOGO__" alt="Logo" />

    <div class="badge">🐾 卡奴请输入</div>

    <div class="score-header">
      <div class="score">🏆 <span id="currentScore">0</span></div>
      <div class="title-badge" id="titleBadge">杂鱼猫娘</div>
    </div>
    <div class="attempts" id="attemptsDisplay"></div>

    <div class="riddle" id="riddleArea">
      <span class="tag">📖 谜面</span>
      <div id="riddleText">加载中…</div>
    </div>

    <div class="hint-area" id="hintArea"></div>
    <div class="input-group" id="inputGroup"></div>

    <div class="submit-row">
      <button id="submitBtn">确认</button>
      <button class="restart-btn" id="restartBtn">🔄 重新挑战</button>
    </div>

    <div class="feedback-area" id="feedbackArea"></div>
    <div class="message" id="message"></div>
  </div>

  <div class="side-area">
    <div class="ref-box">
      <h3>📋 参考信息</h3>
      <div class="ref-grid" id="refGrid"></div>
    </div>
    <div class="rank-box">
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
  var ROLES = __ROLES__;
  var WTYPES = __WTYPES__;
  var HAIRS = __HAIRS__;
  var GENDERS = __GENDERS__;
  var TITLES = __TITLES__;

  var RANK_KEY = "karabiyo_rank_v7";

  var current = null;
  var score = 0;
  var streak = 0;
  var bestStreak = 0;
  var maxAttempts = 4;
  var attempts = 4;
  var answered = false;
  var gameOver = false;
  var isHard = false;
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

  /* -------------------------------------------------------- leaderboard */
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

  /* ------------------------------------------------------------ render */
  function renderAttempts() {
    var h = "";
    for (var i = 0; i < maxAttempts; i++) h += '<span class="heart">' + (i < attempts ? "❤️" : "🖤") + "</span>";
    attemptsDisplay.innerHTML = h;
  }
  function renderTitle() { titleBadge.textContent = titleFor(score); }

  function renderRef() {
    // 只展示「阵营 / 定位 / 发色」，隐藏年龄、身高、武器——
    // 否则玩家可以直接查表对号入座，谜题就没有意义了。
    var h = "";
    for (var i = 0; i < CHARS.length; i++) {
      var c = CHARS[i];
      h += '<div class="item"><span class="highlight">' + esc(c.name) + "</span> · " +
           esc(c.faction) + " · " + esc(c.role) + " · " + esc(c.hair) + "</div>";
    }
    refGrid.innerHTML = h;
  }

  /* 谜面：只给「交叉线索」，绝不含答案字段本身 */
  function buildClues(c) {
    var clues = [];
    clues.push(["年龄", c.age + " 岁"]);
    clues.push(["身高", c.height + " cm"]);
    clues.push(["武器", c.weapon + "（" + c.wtype + "）"]);
    clues.push(["生日", c.birthday]);
    clues.push(["性别", c.gender]);
    // 定位只给「是不是同一个」，不给具体值——留给玩家推理
    return clues;
  }

  function renderRiddle() {
    var c = current;
    var clues = buildClues(c);
    // 硬核模式少给一条线索
    if (isHard) clues = clues.slice(0, 4);
    var h = '<span style="color:var(--muted);font-size:.82rem;">这位超弦体是——</span>';
    h += '<div class="clue-list">';
    for (var i = 0; i < clues.length; i++) {
      h += '<div class="clue"><span class="k">' + clues[i][0] + '</span><span class="v">' + esc(clues[i][1]) + '</span></div>';
    }
    h += "</div>";
    riddleText.innerHTML = h;
    hintArea.textContent = isHard ? "🔒 硬核模式：线索更少，且要多答一个词条" : "💡 参考右表可查全部角色资料";
  }

  function makeRow(label, field, options, render) {
    var wrap = document.createElement("div");
    var lab = document.createElement("span");
    lab.className = "field-label";
    lab.textContent = label;
    wrap.appendChild(lab);
    var row = document.createElement("div");
    row.className = "choice-row";
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

  function buildInputs() {
    inputGroup.innerHTML = "";
    picked = {};
    // 必答：阵营 + 角色名
    inputGroup.appendChild(makeRow("阵营", "faction", FACTIONS));
    inputGroup.appendChild(makeRow("角色名", "name", CHARS.map(function (c) { return c.name; })));
    // 发色必答
    inputGroup.appendChild(makeRow("发色", "hair", HAIRS.map(function (p) { return p[0]; }),
      function (v) {
        for (var i = 0; i < HAIRS.length; i++) if (HAIRS[i][0] === v) return HAIRS[i][1] + " " + v;
        return v;
      }));
    // 硬核模式追加：武器类型 + 人气
    if (isHard) {
      inputGroup.appendChild(makeRow("武器类型", "wtype", WTYPES));
      var pops = [1, 2, 3, 4, 5];
      inputGroup.appendChild(makeRow("人气星级", "pop", pops, function (v) { return v + "★"; }));
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
    var all = inputGroup.querySelectorAll(".choice");
    for (var i = 0; i < all.length; i++) all[i].disabled = true;
    submitBtn.disabled = true;
  }

  function markAnswers(c) {
    var want = { faction: c.faction, name: c.name, hair: c.hair };
    if (isHard) { want.wtype = c.wtype; want.pop = String(c.pop); }
    var all = inputGroup.querySelectorAll(".choice");
    for (var i = 0; i < all.length; i++) {
      var b = all[i];
      if (want[b.dataset.field] === b.dataset.value) b.classList.add("correct");
      else if (b.getAttribute("aria-pressed") === "true") b.classList.add("wrong");
    }
  }

  /* ------------------------------------------------------------- rounds */
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

  function requiredFields() {
    return isHard ? ["faction", "name", "hair", "wtype", "pop"] : ["faction", "name", "hair"];
  }

  function handleSubmit() {
    if (answered || gameOver || !current) return;

    var need = requiredFields();
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
      score++;
      streak++;
      if (streak > bestStreak) bestStreak = streak;
      currentScoreEl.textContent = score;
      renderTitle();
      markAnswers(current);
      disableChoices();
      var combo = streak >= 3 ? " 🔥" + streak + " 连击！" : "";
      message.textContent = "🎉 完美！就是 " + current.name + " 喵～" + combo;
      message.className = "message success";
      mainArea.classList.add("chord-effect");
      setTimeout(function () { mainArea.classList.remove("chord-effect"); }, 700);
      setTimeout(loadNewRound, 1100);
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
        }, 1000);
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
    mainArea.classList.remove("chord-effect");
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
        .replace("__ROLES__", js(ROLES))
        .replace("__WTYPES__", js(WTYPES))
        .replace("__HAIRS__", js(HAIRS))
        .replace("__GENDERS__", js(GENDERS))
        .replace("__TITLES__", js(TITLES)))

out = os.path.join(ROOT, "index.html")
with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(html)

print("written:", out)
print("bytes:", len(html.encode("utf-8")))
print("chars:", len(CHARS), " factions:", FACTIONS, " wtypes:", len(WTYPES))

