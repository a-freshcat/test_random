// Find the "初始立绘" (default portrait) image for every character.
import fs from 'node:fs';

const API = 'https://wiki.biligame.com/klbq/api.php';
const OUT = process.argv[2];

const NAMES = [
  '白墨', '星绘', '奥黛丽', '玛德蕾娜', '绯莎', '汐', '加拉蒂亚',
  '蕾欧娜', '米雪儿', '心夏', '伊薇特', '芙拉薇娅', '千代', '信',
  '艾卡', '明', '令', '香奈美', '诺诺', '玛拉',
  '忧雾', '拉薇', '梅瑞狄斯', '珐格兰丝',
];
const PAGE = {
  '奥黛丽': '奥黛丽·格罗夫',
  '玛德蕾娜': '玛德蕾娜·利里',
  '米雪儿': '米雪儿·李',
  '加拉蒂亚': '加拉蒂亚·利里',
};

async function api(params, tries = 6) {
  const qs = new URLSearchParams({ ...params, format: 'json' }).toString();
  for (let attempt = 1; attempt <= tries; attempt++) {
    try {
      const r = await fetch(API + '?' + qs, {
        headers: { 'User-Agent': 'Mozilla/5.0' },
        signal: AbortSignal.timeout(30000),
      });
      const text = await r.text();
      try { return JSON.parse(text); } catch {
        await new Promise((res) => setTimeout(res, 3000 * attempt));
      }
    } catch (e) {
      await new Promise((res) => setTimeout(res, 3000 * attempt));
    }
  }
  throw new Error('api failed');
}

const out = [];

for (const name of NAMES) {
  const title = PAGE[name] ?? name;
  try {
    const j = await api({ action: 'parse', page: title, prop: 'images' });
    const imgs = j.parse?.images ?? [];
    // 优先「初始立绘」，其次任意「立绘」
    let pick = imgs.find((i) => i.indexOf('初始立绘') >= 0);
    if (!pick) pick = imgs.find((i) => i.indexOf('立绘') >= 0 && i.indexOf('时装') < 0);
    if (!pick) { console.log('MISS ' + name); continue; }
    out.push({ name: name, file: pick });
    console.log('OK   ' + name.padEnd(6) + ' -> ' + pick);
  } catch (e) {
    console.log('ERR  ' + name + '  ' + e.message);
  }
  await new Promise((res) => setTimeout(res, 1800));
}

fs.writeFileSync(OUT, JSON.stringify(out, null, 2), 'utf8');
console.log('\n找到 ' + out.length + ' / ' + NAMES.length);
