const {chromium}=require('playwright');const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream']});
 try{
  const context=await browser.newContext({viewport:{width:1280,height:800},permissions:['camera']});const page=await context.newPage();const errors=[],bad=[],external=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400&&!r.url().endsWith('favicon.ico'))bad.push(r.url());});page.on('request',r=>{if(!['127.0.0.1','localhost'].includes(new URL(r.url()).hostname))external.push(r.url());});
  await page.goto((process.env.PROTOCOL_URL||'http://127.0.0.1:8010')+'/demo/');await page.waitForFunction(()=>!!globalThis.MonsterProtocol?.getScene());
  const value=n=>page.evaluate(n=>MonsterProtocol.getScene().getGame().getVariables().get(n).getAsNumber(),n);
  async function click(n){await page.waitForFunction(n=>!!MonsterProtocol.getScene()?.getObjects(n)[0],n);const p=await page.evaluate(n=>{const o=MonsterProtocol.getScene().getObjects(n)[0],c=document.querySelector('canvas').getBoundingClientRect();return{x:c.x+(o.getX()+o.getWidth()/2)*c.width/1280,y:c.y+(o.getY()+o.getHeight()/2)*c.height/800};},n);await page.mouse.move(p.x,p.y);await page.waitForTimeout(70);await page.mouse.click(p.x,p.y,{delay:45});await page.waitForTimeout(120);}
  await click('ToLab');await page.waitForFunction(()=>MonsterProtocol.getScene()?.getName()==='Lab'&&MonsterProtocol.getScene().getObjects('Battle').length);await click('Battle');await page.waitForFunction(()=>MonsterProtocol.getScene()?.getName()==='Arena'&&MonsterProtocol.getScene().getObjects('Camera').length);await click('Camera');await page.waitForFunction(()=>MonsterProtocol.getCameraState().running,{timeout:60000});
  await page.waitForFunction(()=>document.getElementById('mp-status')?.textContent.includes('Покажи одну руку'),{},{timeout:60000});
  assert.equal(await page.locator('#mp-overlay').count(),0);assert.equal(await value('EnemyHP'),60);assert.equal(await page.locator('#mp-model-files').isVisible(),false);
  // Actual MediaPipe/WASM inference on a blank fake webcam has just abstained.
  // Next isolate the landmark-to-command boundary with deterministic fixtures.
  const labels=await page.evaluate(()=>{
   globalThis.handFixture=extended=>Array.from({length:21},(_,i)=>({x:(i%4)*.02,y:i===0?.8:.5,z:0})).map((p,i)=>{if([8,12,16,20].includes(i))p.y=extended.includes(i)?.1:.65;if([6,10,14,18].includes(i))p.y=.5;return p;});
   return [[],[8,12,16,20],[8,12],[8]].map(v=>MonsterProtocol.handLabel(handFixture(v))).concat(MonsterProtocol.handLabel(null));
  });assert.deepEqual(labels,['ATTACK','SHIELD','HEAL','IDLE','IDLE']);
  await page.evaluate(()=>{globalThis.realSend=Hands.prototype.send;globalThis.realResults=Hands.prototype.onResults;Hands.prototype.onResults=function(fn){globalThis.fixtureResults=fn;return realResults.call(this,fn);};Hands.prototype.send=async function(){fixtureResults({multiHandLandmarks:globalThis.fixturePoints?[fixturePoints]:[]});};globalThis.fixturePoints=null;});
  await page.evaluate(()=>MonsterProtocol.stop());await page.locator('#mp-retry').click();await page.waitForFunction(()=>MonsterProtocol.getCameraState().running);
  await page.evaluate(()=>fixturePoints=handFixture([]));await page.waitForFunction(()=>MonsterProtocol.getScene().getGame().getVariables().get('EnemyHP').getAsNumber()===50);
  await page.waitForTimeout(3000);assert.equal(await value('EnemyHP'),50,'Held fist must not repeat after enemy counterattack');
  async function neutral(){await page.evaluate(()=>fixturePoints=null);await page.waitForTimeout(700);await page.waitForFunction(()=>MonsterProtocol.getScene().getVariables().get('Phase').getAsNumber()===0);}
  await neutral();const health=await value('Health');await page.evaluate(()=>fixturePoints=handFixture([8,12,16,20]));await page.waitForFunction(v=>MonsterProtocol.getScene().getGame().getVariables().get('Health').getAsNumber()===v-3,health);await page.waitForTimeout(1600);assert.equal(await value('EnemyHP'),50);
  await neutral();const energy=await value('Energy');await page.evaluate(()=>fixturePoints=handFixture([8,12]));await page.waitForFunction(v=>MonsterProtocol.getScene().getGame().getVariables().get('Energy').getAsNumber()===v-20,energy);
  await neutral();await page.evaluate(()=>fixturePoints=handFixture([8]));await page.waitForTimeout(1800);assert.equal(await value('EnemyHP'),50,'Unknown gesture abstains');
  await click('Shield');assert(await page.locator('#mp-camera').isVisible(),'Canvas controls remain usable beside camera');
  const box=await page.locator('#mp-drag').boundingBox();await page.mouse.move(box.x+40,box.y+10);await page.mouse.down();await page.mouse.move(150,180,{steps:8});await page.mouse.up();assert((await page.locator('#mp-camera').boundingBox()).x<300,'Window moves');
  await page.screenshot({path:'test-results/hand-camera.png'});await page.evaluate(()=>globalThis.savedStream=document.getElementById('mp-video').srcObject);await page.locator('#mp-close').click();assert(await page.evaluate(()=>savedStream.getTracks().every(t=>t.readyState==='ended')));
  // Restore actual inference for repeat start and a denied camera permission.
  await page.evaluate(()=>{Hands.prototype.send=realSend;Hands.prototype.onResults=realResults;});await click('Camera');await page.waitForFunction(()=>MonsterProtocol.getCameraState().running);await click('Camera');assert.equal(await page.locator('#mp-camera').count(),0);
  await context.clearPermissions();await context.grantPermissions([]);await page.evaluate(()=>{navigator.mediaDevices.getUserMedia=async()=>{throw new DOMException('denied','NotAllowedError');};});await click('Camera');await page.waitForFunction(()=>document.getElementById('mp-status')?.textContent.includes('Разреши камеру'));assert.equal(await page.evaluate(()=>MonsterProtocol.getCameraState().running),false);
  assert.deepEqual(errors,[]);assert.deepEqual(bad,[]);assert.deepEqual(external,[]);
  console.log('PASS: real local hand inference/no-hand abstention; fist/palm/two-finger mapping; landmark fixtures drive attack/shield/heal; held/unknown gestures do not repeat; draggable nonmodal window, canvas buttons, stop/restart/toggle, denied permission; no external requests.');
 }catch(e){for(const p of browser.contexts().flatMap(c=>c.pages())){console.error(await p.evaluate(()=>({state:globalThis.MonsterProtocol?.getCameraState(),scene:globalThis.MonsterProtocol?.getScene()?.getName(),status:document.getElementById('mp-status')?.textContent})));await p.screenshot({path:'/tmp/hand-camera-failure.png'});}throw e;}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
