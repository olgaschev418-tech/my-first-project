// A stale offline worker ignores HTTP cache headers and even ?version= queries.
const {chromium}=require('playwright');
const http=require('node:http');const fs=require('node:fs');const os=require('node:os');const path=require('node:path');const {spawn}=require('node:child_process');const assert=require('node:assert/strict');
(async()=>{
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'monster-offline-'));fs.mkdirSync(path.join(root,'play'));fs.writeFileSync(path.join(root,'play/index.html'),'NEW GAME');fs.copyFileSync(path.resolve(__dirname,'../tools/start_demo.py'),path.join(root,'start_demo.py'));
 const stale=http.createServer((req,res)=>{
  if(req.url==='/old-worker.js'){res.setHeader('Content-Type','application/javascript');res.end(`self.addEventListener('install',e=>e.waitUntil(self.skipWaiting()));self.addEventListener('activate',e=>e.waitUntil(clients.claim()));self.addEventListener('fetch',e=>{if(e.request.mode==='navigate')e.respondWith(new Response('OLD GAME',{headers:{'Content-Type':'text/html'}}));});`);}
  else res.end('Initial page');
 });
 await new Promise(r=>stale.listen(0,'127.0.0.1',r));const oldPort=stale.address().port;
 let browser;const children=[];
 function launch(port){return new Promise((resolve,reject)=>{const c=spawn('python3',[path.join(root,'start_demo.py'),'--no-browser',...(port===undefined?[]:['--port',String(port)])]);children.push(c);let log='';c.stdout.on('data',b=>{log+=b;const m=log.match(/http:\/\/127\.0\.0\.1:\d+\/\?version=[^\s]+/);if(m)resolve(m[0]);});c.on('error',reject);});}
 try{
  browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});const context=await browser.newContext();const page=await context.newPage();
  await page.goto(`http://127.0.0.1:${oldPort}/`);
  await page.evaluate(async()=>{await navigator.serviceWorker.register('/old-worker.js');await navigator.serviceWorker.ready;if(!navigator.serviceWorker.controller)await new Promise(r=>navigator.serviceWorker.addEventListener('controllerchange',r,{once:true}));});
  await new Promise(r=>stale.close(r));
  const reused=await launch(oldPort);await page.goto(reused);assert.equal(await page.locator('body').innerText(),'OLD GAME','Reproduces old game despite version query and no-store headers');
  const fresh=await launch();assert.notEqual(new URL(fresh).origin,new URL(reused).origin);await page.goto(fresh);assert.equal(await page.locator('body').innerText(),'NEW GAME');assert.equal(await page.evaluate(()=>!!navigator.serviceWorker.controller),false);
  console.log('PASS: reproduced stale offline game on reused origin; default launcher bypasses it and serves NEW GAME in the same browser profile.');
 }finally{for(const c of children)c.kill();if(browser)await browser.close();stale.close();fs.rmSync(root,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1;});
