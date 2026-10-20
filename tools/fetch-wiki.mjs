// Fetch {{超弦体}} template fields for every playable character from the klbq wiki.
import fs from 'node:fs';

const NAMES = [
  '白墨', '星绘', '奥黛丽', '玛德蕾娜', '绯莎', '汐', '加拉蒂亚',
  '蕾欧娜', '米雪儿', '心夏', '伊薇特', '芙拉薇娅', '千代', '信',
  '艾卡', '明', '令', '香奈美', '诺诺', '玛拉',
];

// wiki page titles differ from display names for some characters
const PAGE = {
  '奥黛丽': '奥黛丽·格罗夫',
  '玛德蕾娜': '玛德蕾娜·利里',
  '米雪儿': '米雪儿·李',
  '加拉蒂亚': '加拉蒂亚·利里',
};

const FIELDS = ['定位', '阵营', '英文名', '性别', '角色简介', '身高', '体重', '生日',
  '年龄', '中文声优', '武器名称', '武器类型', '超弦体特性', '兴趣爱好', '身份'];

function parseTemplate(wt) {
  const m = wt.match(/\{\{超弦体([\s\S]*?)\n\}\}/);
  if (!m) return null;
  const out = {};
  for (const line of m[1].split('\n')) {
    const kv = line.match(/^\s*\|\s*([^=]+?)\s*=\s*(.*)$/);
    if (!kv) continue;
    const key = kv[1].trim();
    if (FIELDS.includes(key)) out[key] = kv[2].trim();
  }
  return out;
}

const results = [];
for (const name of NAMES) {
  const title = PAGE[name] ?? name;
  const url = 'https://wiki.biligame.com/klbq/api.php?action=parse&page='
    + encodeURIComponent(title) + '&prop=wikitext&format=json';
  try {
    let r, attempt = 0, j;
    for (;;) {
      r = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' }, signal: AbortSignal.timeout(30000) });
      const text = await r.text();
      try { j = JSON.parse(text); break; } catch {
        attempt++;
        if (attempt >= 4) throw new Error('non-JSON after ' + attempt + ' tries (HTTP ' + r.status + ')');
        await new Promise((res) => setTimeout(res, 2500 * attempt));
      }
    }
        const wt = j.parse?.wikitext?.['*'] ?? '';
    if (!wt) { console.log('MISS  ' + name + '  (no wikitext)'); results.push({ name, error: 'no-wikitext' }); continue; }
    const t = parseTemplate(wt);
    if (!t) { console.log('MISS  ' + name + '  (no template)'); results.push({ name, error: 'no-template' }); continue; }
    t.name = name;
    t.page = title;
    results.push(t);
    console.log('OK    ' + name.padEnd(5) + ' | ' + (t['阵营'] ?? '?').padEnd(5) + ' | ' +
      (t['定位'] ?? '?').padEnd(3) + ' | ' + (t['武器类型'] ?? '?').padEnd(6) + ' | ' +
      (t['武器名称'] ?? '?').padEnd(5) + ' | 年龄 ' + (t['年龄'] ?? '?') + ' | ' + (t['性别'] ?? '?'));
  } catch (e) {
    console.log('ERR   ' + name + '  ' + e.message);
    results.push({ name, error: e.message });
  }
  await new Promise((r) => setTimeout(r, 1500));
}

fs.writeFileSync(process.argv[2], JSON.stringify(results, null, 2), 'utf8');
console.log('\nsaved ' + results.length + ' entries -> ' + process.argv[2]);
console.log('success: ' + results.filter((r) => !r.error).length + ' / ' + NAMES.length);

