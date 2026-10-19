// Record actual game frames for the repository preview; no animation is composited in post.
const {chromium}=require('playwright');const fs=require('node:fs');const {execFileSync}=require('node:child_process');
(async()=>{fs.mkdirSync('build/preview-frames',{recursive:true});const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox','--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});try{
const page=await browser.newPage({viewport:{width:1280,height:800}});page.on('pageerror',e=>console.log('PAGE ERROR',e.message));await page.goto((process.env.PROTOCOL_URL||'http://127.0.0.1:8010')+'/demo/');await page.waitForFunction(()=>!!globalThis.MonsterProtocol?.getScene());await page.waitForTimeout(500);
async function click(name){const b=await page.evaluate(n=>{const o=MonsterProtocol.getScene().getObjects(n)[0];const c=document.querySelector('canvas').getBoundingClientRect();return{x:c.x+(o.getX()+o.getWidth()/2)*c.width/1280,y:c.y+(o.getY()+o.getHeight()/2)*c.height/800};},name);await page.mouse.move(b.x,b.y);await page.waitForTimeout(50);await page.mouse.click(b.x,b.y,{delay:45});await page.waitForFunction(()=>!MonsterProtocol.getScene().getGame().getInputManager().isMouseButtonReleased(0));await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));}
await click('HornsNext');await click('EyesNext');await click('ToLab');await page.waitForFunction(()=>MonsterProtocol.getScene().getName()==='Lab');await click('Feed');let action=0;
for(let f=0;f<80;f++){
 if(f===8)await click('Train');
 if(f===20){await click('Battle');await page.waitForFunction(()=>MonsterProtocol.getScene().getName()==='Arena');}
 if(f>22&&f%4===0&&(await page.evaluate(()=>MonsterProtocol.getScene().getVariables().get('Phase').getAsNumber()))===0){await click(['Attack','Shield','Heal'][action++%3]);}
 await page.screenshot({path:'build/preview-frames/'+String(f).padStart(3,'0')+'.png'});await page.waitForTimeout(80);
}
}finally{await browser.close();}
execFileSync('ffmpeg',['-y','-v','error','-framerate','10','-i','build/preview-frames/%03d.png','-filter_complex','[0:v]scale=768:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=bayer:bayer_scale=3','-loop','0','docs/images/living-preview.gif'],{stdio:'inherit'});console.log('Captured actual GDevelop lab and combat animation.');})().catch(e=>{console.error(e);process.exitCode=1;});
