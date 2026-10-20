// Resolve file names to actual image URLs and download them.
import fs from 'node:fs';
import path from 'node:path';

const API = 'https://wiki.biligame.com/klbq/api.php';
const LIST = process.argv[2];
const OUTDIR = process.argv[3];

const items = JSON.parse(fs.readFileSync(LIST, 'utf8'));

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

fs.mkdirSync(OUTDIR, { recursive: true });

// Batch query imageinfo (up to 20 titles per request)
const resolved = [];
const BATCH = 10;
for (let i = 0; i < items.length; i += BATCH) {
  const chunk = items.slice(i, i + BATCH);
  const titles = chunk.map((c) => 'File:' + c.file).join('|');
  const j = await api({
    action: 'query', titles: titles, prop: 'imageinfo', iiprop: 'url|size|mime',
  });
  const pages = j.query?.pages ?? {};
  for (const key of Object.keys(pages)) {
    const p = pages[key];
    // wiki 会把 File: 规范化成 文件:，两种前缀都要剥掉
    const title = (p.title ?? '').replace(/^(File|文件):/, '');
    const match = chunk.find((c) => c.file === title);
    if (!match) continue;
    const info = p.imageinfo?.[0];
    if (!info) { console.log('NO-INFO ' + title); continue; }
    resolved.push({ name: match.name, file: title, url: info.url, w: info.width, h: info.height, mime: info.mime });
    console.log('  ' + match.name.padEnd(6) + ' ' + info.width + 'x' + info.height + '  ' + (info.mime ?? ''));
  }
  await new Promise((res) => setTimeout(res, 2000));
}

console.log('\n解析到 ' + resolved.length + ' / ' + items.length);
fs.writeFileSync(path.join(OUTDIR, '..', 'art-urls.json'), JSON.stringify(resolved, null, 2), 'utf8');

