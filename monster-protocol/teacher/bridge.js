/* Teacher-owned adapter. Gameplay lives in visible GDevelop events, not here. */
if (!globalThis.MonsterProtocol) {
  globalThis.MonsterProtocol = (() => {
    let scene, model=null, panel=null, webcam=null, stream=null, running=false, session=0;
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
    function stop(){session++;running=false;if(stream)stream.getTracks().forEach(t=>t.stop());stream=null;if(webcam){webcam.srcObject=null;webcam.remove();webcam=null;}set('AICommand',0);resetGate();status('Камера выключена. Кнопки игры доступны.');}
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
    async function start(){
      if(!model){
        status('Загружаем встроенную модель цветных карточек…');
        try{await demoModel();}catch(e){status('Не удалось загрузить встроенную модель: '+e.message);return;}
      }
      stop();const token=session;status('Разреши доступ к камере…');
      try{
        if(!navigator.mediaDevices?.getUserMedia)throw Error('Камере нужен localhost или HTTPS. Запусти START_WINDOWS.bat из распакованной папки.');
        const acquired=await navigator.mediaDevices.getUserMedia({video:{width:320,height:240,facingMode:'user'},audio:false});
        if(token!==session){acquired.getTracks().forEach(t=>t.stop());return;}
        stream=acquired;webcam=document.createElement('video');webcam.id='mp-video';webcam.autoplay=true;webcam.muted=true;webcam.playsInline=true;webcam.style.cssText='width:240px;border-radius:14px;transform:scaleX(-1)';webcam.srcObject=stream;
        document.getElementById('mp-video-box').append(webcam);await webcam.play();
        if(token!==session)return;running=true;resetGate();
        while(running&&token===session){
          const predictions=await model.predict(webcam,false);if(token!==session)break;
          const top=predictions.reduce((a,b)=>a.probability>b.probability?a:b);
          const command=gate(predictions);
          status(top.className+' · '+Math.round(top.probability*100)+'%'+(armed?' · готов':' · убери карточку / вернись в IDLE'));
          if(command&&scene.getName()==='Arena')set('AICommand',command);
          await new Promise(r=>setTimeout(r,100));
        }
      }catch(e){if(token===session){stop();const help={NotAllowedError:'Разреши камеру в настройках рядом с адресом браузера.',NotFoundError:'Камера не найдена. Проверь подключение.',NotReadableError:'Камера занята или недоступна. Закрой видеозвонки и попробуй снова.'};status(help[e.name]||('Камера или модель: '+e.message));}}
    }
    function camera(){const root=shell('Teachable Machine → команды игры');
      root.innerHTML='<p>Быстрый старт: нажми <b>«Включить камеру»</b>. Встроенная модель цветных карточек загрузится сама.</p><p>Для своей модели: 4 класса <b>ATTACK · SHIELD · HEAL · IDLE</b>. Добавь <b>model.json, metadata.json и все веса</b> из экспорта TensorFlow.js — вместе или по очереди. Выбранные файлы останутся в списке.</p><input id="mp-model-files" type="file" multiple accept=".json,.bin"><p><button id="mp-demo">Модель цветных карточек</button> <button id="mp-start">Включить камеру</button> <button id="mp-stop">Выключить камеру</button></p><p>Красная карточка — атака, синяя — щит, зелёная — лечение. Нейтральный серый фон — IDLE. Это модель цвета, а не распознавание рук. Удержи карточку 0,5 с, затем убери её.</p><div id="mp-video-box"></div><p id="mp-battle-state" style="padding:12px;background:#171122;border-radius:10px"></p><p>Оставь окно открытым на арене. Для перехода к кнопкам нажми «Закрыть»: камера выключится. Видео и файлы обрабатываются в этом браузере.</p>';
      const collected=new Map();
      const selection=document.createElement('p');selection.id='mp-selected-files';selection.textContent='Своя модель: файлы пока не добавлены.';root.querySelector('#mp-model-files').after(selection);
      root.querySelector('#mp-model-files').onchange=async e=>{
        for(const file of e.target.files)collected.set(file.name,file);
        selection.textContent='Добавлены: '+[...collected.keys()].join(', ');
        try{
          const files=[...collected.values()],missing=missingFiles(files);
          if(missing.length){status('Файлы добавлены. Теперь добавь: '+missing.join(', ')+', затем файл весов из той же папки. Можно выбирать по очереди.');return;}
          status('Проверяем комплект модели…');await loadLocal(files);
        }catch(err){status('Модель пока не загружена: '+err.message+' Добавь недостающий файл, уже выбранные сохранены.');}
      };
      root.querySelector('#mp-demo').onclick=async()=>{try{status('Загружаем локальную модель…');await demoModel();}catch(e){status('Модель не загружена: '+e.message);}};
      root.querySelector('#mp-start').onclick=start;root.querySelector('#mp-stop').onclick=stop;
      status(model?'Модель готова. Можно включить камеру.':'Для быстрого старта нажми «Включить камеру»: встроенная модель карточек загрузится автоматически. Для своей модели добавь model.json, metadata.json и веса — вместе или по очереди.');
    }
    const fields=['Name','Health','Energy','Strength','XP','Level','Wins','Round',...['Body','Eyes','Mouth','Arms','Legs','Horns','Nose','Ears','Tail','Wings'].map(x=>x+'Variant')];
    // Optional teacher-owned presentation. It never writes gameplay variables.
    let visualScene=null,homes=[],previous=null,animation=null,fx=null;
    function presentation(next){
      const now=performance.now();
      if(visualScene!==next){
        fx?.remove();fx=document.createElement('canvas');fx.id='mp-effects';fx.width=1280;fx.height=800;
        fx.style.cssText='position:fixed;pointer-events:none;z-index:100';document.body.append(fx);
        visualScene=next;animation=null;previous=null;homes=[];
        for(const name of ['MonsterBody','MonsterEyes','MonsterMouth','MonsterArms','MonsterLegs','MonsterHorns','MonsterNose','MonsterEars','MonsterTail','MonsterWings','Rival'])
          for(const object of next.getObjects(name))homes.push({object,x:object.getX(),y:object.getY(),rival:name==='Rival'});
      }
      const current={hp:get('Health'),enemy:get('EnemyHP'),energy:get('Energy'),xp:get('XP')};
      if(previous){
        const hit=next.getName()==='Arena'&&current.enemy<previous.enemy;
        const hurt=next.getName()==='Arena'&&current.hp<previous.hp;
        const heal=current.hp>previous.hp||current.energy>previous.energy;
        if(hit||hurt||heal||current.xp>previous.xp)animation={start:now,hit,hurt,heal,damage:previous.enemy-current.enemy,taken:previous.hp-current.hp};
      }
      previous=current;
      const bounds=document.querySelector('canvas:not(#mp-effects)')?.getBoundingClientRect();
      if(!bounds)return;
      Object.assign(fx.style,{left:bounds.left+'px',top:bounds.top+'px',width:bounds.width+'px',height:bounds.height+'px'});
      const ctx=fx.getContext('2d');ctx.clearRect(0,0,1280,800);
      const elapsed=animation?(now-animation.start)/1000:5;
      const pulse=(start,duration)=>elapsed>start&&elapsed<start+duration?Math.sin((elapsed-start)/duration*Math.PI):0;
      const attack=pulse(0,.32),retaliate=pulse(.4,.32),jump=pulse(0,.5);
      if(animation)for(const h of homes){
        const dx=animation?(h.rival?(animation.hurt?-55*retaliate:0):(animation.hit?55*attack:0)):0;
        const dy=animation&&!h.rival&&next.getName()==='Lab'?-22*jump:0;
        h.object.setPosition(h.x+dx,h.y+dy);
      }
      if(!animation)return;
      if(elapsed>1.15){animation=null;return;}
      function orb(x,y,color,r=18){ctx.fillStyle=color;ctx.shadowColor=color;ctx.shadowBlur=25;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();ctx.shadowBlur=0;}
      if(animation.hit&&elapsed<.32){orb(420+elapsed/.32*480,370,'#baf5d2');}
      if(animation.hurt&&elapsed>.4&&elapsed<.72){orb(930-(elapsed-.4)/.32*590,370,'#ffbca1');}
      ctx.font='bold 34px system-ui';ctx.textAlign='center';
      if(animation.hit){ctx.fillStyle='#ffe3ab';ctx.fillText('−'+animation.damage,970,280-elapsed*35);}
      if(animation.hurt&&elapsed>.4){ctx.fillStyle='#ffbca1';ctx.fillText('−'+animation.taken+' HP',330,280-elapsed*35);}
      if(animation.heal){ctx.strokeStyle='#baf5d2';ctx.lineWidth=6;ctx.beginPath();ctx.arc(330,383,110+jump*15,0,Math.PI*2);ctx.stroke();}
    }
    const limits={Health:[0,100],Energy:[0,100],Strength:[10,30],XP:[0,100000],Level:[1,33334],Wins:[0,3],Round:[1,3],BodyVariant:[0,5],EyesVariant:[0,7],MouthVariant:[0,5]};
    function save(){try{const values={};for(const n of fields)values[n]=n==='Name'?state().get(n).getAsString():get(n);localStorage.setItem('monster-protocol-v1',JSON.stringify({version:1,values}));set('Message','Сохранено в этом браузере. Для переноса копируй проект; эта запись не передаётся автоматически.');}catch{set('Message','Браузер запретил локальное сохранение. Сохрани проект в GDevelop.');}}
    function load(){try{const data=JSON.parse(localStorage.getItem('monster-protocol-v1'));if(data?.version!==1||!data.values)throw Error('Нет сохранения');for(const n of fields){const v=data.values[n];if(n==='Name'){if(typeof v!=='string'||!v.trim()||v.length>24)throw Error('Имя');}else{const [lo,hi]=limits[n]||[0,3];if(!Number.isFinite(v)||!Number.isInteger(v)||v<lo||v>hi)throw Error(n);}}for(const n of fields)set(n,data.values[n]);set('Message','Сохранение загружено.');}catch{set('Message','Корректное сохранение не найдено. Текущий монстр не изменён.');}}
    function tick(next){if(scene&&scene!==next&&panel)close();scene=next;
      presentation(next);
      const battle=document.getElementById('mp-battle-state');if(battle)battle.textContent='Раунд '+get('Round')+' / 3 · Соперник: '+get('EnemyHP')+' HP · Ты: '+get('Health')+' HP · Энергия: '+get('Energy')+' · '+state().get('Message').getAsString();
      for(const [key,fn] of [['NamePanel',rename],['AIPanel',camera],['SaveRequest',save],['LoadRequest',load]])if(get(key)){set(key,0);fn();}
    }
    window.addEventListener('pagehide',()=>{if(scene)stop();});
    return {tick,gate,resetGate,stop,close,loadLocal,demoModel,getScene:()=>scene,getModel:()=>model};
  })();
}
runtimeScene.getGame().enableMetrics(false);
globalThis.MonsterProtocol.tick(runtimeScene);
