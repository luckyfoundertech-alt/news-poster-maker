import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const cwd = process.cwd();
const require = createRequire(path.join(cwd, 'package.json'));
const puppeteer = require('puppeteer-core');
const chromiumModule = await import(pathToFileURL(require.resolve('@sparticuz/chromium')).href);
const chromium = chromiumModule.default || chromiumModule;
const editor = path.join(cwd, 'apps/editor');
const publicDir = path.join(editor, 'public');
const index = JSON.parse(fs.readFileSync(path.join(publicDir, 'templates/index.json'), 'utf8'));
const wanted = new Set(['bharat-news','state-district','politics-public','cricket-sports','business-education','indian-festivals','national-culture']);
const templates = index.templates.filter(t => wanted.has(t.vibe));
if (templates.length < 3000) throw new Error('Expected 3000 Indian templates before thumbnail rendering; found '+templates.length);
const thumbDir = path.join(publicDir, 'templates/thumbs');
fs.mkdirSync(thumbDir, { recursive: true });
const allMissing = templates.filter(t => !fs.existsSync(path.join(thumbDir, t.id+'.jpg')));
const limit = Number(process.env.THUMBNAIL_LIMIT || 0);
const missing = limit > 0 ? allMissing.slice(0, limit) : allMissing;
console.log('Rendering '+missing.length+' missing Indian template previews (of '+templates.length+').');
if (!missing.length) process.exit(0);

const server = spawn('npm', ['run','dev','-w','@opentempl/editor','--','--host','127.0.0.1'], { cwd, stdio:'ignore', detached:false });
let browser;
try {
  let ready = false;
  for (let i=0;i<90;i++) {
    try { const r=await fetch('http://127.0.0.1:5181'); if(r.ok){ready=true;break;} } catch {}
    await new Promise(resolve=>setTimeout(resolve,1000));
  }
  if(!ready) throw new Error('Vite preview server did not start on port 5181.');
  browser = await puppeteer.launch({
    args: await puppeteer.defaultArgs({ args: chromium.args, headless: 'shell' }),
    defaultViewport: { width: 900, height: 1200, deviceScaleFactor: 1 },
    executablePath: await chromium.executablePath(),
    headless: 'shell',
  });
  const workers = 3;
  const pages = await Promise.all(Array.from({length:workers},()=>browser.newPage()));
  for(const page of pages) page.setDefaultTimeout(12000);
  const initialized = new WeakSet();
  let cursor=0, done=0;
  const failures=[];
  async function worker(page) {
    while(true) {
      const n=cursor++;
      if(n>=missing.length) return;
      const t=missing[n];
      const out=path.join(thumbDir,t.id+'.jpg');
      let success=false, lastError='';
      for(let attempt=0;attempt<2&&!success;attempt++) {
        try {
          const scale=480/t.width;
          const url='http://127.0.0.1:5181/#/render?vibe='+encodeURIComponent(t.vibe)+'&id='+encodeURIComponent(t.id)+'&scale='+scale;
          const hash = url.slice('http://127.0.0.1:5181/'.length);
          if (!initialized.has(page)) {
            await page.goto(url,{waitUntil:'domcontentloaded',timeout:20000});
            initialized.add(page);
          } else {
            await page.evaluate((nextHash) => {
              document.body.removeAttribute('data-ready');
              window.location.hash = nextHash;
            }, hash);
          }
          await page.waitForFunction(() => window.location.hash.startsWith('#/render'), { timeout: 12000 });
          await page.waitForFunction(() => document.body.hasAttribute('data-ready'), { timeout: 12000 });
          const renderState = await page.evaluate(() => ({
            ready: document.body.getAttribute('data-ready'),
            hash: window.location.hash,
            text: document.body.innerText.slice(0, 400),
          }));
          if (renderState.ready !== 'yes') throw new Error('Renderer state '+renderState.ready+': '+renderState.hash+' | '+renderState.text);
          const stage=await page.$('.render-page');
          if(!stage) throw new Error('render page element missing');
          await stage.screenshot({path:out,type:'jpeg',quality:72});
          success=true;
        } catch(e) {
          let state = '';
          try { state = JSON.stringify(await page.evaluate(() => ({ hash: location.hash, ready: document.body.getAttribute('data-ready'), text: document.body.innerText.slice(0,400) }))); } catch {}
          lastError = (e?.message || String(e)) + (state ? ' | ' + state : '');
        }
      }
      if(!success) failures.push(t.id+': '+lastError);
      done++;
      if(done%100===0||done===missing.length) console.log('Template previews '+done+'/'+missing.length);
    }
  }
  await Promise.all(pages.map(worker));
  await Promise.all(pages.map(p=>p.close()));
  if(failures.length) {
    console.error(failures.slice(0,30).join('\n'));
    throw new Error(failures.length+' template preview(s) failed to render.');
  }
  const verifySet = limit > 0 ? missing : templates;
  const absent=verifySet.filter(t=>!fs.existsSync(path.join(thumbDir,t.id+'.jpg')));
  if(absent.length) throw new Error(absent.length+' template preview files are missing after render.');
  console.log('Verified '+verifySet.length+' Indian template preview thumbnails.');
} finally {
  if(browser) await browser.close().catch(()=>{});
  server.kill('SIGTERM');
}
