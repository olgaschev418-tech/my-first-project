/* Teacher-owned adapter. Gameplay lives in visible GDevelop events, not here. */
if (!globalThis.MonsterProtocol) {
  globalThis.MonsterProtocol = (() => {
    let scene, model=null, panel=null, webcam=null, stream=null, running=false, session=0, handEngine=null, handReady=null, frameTask=Promise.resolve();
    let candidate='', since=0, neutralSince=0, armed=true, lastCommand=-Infinity;
    const allowed=['ATTACK','SHIELD','HEAL','IDLE'];
    const state=()=>scene.getGame().getVariables();
    const set=(n,v)=>typeof v==='string'?state().get(n).setString(v):state().get(n).setNumber(v);
    const get=n=>state().get(n).getAsNumber();
    const status=s=>{const el=document.getElementById('mp-status');if(el)el.textContent=s;};
    function resource(name) {
      const data=scene.getGame().getGameData().resources.resources.find(r=>r.name==='assets/'+name);
      if (!data) throw Error('Ресурс не найден: '+name);
      return scene.getGame().getResourceLoader().getFullUrl(data.file);
    }
    const loadScript=(name,globalName)=>new Promise((resolve,reject)=>{
      if(globalThis[globalName])return resolve();
      const s=document.createElement('script');s.src=resource(name);s.onload=resolve;s.onerror=()=>reject(Error('Не загружена локальная библиотека '+name));document.head.append(s);
    });
    async function libraries(){await loadScript('tf.min.js','tf');await loadScript('tm.min.js','tmImage');}
    function resetGate(){candidate='';since=0;neutralSince=0;armed=true;lastCommand=-Infinity;}
    function gate(predictions,now=performance.now()) {
      const top=predictions.reduce((a,b)=>a.probability>b.probability?a:b,{className:'IDLE',probability:0});
      const label=top.className;
      if(top.probability<.85 || label==='IDLE') {
        candidate='';
        if(!neutralSince)neutralSince=now;
        if(now-neutralSince>=400)armed=true;
        return 0;
      }
      neutralSince=0;
      if(candidate!==label){candidate=label;since=now;return 0;}
      if(!armed || now-since<500 || now-lastCommand<1500)return 0;
      armed=false;lastCommand=now;
      return {ATTACK:1,SHIELD:2,HEAL:3}[label]||0;
    }
    function stop(){session++;running=false;if(stream)stream.getTracks().forEach(t=>t.stop());stream=null;if(webcam){webcam.srcObject=null;webcam.remove();webcam=null;}set('AICommand',0);resetGate();const retry=document.getElementById('mp-retry');if(retry)retry.hidden=false;status('Камера выключена. Кнопки игры доступны.');}
    function close(){stop();if(panel)panel.remove();panel=null;}
    function shell(title){
      close();panel=document.createElement('div');panel.id='mp-overlay';panel.setAttribute('role','dialog');panel.setAttribute('aria-label',title);
      panel.style.cssText='position:fixed;inset:0;z-index:99999;background:#100b20dd;display:grid;place-items:center;font:16px system-ui;color:#fff8ed';
      panel.innerHTML='<section style="background:#282039;border:1px solid #655276;border-radius:24px;padding:26px;width:min(680px,86vw);max-height:86vh;overflow:auto"><button id="mp-close" style="float:right">Закрыть ×</button><h2></h2><div id="mp-content"></div><p id="mp-status" role="status"></p></section>';
      panel.querySelector('h2').textContent=title;
      // The canvas must not receive clicks made on a modal control.
      for(const event of ['mousedown','mouseup','pointerdown','pointerup','touchstart','touchend'])panel.addEventListener(event,e=>e.stopPropagation());
      document.body.append(panel);panel.querySelector('#mp-close').onclick=close;
      return panel.querySelector('#mp-content');
    }
    function rename(){const root=shell('Имя твоего монстра');root.innerHTML='<label>Имя (до 24 символов)<br><input id="mp-name" maxlength="24" style="font:24px system-ui;padding:10px;margin:16px 0"></label><br><button id="mp-name-save">Готово</button>';
      root.querySelector('input').value=state().get('Name').getAsString();root.querySelector('button').onclick=()=>{const n=root.querySelector('input').value.trim();if(n){set('Name',n);close();}};
    }
    function validateLabels(m){const labels=m.getClassLabels();if(labels.length!==4||!allowed.every(n=>labels.includes(n)))throw Error('Нужны ровно 4 класса: ATTACK, SHIELD, HEAL, IDLE. Проверь регистр.');}
    async function replaceModel(next){try{validateLabels(next);}catch(e){next.model.dispose();throw e;}stop();if(model)model.model.dispose();model=next;status('Модель готова. Включи камеру; команды действуют только на арене.');}
    function missingFiles(files){
      const names=Array.from(files,f=>f.name);
      return ['model.json','metadata.json'].filter(n=>!names.includes(n));
    }
    async function loadLocal(files){const f=Array.from(files),find=n=>f.find(x=>x.name===n);const missing=missingFiles(f);if(missing.length)throw Error('Не хватает: '+missing.join(', ')+'. Нужен распакованный экспорт TensorFlow.js из Teachable Machine.');
      const meta=JSON.parse(await find('metadata.json').text());const spec=JSON.parse(await find('model.json').text());
      if(!Array.isArray(spec.weightsManifest)||!spec.modelTopology)throw Error('Этот JSON не похож на модель TensorFlow.js. game.json — проект GDevelop, а не файл ИИ.');
      const names=spec.weightsManifest.flatMap(g=>g.paths);const weights=names.map(n=>{const file=find(n);if(!file)throw Error('Не найден файл весов '+n);return file;});
      await libraries();
      const layers=await tf.loadLayersModel(tf.io.browserFiles([find('model.json'),...weights]));
      await replaceModel(new tmImage.CustomMobileNet(layers,meta));
    }
    async function demoModel(){await libraries();const response=await fetch(resource('demo-bundle.json'));if(!response.ok)throw Error('Не найден локальный комплект модели');const b=await response.json();const weightData=Uint8Array.from(atob(b.weightData),c=>c.charCodeAt(0)).buffer;const layers=await tf.loadLayersModel(tf.io.fromMemory(b.modelTopology,b.weightSpecs,weightData));await replaceModel(new tmImage.CustomMobileNet(layers,b.metadata));}
    // Same gesture vocabulary as the previous game. MediaPipe finds the hand;
    // readable distance rules turn its 21 landmarks into three commands.
    function handLabel(points){
      if(!points||points.length!==21)return 'IDLE';
      const distance=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y,(a.z||0)-(b.z||0));
      const [index,middle,ring,pinky]=[8,12,16,20].map(tip=>distance(points[tip],points[0])>distance(points[tip-2],points[0])*1.15);
      if(!index&&!middle&&!ring&&!pinky)return 'ATTACK';
      if(index&&middle&&ring&&pinky)return 'SHIELD';
      if(index&&middle&&!ring&&!pinky)return 'HEAL';
      return 'IDLE';
    }
    const links=[[0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],[5,9],[9,10],[10,11],[11,12],[9,13],[13,14],[14,15],[15,16],[13,17],[0,17],[17,18],[18,19],[19,20]];
    function deliver(label){
      const ready=scene.getName()==='Arena'&&scene.getVariables().get('Phase').getAsNumber()===0&&!document.getElementById('mp-learning')?.open;
      // Never accumulate a command during the enemy turn or outside the arena.
      const command=gate([{className:label,probability:1}]);
      if(command&&ready)set('AICommand',command);
    }
    function handResults(result){
      const points=result.multiHandLandmarks?.[0]||null;
      const canvas=document.getElementById('mp-hand-draw');
      if(canvas){const ctx=canvas.getContext('2d');ctx.clearRect(0,0,canvas.width,canvas.height);
        if(points){ctx.strokeStyle='#baf5d2';ctx.lineWidth=2;
          for(const [a,b] of links){ctx.beginPath();ctx.moveTo(points[a].x*canvas.width,points[a].y*canvas.height);ctx.lineTo(points[b].x*canvas.width,points[b].y*canvas.height);ctx.stroke();}
          ctx.fillStyle='#bca7ff';for(const p of points){ctx.beginPath();ctx.arc(p.x*canvas.width,p.y*canvas.height,2.5,0,Math.PI*2);ctx.fill();}
        }
      }
      const label=handLabel(points);deliver(label);
      const names={ATTACK:'Кулак — атака',SHIELD:'Ладонь — щит',HEAL:'Два пальца — лечение'};
      status(!points?'Покажи одну руку целиком':label==='IDLE'?'Поверни ладонь к камере':names[label]+(armed?' · удержи жест':' · убери руку'));
    }
    async function hands(){
      if(!handReady){handReady=(async()=>{
        await loadScript('hands.js','Hands');
        handEngine=new Hands({locateFile:name=>resource(name)});
        handEngine.setOptions({maxNumHands:1,modelComplexity:1,minDetectionConfidence:.7,minTrackingConfidence:.7});
        await handEngine.initialize();return handEngine;
      })().catch(e=>{handReady=null;throw e;});}
      return handReady;
    }
    async function start(){
      stop();const retry=document.getElementById('mp-retry');if(retry)retry.hidden=true;const token=session;status('Разреши камеру…');
      try{
        if(!navigator.mediaDevices?.getUserMedia)throw Error('Запусти игру через START_WINDOWS.bat: камере нужен localhost или HTTPS.');
        const acquired=await navigator.mediaDevices.getUserMedia({video:{width:640,height:480,facingMode:'user'},audio:false});
        if(token!==session){acquired.getTracks().forEach(t=>t.stop());return;}
        stream=acquired;webcam=document.createElement('video');webcam.id='mp-video';webcam.autoplay=true;webcam.muted=true;webcam.playsInline=true;
        webcam.style.cssText='display:block;width:100%;height:150px;object-fit:contain;transform:scaleX(-1);background:#100b20;border-radius:10px';webcam.srcObject=stream;
        document.getElementById('mp-video-box').prepend(webcam);await webcam.play();
        if(token!==session)return;
        let engine=null;
        if(!model){status('Загружаем распознавание руки…');engine=await hands();}
        if(token!==session)return;
        running=true;resetGate();
        if(engine){await frameTask.catch(()=>{});if(token!==session)return;engine.onResults(result=>{if(running&&token===session)handResults(result);});}
        while(running&&token===session){
          if(engine){frameTask=engine.send({image:webcam});await frameTask;}
          else{
            const predictions=await model.predict(webcam,false);if(token!==session)break;
            const top=predictions.reduce((a,b)=>a.probability>b.probability?a:b);
            deliver(top.probability>=.85?top.className:'IDLE');status('Своя модель: '+top.className+(armed?'':' · убери руку'));
          }
          await new Promise(r=>setTimeout(r,100));
        }
      }catch(e){if(token===session){stop();const help={NotAllowedError:'Разреши камеру рядом с адресом браузера.',NotFoundError:'Камера не найдена.',NotReadableError:'Камера занята. Закрой видеозвонок.'};status(help[e.name]||('Не удалось включить камеру: '+e.message));}}
    }
    function camera(){
      if(panel?.id==='mp-camera'){close();return;}
      close();panel=document.createElement('section');panel.id='mp-camera';panel.setAttribute('role','region');panel.setAttribute('aria-label','Камера: управление рукой');
      panel.style.cssText='position:fixed;right:12px;top:145px;width:220px;max-width:85vw;max-height:75vh;overflow:auto;box-sizing:border-box;z-index:99999;background:#282039f5;color:#fff8ed;border:1px solid #bca7ff;border-radius:16px;padding:10px;box-shadow:0 8px 32px #0007;font:13px system-ui';
      panel.innerHTML='<header id="mp-drag" style="display:flex;align-items:center;justify-content:space-between;cursor:move;touch-action:none;padding:0 0 8px"><b>Управление рукой</b><button id="mp-close" aria-label="Выключить камеру" style="font:20px system-ui;background:transparent;color:inherit;border:0;cursor:pointer">×</button></header><div id="mp-video-box" style="position:relative;min-height:50px"><canvas id="mp-hand-draw" width="200" height="150" style="position:absolute;inset:0;width:100%;height:150px;transform:scaleX(-1);pointer-events:none"></canvas></div><p style="display:flex;justify-content:space-between;font-size:11px;margin:8px 0"><span>✊ Атака</span><span>✋ Щит</span><span>✌ Лечение</span></p><p id="mp-status" role="status" style="min-height:30px;margin:6px 0;color:#baf5d2"></p><button id="mp-retry" style="font:inherit">Перезапустить камеру</button><details id="mp-learning" style="margin-top:8px;font-size:11px"><summary>Своя модель для занятия</summary><p>Необязательно: экспорт Teachable Machine с классами ATTACK, SHIELD, HEAL, IDLE. Добавь model.json, metadata.json и веса.</p><input id="mp-model-files" type="file" multiple accept=".json,.bin" style="width:100%"><p id="mp-selected-files"></p><button id="mp-hands">Вернуть жесты руки</button></details>';
      for(const event of ['mousedown','mouseup','pointerdown','pointerup','touchstart','touchend'])panel.addEventListener(event,e=>e.stopPropagation());
      document.body.append(panel);panel.querySelector('#mp-close').onclick=close;panel.querySelector('#mp-retry').onclick=start;
      const header=panel.querySelector('#mp-drag');let drag=null;
      header.onpointerdown=e=>{if(e.target.closest('button'))return;const b=panel.getBoundingClientRect();drag={x:e.clientX-b.left,y:e.clientY-b.top};header.setPointerCapture(e.pointerId);};
      header.onpointermove=e=>{if(!drag)return;panel.style.right='auto';panel.style.left=Math.max(0,Math.min(innerWidth-panel.offsetWidth,e.clientX-drag.x))+'px';panel.style.top=Math.max(0,Math.min(innerHeight-panel.offsetHeight,e.clientY-drag.y))+'px';};
      header.onpointerup=header.onpointercancel=()=>{drag=null;};
      const collected=new Map();
      panel.querySelector('#mp-model-files').onchange=async e=>{
        for(const f of e.target.files)collected.set(f.name,f);
        const selection=document.getElementById('mp-selected-files');selection.textContent='Добавлены: '+[...collected.keys()].join(', ');
        try{await loadLocal([...collected.values()]);status('Модель готова. Закрой эти настройки и нажми «Перезапустить камеру».');}catch(err){status(err.message);}
      };
      panel.querySelector('#mp-hands').onclick=()=>{stop();if(model)model.model.dispose();model=null;panel.querySelector('details').open=false;start();};
      start();
    }
    const fields=['Name','Health','Energy','Strength','XP','Level','Wins','Round','Gold','RoomStyle','Badges',...['Body','Eyes','Mouth','Arms','Legs','Horns','Nose','Ears','Tail','Wings'].map(x=>x+'Variant')];
    const limits={Gold:[0,100000],RoomStyle:[0,2],Badges:[0,3],Health:[0,100],Energy:[0,100],Strength:[10,30],XP:[0,100000],Level:[1,33334],Wins:[0,3],Round:[1,3],BodyVariant:[0,5],EyesVariant:[0,7],MouthVariant:[0,5]};
    function save(){try{const values={};for(const n of fields)values[n]=n==='Name'?state().get(n).getAsString():get(n);localStorage.setItem('monster-protocol-v1',JSON.stringify({version:1,values}));set('Message','Сохранено в этом браузере. Для переноса копируй проект; эта запись не передаётся автоматически.');}catch{set('Message','Браузер запретил локальное сохранение. Сохрани проект в GDevelop.');}}
    function load(){try{const data=JSON.parse(localStorage.getItem('monster-protocol-v1'));if(data?.version!==1||!data.values)throw Error('Нет сохранения');for(const n of fields){const v=data.values[n]===undefined&&['Gold','RoomStyle','Badges'].includes(n)?get(n):data.values[n];data.values[n]=v;if(n==='Name'){if(typeof v!=='string'||!v.trim()||v.length>24)throw Error('Имя');}else{const [lo,hi]=limits[n]||[0,3];if(!Number.isFinite(v)||!Number.isInteger(v)||v<lo||v>hi)throw Error(n);}}for(const n of fields)set(n,data.values[n]);set('Message','Сохранение загружено.');}catch{set('Message','Корректное сохранение не найдено. Текущий монстр не изменён.');}}
    function tick(next){if(scene&&scene!==next){if(panel&&panel.id!=='mp-camera')close();resetGate();}scene=next;
      const cameraLabel=scene.getObjects('CameraLabel')[0];if(cameraLabel)cameraLabel.setString(panel?.id==='mp-camera'?'Выключить камеру':'Включить камеру');
      const battle=document.getElementById('mp-battle-state');if(battle)battle.textContent='Раунд '+get('Round')+' / 3 · Соперник: '+get('EnemyHP')+' HP · Ты: '+get('Health')+' HP · Энергия: '+get('Energy')+' · '+state().get('Message').getAsString();
      for(const [key,fn] of [['NamePanel',rename],['AIPanel',camera],['SaveRequest',save],['LoadRequest',load]])if(get(key)){set(key,0);fn();}
    }
    window.addEventListener('pagehide',()=>{if(scene)stop();});
    return {tick,gate,resetGate,stop,close,loadLocal,demoModel,handLabel,getCameraState:()=>({running,mode:model?'custom':'hands'}),getScene:()=>scene,getModel:()=>model};
  })();
}
runtimeScene.getGame().enableMetrics(false);
globalThis.MonsterProtocol.tick(runtimeScene);
