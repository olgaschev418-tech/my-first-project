import {LABELS, starterGesture, features, classifyKNN, GestureLatch} from './gestures.mjs';
const $ = id => document.getElementById(id);
const canvas = $('stage');
const vm = new window.VirtualMachine();
const renderer = new window.ScratchRender(canvas);
new ResizeObserver(()=>{
  const rect=canvas.getBoundingClientRect();
  renderer.resize(Math.round(rect.width*devicePixelRatio),Math.round(rect.height*devicePixelRatio));
}).observe(canvas);
vm.attachRenderer(renderer);
vm.attachStorage(new window.ScratchStorage.ScratchStorage());
const read = name => vm.runtime.getTargetForStage()?.variables['v_'+name]?.value;
let loaded=false, lastScene=-1, audio=null, sound=false, lastEnemyHP=60;
function chirp(frequency=440) {
  if (!sound) return;
  try {
    audio ||= new (window.AudioContext || window.webkitAudioContext)();
    audio.resume();
    const osc=audio.createOscillator(), gain=audio.createGain();
    osc.type='sine';osc.frequency.setValueAtTime(frequency,audio.currentTime);
    osc.frequency.exponentialRampToValueAtTime(frequency*1.5,audio.currentTime+.1);
    gain.gain.setValueAtTime(.045,audio.currentTime);gain.gain.exponentialRampToValueAtTime(.001,audio.currentTime+.18);
    osc.connect(gain);gain.connect(audio.destination);osc.start();osc.stop(audio.currentTime+.2);
  } catch {/* sound is optional */}
}
function press(key) {
  if (!loaded) return;
  const room=['f','t','r','b','n'], battle=['a','d','h'];
  const scene=Number(read('Сцена'));
  if (room.includes(key) && scene!==0 || battle.includes(key) && scene!==1) return;
  vm.postIOData('keyboard',{key:key.toUpperCase(),isDown:true});
  setTimeout(()=>vm.postIOData('keyboard',{key:key.toUpperCase(),isDown:false}),70);
  if (Number(read('Ход'))===0) chirp(key==='a'?280:520);
}
document.querySelectorAll('[data-key]').forEach(b=>b.addEventListener('click',()=>press(b.dataset.key)));
document.addEventListener('keydown', e=>{
  if (e.target instanceof HTMLInputElement || e.repeat || e.ctrlKey || e.metaKey || e.altKey) return;
  if ('ftrbadhqn'.includes(e.key.toLowerCase())) {e.preventDefault();press(e.key.toLowerCase());}
});
function mouse(e, isDown) {
  if (!loaded) return;
  const rect=canvas.getBoundingClientRect();
  vm.postIOData('mouse',{x:e.clientX-rect.left,y:e.clientY-rect.top,
    canvasWidth:rect.width,canvasHeight:rect.height,isDown});
}
canvas.addEventListener('pointerdown',e=>{canvas.focus();canvas.setPointerCapture(e.pointerId);mouse(e,true);});
canvas.addEventListener('pointermove',e=>mouse(e,Boolean(e.buttons)));
canvas.addEventListener('pointerup',e=>mouse(e,false));
canvas.addEventListener('pointercancel',e=>mouse(e,false));
$('answer-form').addEventListener('submit',e=>{
  e.preventDefault();$('ask').hidden=true;canvas.focus();
  vm.runtime.emit('ANSWER',$('answer').value.trim().slice(0,24)||'Искрик');
});
vm.runtime.on('QUESTION',question=>{
  // Scratch sends an empty string when the visible sprite asks in a bubble.
  // Only null means that the question has ended.
  $('ask').hidden=question===null;
  if(question!==null){$('question').textContent=question||'Как назовём питомца? Используй вымышленное имя.';$('answer').value='';$('answer').focus();}
});
$('restart').onclick=()=>{if(loaded){vm.greenFlag();latch.reset();chirp(660);}};
$('project-file').onchange=async event=>{
  const file=event.target.files[0];if(!file)return;
  if(file.size>10*1024*1024){$('hint').textContent='Выбери учебный .sb3 размером до 10 МБ.';return;}
  const previous=await vm.saveProjectSb3();
  loaded=false;vm.stopAll();
  try{
    await vm.loadProject(await file.arrayBuffer());
    const variables=vm.runtime.getTargetForStage()?.variables||{};
    if(!Object.keys(variables).includes('v_Сцена')||!Object.keys(variables).includes('v_Ход'))throw new Error('Нужен проект MONSTER AI LAB с исходными переменными');
    vm.greenFlag();latch.reset();lastScene=-1;
  }catch(error){await vm.loadProject(await previous.arrayBuffer());vm.greenFlag();$('ai-status').textContent='Не удалось открыть проект: '+error.message;}
  finally{loaded=true;event.target.value='';}
};
$('fullscreen').onclick=async()=>{
  try {if(document.fullscreenElement)await document.exitFullscreen();else await $('stage-wrap').requestFullscreen();}
  catch {$('hint').textContent='Полноэкранный режим недоступен в этом браузере.';}
};
$('sound').onclick=()=>{sound=!sound;$('sound').textContent='Звук: '+(sound?'вкл.':'выкл.');$('sound').setAttribute('aria-pressed',sound);chirp();};
function updateHUD() {
  if (!loaded) return;
  const scene=Number(read('Сцена')), round=Number(read('Раунд'));
  const names=['Шуршик','Тучка','Громобосс'];
  $('scene-label').textContent=scene===1 ? 'Арена / '+names[round-1] : 'Лаборатория / '+read('Имя');
  $('room-actions').hidden=scene!==0;
  $('battle-actions').hidden=scene!==1;
  $('result').hidden=scene<2;
  $('round').textContent=String(round).padStart(2,'0')+' / 03';
  if(scene!==lastScene){
    lastScene=scene;
    $('mission').textContent=scene===0?'Задание / Подготовь питомца':scene===1?'Испытание / '+names[round-1]:'Задание / Сделай выводы';
    if(scene>=2){
      $('result-title').textContent=scene===4?'✦ Хранитель искр!':scene===2?'Победа! Следующий соперник ждёт.':'Хорошая попытка. Попробуем другую стратегию?';
      $('result-text').textContent=scene===3?'Отдохни, потренируйся и используй щит перед каждым третьим ударом.':scene===4?'Ты победил Громобосса! Теперь измени игру: придумай нового соперника или обучи собственные жесты.':'Получено 30 опыта. Вернись в лабораторию: здоровье и энергия сами не восстанавливаются.';
      if(scene!==3)chirp(880);
    }
  }
  const hp=Number(read('Здоровье')),energy=Number(read('Энергия'));
  $('hint').textContent=scene===0?'Сила '+read('Сила')+' / 24 · Опыт '+read('Опыт')+' / 50 · Нажми N, чтобы дать питомцу имя.':
    scene===1?(Number(read('Ход'))?'Идёт ход…':Number(read('Счётчик ходов'))%3===2?'⚡ Соперник заряжает мощный удар. Сейчас нужен щит!':energy<8?'Мало энергии. Щит восстановит 18 энергии.':hp<35?'Здоровье на исходе: лечение стоит 20 энергии.':'Атака расходует энергию. Щит восстанавливает её. Не торопись!'):
    'Победы: '+read('Победы')+' · Уровень: '+read('Уровень');
  document.querySelectorAll('[data-key]').forEach(b=>{
    const k=b.dataset.key;
    b.disabled=Number(read('Ход'))!==0 || (k==='a'&&energy<8)||(k==='h'&&(energy<20||hp>=100))||(k==='t'&&energy<10);
  });
  const holder=$('monitors');
  holder.replaceChildren();
  for(const [name,x,y] of [['Здоровье',4,11],['Энергия',28,11],['Сила',52,11],['Уровень',74,11],['Опыт',3,29],['Здоровье врага',64,29]]){
    if(name==='Здоровье врага' && scene!==1)continue;
    const div=document.createElement('div');div.className='monitor';div.style.left=x+'%';div.style.top=y+'%';
    div.append(document.createTextNode(name));const b=document.createElement('b');b.textContent=read(name);div.append(b);holder.append(div);
  }
  const enemyHP=Number(read('Здоровье врага'));
  if(scene===1 && enemyHP<lastEnemyHP)chirp(220);
  lastEnemyHP=enemyHP;
}

// AI input. The same keyboard events are used by the visible buttons and AI.
const latch=new GestureLatch();
let hands=null,stream=null,running=false,frameBusy=false,lastPoints=null,samples=[],lastFrame=0;
const video=$('camera'), draw=$('landmarks'), ctx=draw.getContext('2d');
let cameraGeneration=0;
function stopCamera() {
  cameraGeneration++;running=false;
  stream?.getTracks().forEach(t=>t.stop());stream=null;video.srcObject=null;
  lastPoints=null;latch.reset();ctx.clearRect(0,0,draw.width,draw.height);
  $('camera-placeholder').hidden=false;$('camera-toggle').textContent='Включить камеру и ИИ';
  $('ai-status').textContent='Камера выключена. Можно играть кнопками.';
}
const connections=[[0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],[5,9],[9,10],[10,11],[11,12],[9,13],[13,14],[14,15],[15,16],[13,17],[0,17],[17,18],[18,19],[19,20]];
function onResults(result){
  if(!running)return;
  lastPoints=result.multiHandLandmarks?.[0]||null;
  draw.width=video.videoWidth||640;draw.height=video.videoHeight||480;
  ctx.clearRect(0,0,draw.width,draw.height);
  if(lastPoints){
    ctx.strokeStyle='#81f3c4';ctx.lineWidth=3;
    for(const [a,b] of connections){ctx.beginPath();ctx.moveTo(lastPoints[a].x*draw.width,lastPoints[a].y*draw.height);ctx.lineTo(lastPoints[b].x*draw.width,lastPoints[b].y*draw.height);ctx.stroke();}
    ctx.fillStyle='#c9b6ff';for(const p of lastPoints){ctx.beginPath();ctx.arc(p.x*draw.width,p.y*draw.height,4,0,Math.PI*2);ctx.fill();}
  }
  const custom=$('custom-model').checked;
  const label=custom?classifyKNN(features(lastPoints),samples):starterGesture(lastPoints);
  $('ai-status').textContent=label?'Вижу: '+LABELS[label]+'. Удержи жест, затем убери руку.':lastPoints?'Вижу руку. Покажи понятный жест ладонью к камере.':'Покажи одну руку в камеру. Хорошее освещение помогает.';
  const command=latch.update(label,performance.now());
  if(command && !$('learning').open && Number(read('Сцена'))===1 && Number(read('Ход'))===0) press({attack:'a',defend:'d',heal:'h'}[command]);
}
async function frame(now){
  if(!running)return;
  if(!frameBusy && now-lastFrame>100 && video.readyState>=2){
    frameBusy=true;lastFrame=now;
    try{await hands.send({image:video});}
    catch(error){stopCamera();$('ai-status').textContent='Не удалось обработать кадр. Попробуй Chrome и проверь поддержку WebGL. '+error.message;}
    finally{frameBusy=false;}
  }
  if(running)requestAnimationFrame(frame);
}
$('camera-toggle').onclick=async()=>{
  if(running){stopCamera();return;}
  $('camera-toggle').disabled=true;$('ai-status').textContent='Загружаем локальную нейросеть и запрашиваем доступ к камере…';
  const generation=++cameraGeneration;
  try{
    if(!navigator.mediaDevices?.getUserMedia)throw new Error('Камере нужен localhost или HTTPS. Открой игру через npm start.');
    const acquired=await navigator.mediaDevices.getUserMedia({video:{width:640,height:480,facingMode:'user'},audio:false});
    if(generation!==cameraGeneration){acquired.getTracks().forEach(t=>t.stop());return;}
    stream=acquired;video.srcObject=stream;await video.play();
    if(!hands){
      hands=new window.Hands({locateFile:file=>'vendor/hands/'+file});
      hands.setOptions({maxNumHands:1,modelComplexity:1,minDetectionConfidence:.7,minTrackingConfidence:.7});
      hands.onResults(onResults);
      await hands.initialize();
    }
    if(generation!==cameraGeneration)return;
    running=true;latch.reset();$('camera-placeholder').hidden=true;$('camera-toggle').textContent='Выключить камеру';
    $('ai-status').textContent='ИИ готов. Покажи руку!';requestAnimationFrame(frame);
  }catch(error){stopCamera();$('ai-status').textContent='Камера не запущена: '+error.message+' Играй кнопками или разреши доступ в браузере.';}
  finally{$('camera-toggle').disabled=false;}
};
document.querySelectorAll('[data-sample]').forEach(button=>button.onclick=()=>{
  const vector=features(lastPoints), label=button.dataset.sample;
  if(!running || !vector){$('training-status').textContent='Сначала включи камеру и покажи руку, чтобы появились точки.';return;}
  if(samples.filter(s=>s.label===label).length>=100){$('training-status').textContent='Достаточно: максимум 100 примеров на команду.';return;}
  samples.push({label,vector});$('count-'+label).textContent=samples.filter(s=>s.label===label).length;
  $('training-status').textContent='Пример «'+LABELS[label]+'» записан. Измени положение руки перед следующим примером.';
});
$('custom-model').onchange=()=>{
  latch.reset();
  if($('custom-model').checked && !Object.keys(LABELS).every(l=>samples.filter(s=>s.label===l).length>=5)){
    $('custom-model').checked=false;$('training-status').textContent='Нужно минимум по 5 примеров каждой из трёх команд.';
  }else $('training-status').textContent=$('custom-model').checked?'Твои примеры включены. Закрой лабораторию и проверь на новых жестах!':'Включены стартовые правила жестов.';
};
$('clear-samples').onclick=()=>{samples=[];$('custom-model').checked=false;Object.keys(LABELS).forEach(l=>$('count-'+l).textContent='0');$('training-status').textContent='Примеры очищены. Камера ничего не сохраняет.';latch.reset();};
document.addEventListener('visibilitychange',()=>{if(document.hidden && (running||stream))stopCamera();});
window.addEventListener('pagehide',stopCamera);

try{
  const response=await fetch('game/Monster_AI_Lab.sb3');
  if(!response.ok)throw new Error('Не найден файл игры');
  await vm.loadProject(await response.arrayBuffer());
  vm.start();vm.greenFlag();loaded=true;$('loading').hidden=true;
  setInterval(updateHUD,100);
}catch(error){$('loading').textContent='Не удалось загрузить игру: '+error.message+'. Выполни npm run build и открой через npm start.';console.error(error);}
// Expose read-only state for the automated classroom smoke test, never credentials.
window.monsterLab={state:()=>Object.fromEntries(Object.values(vm.runtime.getTargetForStage()?.variables||{}).filter(v=>v.type==='').map(v=>[v.name,v.value])),ready:()=>loaded};
