const {chromium}=require('playwright');const assert=require('node:assert/strict');const fs=require('node:fs');
const base=process.env.PROTOCOL_URL||'http://127.0.0.1:8010';
(async()=>{
 fs.mkdirSync('test-results',{recursive:true});
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox','--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream']});
 const context=await browser.newContext({viewport:{width:1280,height:800},permissions:['camera']});
 const page=await context.newPage();const errors=[],bad=[],external=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400&&!r.url().endsWith('favicon.ico'))bad.push(r.url()+':'+r.status());});page.on('request',r=>{if(!['127.0.0.1','localhost'].includes(new URL(r.url()).hostname))external.push(r.url());});
 const ready=async()=>{await page.waitForFunction(()=>!!globalThis.MonsterProtocol?.getScene());await page.waitForTimeout(700);};
 const scene=()=>page.evaluate(()=>MonsterProtocol.getScene().getName());
 const value=n=>page.evaluate(n=>{const v=MonsterProtocol.getScene().getGame().getVariables().get(n);return n==='Name'||n==='Message'?v.getAsString():v.getAsNumber();},n);
 async function click(name){const box=await page.evaluate(name=>{const o=MonsterProtocol.getScene().getObjects(name)[0];if(!o)throw Error('Missing object '+name);const c=document.querySelector('canvas').getBoundingClientRect();return {x:c.x+(o.getX()+o.getWidth()/2)*c.width/1280,y:c.y+(o.getY()+o.getHeight()/2)*c.height/800};},name);await page.mouse.move(box.x,box.y);await page.waitForTimeout(60);await page.mouse.click(box.x,box.y,{delay:45});await page.waitForFunction(()=>!MonsterProtocol.getScene().getGame().getInputManager().isMouseButtonReleased(0));await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));if(['Attack','Shield','Heal'].includes(name))await page.waitForFunction(()=>{const s=MonsterProtocol.getScene();return s.getObjects('MonsterBody').length>0&&(s.getName()!=='Arena'||(s.getObjects('Attack').length>0&&s.getVariables().get('Phase').getAsNumber()===0));});}
 async function waitScene(name){await page.waitForFunction(name=>MonsterProtocol.getScene().getName()===name,name);}
 try{
  await page.goto(base+'/demo/');await ready();
  assert.equal(await scene(),'MonsterCreator');
  const bodyY=await page.evaluate(()=>MonsterProtocol.getScene().getObjects('MonsterBody')[0].getY());
  await page.waitForTimeout(400);assert.notEqual(await page.evaluate(()=>MonsterProtocol.getScene().getObjects('MonsterBody')[0].getY()),bodyY,'Monster breathes/moves while idle');
  await click('Music');assert.equal(await value('MusicOn'),0);await click('Music');assert.equal(await value('MusicOn'),1);
  await page.waitForFunction(()=>MonsterWorld.getMusic()?.readyState>=2&&!MonsterWorld.getMusic().paused);

  const counts={Body:6,Eyes:8,Mouth:6,Arms:4,Legs:4,Horns:4,Nose:4,Ears:4,Tail:4,Wings:4};
  for(const [cat,n] of Object.entries(counts)){
   console.log('Selector',cat,'initial',await value(cat+'Variant'));await click(cat+'Prev');assert.equal(await value(cat+'Variant'),n-1,cat+' previous');
   for(let i=0;i<n;i++)await click(cat+'Next');assert.equal(await value(cat+'Variant'),n-1);
   await click(cat+'Next');assert.equal(await value(cat+'Variant'),0);
  }
  await click('EyesNext');assert.deepEqual(await page.evaluate(()=>MonsterProtocol.getScene().getObjects('MonsterEyes').map(o=>o.getAnimation())),[1,1]);
  await click('BodyNext');await click('HornsNext');await click('WingsNext');
  await click('Rename');await page.locator('#mp-name').fill('Комета');await page.locator('#mp-name-save').click();assert.equal(await value('Name'),'Комета');
  await click('Save');await click('BodyNext');await click('Load');assert.equal(await value('BodyVariant'),1);assert.equal(await value('Name'),'Комета');
  await page.screenshot({path:'test-results/01-creator.png'});
  await page.reload();await ready();await click('Load');assert.equal(await value('BodyVariant'),1);assert.equal(await value('Name'),'Комета');
  await click('ToLab');await waitScene('Lab');
  for(let i=0;i<6;i++)await click('Feed');assert.equal(await value('Energy'),100);
  for(let i=0;i<5;i++)await click('Train');assert.equal(await value('Strength'),30);assert.equal(await value('Energy'),0);assert.equal(await value('Level'),2);
  await click('Train');assert.equal(await value('XP'),5);assert.equal(await value('Energy'),0);
  await click('MonsterBody');assert(await page.evaluate(()=>MonsterWorld.events.some(e=>e.type==='pet')));await click('Rest');assert.equal(await value('Health'),100);await page.screenshot({path:'test-results/02-lab.png'});
  await click('Battle');await waitScene('Arena');
  const rivals=new Set();rivals.add(await page.evaluate(()=>MonsterProtocol.getScene().getObjects('EnemyTitle')[0].getString()));
  const before=await value('EnemyHP');await click('Shield');assert.equal(await value('Health'),97);assert.equal(await value('EnemyHP'),before);
  await page.screenshot({path:'test-results/03-arena.png'});
  // Real local neural model, real TM inference on image tensors and fake webcam.
  await click('Camera');await page.locator('#mp-demo').click();await page.waitForFunction(()=>!!MonsterProtocol.getModel());
  const predictions=await page.evaluate(async()=>{
   const out=[];const c=document.createElement('canvas');c.width=c.height=224;const ctx=c.getContext('2d');
   for(const color of ['#ff0000','#0000ff','#00ff00','#7f7f7f']){ctx.fillStyle=color;ctx.fillRect(0,0,224,224);const p=await MonsterProtocol.getModel().predict(c);out.push(p.reduce((a,b)=>a.probability>b.probability?a:b));}return out;
  });
  assert.deepEqual(predictions.map(p=>p.className),['ATTACK','SHIELD','HEAL','IDLE']);assert(predictions.every(p=>p.probability>=.85));
  const gate=await page.evaluate(()=>{MonsterProtocol.resetGate();const p=n=>[{className:n,probability:.98}];return [MonsterProtocol.gate(p('ATTACK'),100),MonsterProtocol.gate(p('ATTACK'),700),MonsterProtocol.gate(p('ATTACK'),2300),MonsterProtocol.gate(p('IDLE'),2400),MonsterProtocol.gate(p('IDLE'),2900),MonsterProtocol.gate(p('SHIELD'),3000),MonsterProtocol.gate(p('SHIELD'),3600)];});
  assert.deepEqual(gate,[0,1,0,0,0,0,2]);
  await page.locator('#mp-start').click();await page.waitForSelector('#mp-video');await page.waitForFunction(()=>document.getElementById('mp-video')?.readyState>=2);
  const tracks=await page.evaluate(()=>{globalThis.testCameraStream=document.getElementById('mp-video').srcObject;return testCameraStream.getVideoTracks().length;});assert.equal(tracks,1);
  await page.locator('#mp-stop').click();assert.equal(await page.evaluate(()=>testCameraStream.getTracks().every(t=>t.readyState==='ended')),true);
  // Import a genuine three-file TF.js/TM export, not a mock network response.
  await page.locator('#mp-model-files').setInputFiles(['teacher/demo-model/model.json','teacher/demo-model/metadata.json','teacher/demo-model/weights.bin']);
  await page.waitForFunction(()=>document.getElementById('mp-status').textContent.includes('Модель готова'));
  // Feed a synthetic camera stream into the SAME real model/adapter/game pipeline.
  // This controls image pixels, never the predicted class or gameplay variables.
  await page.evaluate(()=>{
   globalThis.fixtureColor='#7f7f7f';const canvas=document.createElement('canvas');canvas.width=canvas.height=224;const ctx=canvas.getContext('2d');
   const paint=()=>{ctx.fillStyle=fixtureColor;ctx.fillRect(0,0,224,224);};paint();
   globalThis.fixtureTimer=setInterval(paint,70);globalThis.originalGetUserMedia=navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
   navigator.mediaDevices.getUserMedia=async()=>canvas.captureStream(12);
  });
  await page.locator('#mp-start').click();await page.waitForSelector('#mp-video');
  await page.waitForTimeout(700);const enemyBefore=await value('EnemyHP');
  await page.evaluate(()=>fixtureColor='#ff0000');
  await page.waitForFunction(before=>MonsterProtocol.getScene().getGame().getVariables().get('EnemyHP').getAsNumber()===before-30,enemyBefore,{timeout:15000});
  await page.waitForTimeout(1700);assert.equal(await value('EnemyHP'),enemyBefore-30,'held card must not repeat attack');
  await page.evaluate(()=>fixtureColor='#7f7f7f');await page.waitForFunction(()=>{const s=document.getElementById('mp-status').textContent;return s.startsWith('IDLE')&&s.includes('готов');},{},{timeout:15000});
  const energyBefore=await value('Energy');await page.evaluate(()=>fixtureColor='#00ff00');
  await page.waitForFunction(before=>MonsterProtocol.getScene().getGame().getVariables().get('Energy').getAsNumber()===before-20,energyBefore,{timeout:15000});
  await page.locator('#mp-stop').click();await page.evaluate(()=>{clearInterval(fixtureTimer);navigator.mediaDevices.getUserMedia=originalGetUserMedia;});
  await page.waitForFunction(()=>MonsterProtocol.getScene().getVariables().get('Phase').getAsNumber()===0);
  assert.equal(await scene(),'Arena');await page.screenshot({path:'test-results/04-ai-panel.png'});await page.locator('#mp-close').click();
  // Complete all three battles with actual UI events, no injected gameplay stats.
  for(let round=1;round<=3;round++){
   if(await scene()==='Lab'){await click('Rest');await click('Battle');await waitScene('Arena');}
   assert.equal(await value('Round'),round);rivals.add(await page.evaluate(()=>MonsterProtocol.getScene().getObjects('EnemyTitle')[0].getString()));
   for(let moves=0;moves<30&&(await scene())==='Arena';moves++)await click((await value('Energy'))<10?'Shield':'Attack');
   assert.equal(await value('Wins'),round);
   assert.equal(await scene(),round===3?'Final':'Lab');
   if(round===1){assert.equal(await value('Gold'),20);await click('Decor');assert.equal(await value('RoomStyle'),1);assert.equal(await value('Gold'),0);}

  }
  assert.equal(rivals.size,3,'Distinct named opponents');assert(await page.evaluate(()=>MonsterWorld.events.some(e=>e.type==='enemy-counterattack')));assert(await page.evaluate(()=>MonsterWorld.events.some(e=>e.type==='player-damage'&&e.amount===24)),'Third rival has a genuine empowered counterattack');
  await page.screenshot({path:'test-results/05-final.png'});await click('Home');await waitScene('Lab');await click('Battle');await waitScene('Final');assert.equal(await value('Round'),3,'Completed campaign cannot enter nonexistent fourth arena');await click('Again');await waitScene('Lab');assert.equal(await value('Wins'),0);assert.equal(await value('Name'),'Комета');assert.equal(await value('Badges'),3);assert.equal(await value('RoomStyle'),1);await page.screenshot({path:'test-results/07-upgraded-home.png'});
  // Diagnose defeat separately with a deliberately seeded boundary state.
  await click('Battle');await waitScene('Arena');await page.evaluate(()=>{const v=MonsterProtocol.getScene().getGame().getVariables();v.get('Health').setNumber(1);v.get('Energy').setNumber(0);});
  await click('Attack');assert.equal(await scene(),'Arena');assert.equal(await value('EnemyHP'),60);await click('Shield');await waitScene('Lab');assert.equal(await value('Health'),0);await click('Rest');assert.equal(await value('Health'),100);
  await click('Creator');await waitScene('MonsterCreator');
  await page.evaluate(()=>localStorage.setItem('monster-protocol-v1',JSON.stringify({version:1,values:{Name:'bad'}})));await click('Load');assert.equal(await value('Name'),'Комета');
  // Starter: one ready sample for each of Body/Eyes, other features are learning tasks.
  await page.goto(base+'/student-template/');await ready();await click('BodyNext');assert.equal(await value('BodyVariant'),1);await click('EyesNext');assert.equal(await value('EyesVariant'),1);await click('MouthNext');assert.equal(await value('MouthVariant'),0);
  await page.screenshot({path:'test-results/06-student.png'});
  await page.setViewportSize({width:1366,height:768});await page.waitForTimeout(500);await click('BodyNext');assert.equal(await value('BodyVariant'),2);
  assert.deepEqual(errors,[],'No JS errors');assert.deepEqual(bad,[],'No failed resources');assert.deepEqual(external,[],'No external network requests during gameplay and local ML');
  console.log('PASS: native GDevelop exports; 10 selectors/wraparound; paired eyes; rename/save/reload; energy/training/levels; 3-battle campaign; failure/recovery; AI real inference, local model import, webcam lifecycle, gate; starter and 1366×768 input.');
  fs.writeFileSync('test-results/result.json',JSON.stringify({passed:true,checks:['native-scenes','idle-animation','music-playback-and-mute','pet-reaction','three-distinct-rivals','animated-counterattack','home-upgrades-and-trophies','10-selectors','paired-eyes','save-reload','training','campaign','failure-recovery','real-neural-inference','model-import','fake-webcam','real-camera-pixels-to-game-command','command-gate','student-template','laptop-resolution'],pageErrors:errors,failedResources:bad,externalRequests:external},null,2));
 }catch(error){console.error('Failure context:',await page.evaluate(()=>({scene:globalThis.MonsterProtocol?.getScene()?.getName(),status:document.getElementById('mp-status')?.textContent,battle:document.getElementById('mp-battle-state')?.textContent})));await page.screenshot({path:'test-results/failure.png'});throw error;}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
