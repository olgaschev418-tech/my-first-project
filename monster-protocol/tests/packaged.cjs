// Run AFTER extracting Monster_Protocol_Demo.zip. Validates the shipped launcher.
const {chromium}=require('playwright');const {spawn}=require('node:child_process');const path=require('node:path');const assert=require('node:assert/strict');
(async()=>{
 const root=process.argv[2];if(!root)throw Error('Usage: node tests/packaged.cjs /path/to/Monster_Protocol_Demo');
 const child=spawn('python3',[path.resolve(root,'start_demo.py'),'--no-browser','--port','8012'],{stdio:'pipe'});let log='';child.stdout.on('data',b=>log+=b);child.stderr.on('data',()=>{});
 let browser;
 try{
  for(let i=0;i<50;i++){try{const r=await fetch('http://127.0.0.1:8012/');if(r.ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
  assert(log.includes('MONSTER PROTOCOL'),'Shipped Python launcher started');
  browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox','--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const page=await browser.newPage({viewport:{width:1280,height:800}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:8012/');await page.waitForFunction(()=>!!globalThis.MonsterProtocol?.getScene());await page.waitForTimeout(500);
  async function click(name){const point=await page.evaluate(name=>{const o=MonsterProtocol.getScene().getObjects(name)[0];const c=document.querySelector('canvas').getBoundingClientRect();return{x:c.x+(o.getX()+o.getWidth()/2)*c.width/1280,y:c.y+(o.getY()+o.getHeight()/2)*c.height/800};},name);await page.mouse.move(point.x,point.y);await page.waitForTimeout(60);await page.mouse.click(point.x,point.y,{delay:45});await page.waitForFunction(()=>!MonsterProtocol.getScene().getGame().getInputManager().isMouseButtonReleased(0));await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));}
  await click('BodyNext');assert.equal(await page.evaluate(()=>MonsterProtocol.getScene().getGame().getVariables().get('BodyVariant').getAsNumber()),1);
  await click('ToLab');await page.waitForFunction(()=>MonsterProtocol.getScene().getName()==='Lab');
  await click('Battle');await page.waitForFunction(()=>MonsterProtocol.getScene().getName()==='Arena');
  await click('Camera');await page.locator('#mp-demo').click();await page.waitForFunction(()=>!!MonsterProtocol.getModel());
  const top=await page.evaluate(async()=>{const c=document.createElement('canvas');c.width=c.height=224;const x=c.getContext('2d');x.fillStyle='#ff0000';x.fillRect(0,0,224,224);return(await MonsterProtocol.getModel().predict(c)).reduce((a,b)=>a.probability>b.probability?a:b);});assert.equal(top.className,'ATTACK');assert(top.probability>.85);assert.deepEqual(errors,[]);
  console.log('PASS: extracted demo ZIP, shipped Python launcher, native controls/transitions, bundled real neural model.');
 }finally{if(browser)await browser.close();child.kill('SIGTERM');}
})().catch(e=>{console.error(e);process.exitCode=1;});
