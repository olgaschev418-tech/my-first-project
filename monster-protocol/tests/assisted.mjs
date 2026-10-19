// Reproduce the teacher workflow: activate the supplied scaffold and add pupil button events.
import {readFile,writeFile,cp,mkdir,rm} from 'node:fs/promises';
import {resolve} from 'node:path';
import {loadProject,exportProject,gd_internal_logs} from 'gdcore-tools';
import {createRequire} from 'node:module';const require=createRequire(import.meta.url);const {chromium}=require('playwright');const assert=require('node:assert/strict');
const source=resolve('build/assisted-source'),out=resolve('build/assisted-test');
await rm(source,{recursive:true,force:true});await rm(out,{recursive:true,force:true});await mkdir(source,{recursive:true});await cp('student-template/assets',source+'/assets',{recursive:true});
const data=JSON.parse(await readFile('student-template/game.json','utf8'));
data.firstLayout='Arena';
for(const [name,value] of Object.entries({UseBattleScaffold:1,Strength:30,Energy:100,Health:100,Wins:2,Round:3,EnemyHP:100}))data.variables.find(v=>v.name===name).value=String(value);
const arena=data.layouts.find(s=>s.name==='Arena');const buttons=arena.events.find(g=>g.name?.startsWith('04.2'));
const instruction=(type,...parameters)=>({type:{value:type,inverted:false},parameters,subInstructions:[]});
for(const [name,command]of [['Attack',1],['Shield',2],['Heal',3]])buttons.events.push({type:'BuiltinCommonInstructions::Standard',conditions:[instruction('MouseButtonReleased','','Left'),instruction('SourisSurObjet',name,'','',''),instruction('BuiltinCommonInstructions::Once'),instruction('VarScene','Phase','=','0')],actions:[instruction('ModVarScene','Command','=',String(command))],events:[]});
await writeFile(source+'/game.json',JSON.stringify(data));const project=await loadProject(source+'/game.json');await mkdir(out,{recursive:true});exportProject(project,out);project.delete();if(/^Error:/m.test(gd_internal_logs))throw Error(gd_internal_logs);
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox','--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1280,height:800}});const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto((process.env.PROTOCOL_URL||'http://127.0.0.1:8010')+'/assisted-test/');await page.waitForFunction(()=>!!globalThis.MonsterProtocol?.getScene());await page.waitForTimeout(600);
 const value=n=>page.evaluate(n=>MonsterProtocol.getScene().getGame().getVariables().get(n).getAsNumber(),n);
 async function click(n,wait=true){const point=await page.evaluate(n=>{const o=MonsterProtocol.getScene().getObjects(n)[0];const b=document.querySelector('canvas').getBoundingClientRect();return{x:b.x+(o.getX()+o.getWidth()/2)*b.width/1280,y:b.y+(o.getY()+o.getHeight()/2)*b.height/800};},n);await page.mouse.move(point.x,point.y);await page.waitForTimeout(50);await page.mouse.click(point.x,point.y,{delay:40});await page.waitForFunction(()=>!MonsterProtocol.getScene().getGame().getInputManager().isMouseButtonReleased(0));await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));if(wait)await page.waitForFunction(()=>{const s=MonsterProtocol.getScene();return s.getObjects('MonsterBody').length&&(s.getName()!=='Arena'||(s.getObjects('Attack').length&&s.getVariables().get('Phase').getAsNumber()===0));});}
 await click('Attack',false);await page.waitForFunction(()=>MonsterProtocol.getScene().getVariables().get('Phase').getAsNumber()>0);await click('Attack');assert.equal(await value('Energy'),90,'Busy click cannot buy a second attack');assert.equal(await value('Health'),88);assert.equal(await value('EnemyHP'),70);
 await click('Attack');assert.equal(await value('Health'),76);assert.equal(await value('EnemyHP'),40);assert((await page.evaluate(()=>MonsterProtocol.getScene().getObjects('EnemyIntent')[0].getString())).includes('СИЛЬНЫЙ'));
 await click('Shield');assert.equal(await value('Health'),73,'Shield limits the third empowered reply to 3');assert.equal(await value('Energy'),94);await click('Attack');await click('Attack');assert.equal(await value('Wins'),3);assert.equal(await value('Gold'),20);assert.equal(await page.evaluate(()=>MonsterProtocol.getScene().getName()),'Final');assert.deepEqual(errors,[]);
 console.log('PASS: supplied student scaffold + native pupil button events; busy-click lock; warning; shield against empowered strike; reward and finale.');
}finally{await browser.close();}
