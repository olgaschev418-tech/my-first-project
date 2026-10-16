const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const VM = require('scratch-vm');
const {ScratchStorage} = require('scratch-storage');
const sleep = ms => new Promise(r=>setTimeout(r,ms));
const root = path.resolve(__dirname,'..');
let vm;
async function main(){
  vm=new VM();vm.attachStorage(new ScratchStorage());
  await vm.loadProject(fs.readFileSync(path.join(root,'web/game/Monster_AI_Lab.sb3')));
  vm.start();vm.greenFlag();await sleep(150);
  const vars=vm.runtime.getTargetForStage().variables;
  const get=name=>vars['v_'+name].value;
  const put=(name,value)=>{vars['v_'+name].value=value;};
  async function command(key){
    vm.postIOData('keyboard',{key:key.toUpperCase(),isDown:true});
    await sleep(50);vm.postIOData('keyboard',{key:key.toUpperCase(),isDown:false});
    for(let i=0;i<70;i++){await sleep(25);if(Number(get('Ход'))===0)return;}
    throw new Error('Turn did not finish: '+key);
  }
  assert.equal(Number(get('Энергия')),50);
  for(let i=0;i<4;i++)await command('f');
  assert.equal(Number(get('Энергия')),100,'food must clamp energy');
  for(let i=0;i<5;i++)await command('t');
  assert.equal(Number(get('Уровень')),2);assert.equal(Number(get('Опыт')),0);assert.equal(Number(get('Сила')),20);
  put('Энергия',0);await command('t');assert.equal(Number(get('Сила')),20,'no free training');
  await command('r');assert.equal(Number(get('Энергия')),100);assert.equal(Number(get('Здоровье')),100);
  for(let i=0;i<3;i++)await command('t');
  assert.equal(Number(get('Сила')),24,'strength has a readable cap');
  await command('r');await command('b');assert.equal(Number(get('Сцена')),1);
  const enemyStart=Number(get('Здоровье врага'));
  put('Энергия',0);await command('a');assert.equal(Number(get('Здоровье врага')),enemyStart,'cannot attack without energy');
  await command('d');assert.equal(Number(get('Здоровье')),97);assert.equal(Number(get('Энергия')),18);
  put('Энергия',19);await command('h');assert.equal(Number(get('Здоровье')),97,'healing requires 20 energy');
  await command('q');await command('r');
  // Win the complete campaign using only real keyboard actions, no stat cheats.
  for(let encounter=1;encounter<=3;encounter++){
    await command('b');assert.equal(Number(get('Раунд')),encounter);
    let turns=0;
    while(Number(get('Сцена'))===1 && turns++<35){
      await command(Number(get('Счётчик ходов'))%3===2?'d':Number(get('Здоровье'))<38&&Number(get('Энергия'))>=20?'h':Number(get('Энергия'))<8?'d':'a');
    }
    assert.equal(Number(get('Сцена')),encounter===3?4:2,'encounter '+encounter+' won');
    assert.equal(Number(get('Здоровье врага')),0);
    if(encounter<3){await command('q');await command('r');}
  }
  assert.equal(Number(get('Победы')),3);
  await command('q');assert.equal(Number(get('Раунд')),1,'new campaign resets opponents');
  await command('r');await command('b');
  // Deliberate edge-state fixture for defeat and recovery.
  put('Здоровье',1);await command('d');assert.equal(Number(get('Сцена')),3);assert.equal(Number(get('Здоровье')),0);
  await command('q');await command('r');assert.equal(Number(get('Здоровье')),100);
  console.log('PASS: Scratch VM — food cap, training, level, energy gates, shield, 3 encounters, boss, defeat/recovery.');
  vm.quit();

  const {starterGesture,features,classifyKNN,GestureLatch}=await import('../web/gestures.mjs');
  const hand=extended=>Array.from({length:21},(_,i)=>({x:(i%4)*.02,y:i===0?.8:.5,z:0})).map((p,i)=>{
    if([8,12,16,20].includes(i))p.y=extended.includes(i)?.1:.65;return p;
  });
  assert.equal(starterGesture(hand([])),'attack');
  assert.equal(starterGesture(hand([8,12,16,20])),'defend');
  assert.equal(starterGesture(hand([8,12])),'heal');
  assert.equal(starterGesture(hand([8])),null);
  assert.equal(features(null),null);
  const examples=[];for(const [label,points] of [['attack',hand([])],['defend',hand([8,12,16,20])],['heal',hand([8,12])]])
    for(let i=0;i<5;i++)examples.push({label,vector:features(points)});
  assert.equal(classifyKNN(features(hand([8,12])),examples),'heal');
  assert.equal(classifyKNN(features(hand([])),[]),null);
  const latch=new GestureLatch();assert.equal(latch.update('attack',0),null);
  assert.equal(latch.update('attack',700),'attack');assert.equal(latch.update('attack',2000),null);
  assert.equal(latch.update('defend',2100),null);assert.equal(latch.update('defend',3000),null);
  latch.update(null,3100);latch.update(null,3700);latch.update('defend',3800);
  assert.equal(latch.update('defend',4500),'defend');
  console.log('PASS: AI command layer — 3 gestures, abstention, kNN examples, hold/release protection.');
}
main().catch(error=>{console.error(error);if(vm)vm.quit();process.exitCode=1;});
