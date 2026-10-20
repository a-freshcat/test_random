// Download portraits and downscale them for embedding in a single HTML file.
import fs from 'node:fs';
import path from 'node:path';

const URLS = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const OUTDIR = process.argv[3];
fs.mkdirSync(OUTDIR, { recursive: true });

let ok = 0, fail = 0;
for (const it of URLS) {
  const dest = path.join(OUTDIR, it.name + '.png');
  if (fs.existsSync(dest)) { console.log('SKIP ' + it.name); ok++; continue; }
  try {
    const r = await fetch(it.url, {
      headers: { 'User-Agent': 'Mozilla/5.0', Referer: 'https://wiki.biligame.com/klbq/' },
      signal: AbortSignal.timeout(60000),
    });
    if (!r.ok) { console.log('FAIL ' + it.name + '  HTTP ' + r.status); fail++; continue; }
    const buf = Buffer.from(await r.arrayBuffer());
    if (buf.length < 2000) { console.log('FAIL ' + it.name + '  too small ' + buf.length); fail++; continue; }
    fs.writeFileSync(dest, buf);
    console.log('OK   ' + it.name.padEnd(6) + ' ' + Math.round(buf.length / 1024) + ' KB');
    ok++;
  } catch (e) {
    console.log('ERR  ' + it.name + '  ' + e.message);
    fail++;
  }
  await new Promise((res) => setTimeout(res, 700));
}
console.log('\n下载完成: ' + ok + ' 成功 / ' + fail + ' 失败');
