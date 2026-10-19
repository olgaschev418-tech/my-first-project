/* Ready-made visual/audio kit. All health, energy, rewards and turn rules are native events. */
if (!globalThis.MonsterWorld) {
  globalThis.MonsterWorld = (() => {
    let scene,ctx,music=null,track='',audioContext=null,unlocked=false;
    const events=[];
    const record=(type,detail={})=>{events.push({type,...detail});if(events.length>40)events.shift();};
    const vars=()=>scene.getGame().getVariables();
    const num=n=>vars().get(n).getAsNumber();
    const sv=n=>scene.getVariables().get(n).getAsNumber();
    const resource=name=>{const r=scene.getGame().getGameData().resources.resources.find(r=>r.name==='assets/'+name);return r?scene.getGame().getResourceLoader().getFullUrl(r.file):null;};
    function syncMusic(){
      if(!scene||!unlocked)return;
      const desired=scene.getName()==='Arena'?'battle-loop.wav':'home-loop.wav';
      if(!music||desired!==track){if(music)music.pause();const url=resource(desired);if(!url)return;music=new Audio(url);music.loop=true;music.volume=.25;track=desired;}
      music.volume=Math.max(0,Math.min(1,num('MusicVolume')/100));
      if(num('MusicOn')===1){if(music.paused)music.play().catch(()=>{});}else music.pause();
    }
    document.addEventListener('pointerdown',()=>{
      if(!scene)return;unlocked=true;
      const AudioCtx=globalThis.AudioContext||globalThis.webkitAudioContext;
      if(AudioCtx&&!audioContext)audioContext=new AudioCtx();
      if(audioContext?.state==='suspended')audioContext.resume().catch(()=>{});
      syncMusic();
    },{capture:true});
    document.addEventListener('visibilitychange',()=>{if(document.hidden){if(music)music.pause();}else syncMusic();});
    function sound(kind){
      if(!audioContext||audioContext.state!=='running'||num('MusicOn')!==1)return;
      const tones={attack:[392,784],hit:[120,65],good:[523,659,784],shield:[330,494],sleep:[262,330],error:[160,120]};
      (tones[kind]||tones.good).forEach((f,i)=>{const osc=audioContext.createOscillator(),gain=audioContext.createGain(),at=audioContext.currentTime+i*.07;osc.type=kind==='hit'?'triangle':'sine';osc.frequency.setValueAtTime(f,at);gain.gain.setValueAtTime(0,at);gain.gain.linearRampToValueAtTime(.075,at+.015);gain.gain.exponentialRampToValueAtTime(.001,at+.23);osc.connect(gain);gain.connect(audioContext.destination);osc.start(at);osc.stop(at+.25);});
    }
    function emit(type,x,y,count=12,color=null){
      for(let i=0;i<count&&ctx.particles.length<100;i++){
        const o=scene.createObject(type);if(!o)continue;
        const angle=Math.random()*Math.PI*2,speed=45+Math.random()*130,size=10+Math.random()*15;
        o.setPosition(x,y);o.setSize(size,size);o.setZOrder(80);if(color&&o.setColor)o.setColor(color);
        ctx.particles.push({o,x,y,vx:Math.cos(angle)*speed,vy:Math.sin(angle)*speed-90,age:0,life:.7+Math.random()*.6,spin:Math.random()*180-90});
      }
    }
    function floating(text,x,y,color){const o=scene.createObject('FloatingNumber');if(!o)return;o.setString(text);o.setPosition(x,y);o.setZOrder(85);o.setColor(color);ctx.particles.push({o,x,y,vx:0,vy:-48,age:0,life:1.1,spin:0});}
    function bolt(){const o=scene.createObject('Projectile');if(!o)return;o.setSize(65,65);o.setZOrder(50);ctx.particles.push({o,projectile:true,age:0,life:.3});}
    function base(o){return {o,x:o.getX(),y:o.getY(),w:o.getWidth(),h:o.getHeight(),angle:o.getAngle()};}
    function initialize(next){
      scene=next;const objects=[];for(const cat of ['Body','Eyes','Mouth','Arms','Legs','Horns','Nose','Ears','Tail','Wings'])for(const o of scene.getObjects('Monster'+cat))objects.push({...base(o),cat});
      const body=objects.find(x=>x.cat==='Body');
      ctx={time:0,parts:objects,rival:scene.getObjects('Rival').map(base),heroX:body?body.x+body.w/2:400,heroY:body?body.y+body.h/2:400,particles:[],lastHP:num('Health'),lastEnemy:num('EnemyHP'),lastPhase:0,lastRound:num('Round'),react:0,heroHurt:0,enemyHurt:0,emission:0,barHealth:num('Health'),barEnergy:num('Energy'),barEnemy:num('EnemyHP'),buttons:[]};
      const buttonNames=['Music','Feed','Train','Rest','Battle','Decor','Attack','Shield','Heal','Creator','Camera','Retreat','Again','Home','Random','Rename','Save','Load','ToLab'];
      for(const o of scene.getAdhocListOfAllInstances())if(buttonNames.includes(o.getName())||/^(Body|Eyes|Mouth|Arms|Legs|Horns|Nose|Ears|Tail|Wings)(Next|Prev)$/.test(o.getName()))ctx.buttons.push(base(o));
      if(scene.getName()==='Final'){emit('ParticleSpark',870,300,45);sound('good');}
      record('scene',{name:scene.getName()});syncMusic();
    }
    function tick(next){
      if(scene!==next)initialize(next);
      const dt=Math.min(.05,Math.max(0,scene.getElapsedTime()/1000));ctx.time+=dt;ctx.react=Math.max(0,ctx.react-dt);ctx.heroHurt=Math.max(0,ctx.heroHurt-dt);ctx.enemyHurt=Math.max(0,ctx.enemyHurt-dt);
      const name=scene.getName(),phase=sv('Phase'),turn=sv('TurnTime'),kind=sv('ActionKind');
      const fx=num('VisualFX');if(fx){vars().get('VisualFX').setNumber(0);ctx.react=.9;
        if(fx===1){emit('ParticleHeart',ctx.heroX,ctx.heroY,13);floating('+20 энергии',ctx.heroX-80,ctx.heroY-100,'186;245;210');sound('good');}
        if(fx===2){emit('ParticleSpark',ctx.heroX,ctx.heroY,18);floating('+4 силы',ctx.heroX-60,ctx.heroY-110,'255;221;140');sound('good');}
        if(fx===3){emit('ParticleBubble',ctx.heroX,ctx.heroY,12);floating('Z z z…',ctx.heroX-40,ctx.heroY-120,'202;190;255');sound('sleep');}
        if(fx===4){emit('ParticleSpark',ctx.heroX,ctx.heroY-50,36);sound('good');}
        if(fx===5){emit('ParticleHeart',ctx.heroX,ctx.heroY,12);sound('good');}
        if(fx===6){floating('Нужно больше энергии',ctx.heroX-120,ctx.heroY-110,'255;191;165');sound('error');}
        record('reaction',{kind:fx});
      }
      if(num('PetRequest')){vars().get('PetRequest').setNumber(0);ctx.react=1.2;emit('ParticleHeart',ctx.heroX,ctx.heroY-70,18);sound('good');record('pet');}
      if(name==='Arena'&&phase===1&&ctx.lastPhase!==1){
        if(kind===1){bolt();sound('attack');record('player-attack');}
        if(kind===2){emit('ParticleBubble',ctx.heroX,ctx.heroY,15);sound('shield');record('shield');}
        if(kind===3)record('heal');
      }
      if(name==='Arena'&&phase===3&&ctx.lastPhase!==3){emit('ParticleSpark',970,365,12);sound('attack');record('enemy-counterattack');}
      const hp=num('Health'),enemy=num('EnemyHP');
      if(hp<ctx.lastHP){ctx.heroHurt=.28;emit('ParticleSpark',ctx.heroX,ctx.heroY,13);floating('−'+(ctx.lastHP-hp),ctx.heroX,ctx.heroY-80,'255;157;170');sound('hit');record('player-damage',{amount:ctx.lastHP-hp});}
      if(hp>ctx.lastHP&&name==='Arena')floating('+'+(hp-ctx.lastHP),ctx.heroX,ctx.heroY-90,'186;245;210');
      if(enemy<ctx.lastEnemy&&name==='Arena'){ctx.enemyHurt=.28;emit('ParticleSpark',965,380,20);floating('−'+(ctx.lastEnemy-enemy),960,300,'255;220;151');sound('hit');record('enemy-damage',{amount:ctx.lastEnemy-enemy});}
      ctx.lastHP=hp;ctx.lastEnemy=enemy;ctx.lastPhase=phase;
      const t=ctx.time,breath=1+.018*Math.sin(t*3),blink=(t%4.3)>.12&&(t%4.3)<.25;
      let lunge=0,jump=0;
      if(name==='Arena'&&kind===1&&phase>0&&phase<4)lunge=100*Math.sin(Math.PI*Math.min(1,turn/.62));
      if(ctx.react>0)jump=-Math.abs(Math.sin(ctx.react*10))*num('ReactionHeight');
      const shake=ctx.heroHurt>0?Math.sin(ctx.heroHurt*120)*9:0;
      for(const b of ctx.parts){
        const sx=breath,sy=1-.016*Math.sin(t*3);b.o.setSize(b.w*sx,b.h*sy*(b.cat==='Eyes'&&blink?.08:1));
        let x=ctx.heroX+(b.x-ctx.heroX)*sx+lunge+shake,y=ctx.heroY+(b.y-ctx.heroY)*sy+Math.sin(t*2.4)*num('IdleAmplitude')+jump;
        if(b.cat==='Eyes'&&blink)y+=b.h*.45;
        b.o.setPosition(x,y);b.o.setAngle(b.angle+(b.cat==='Arms'?Math.sin(t*3)*2:0));
        b.o.setOpacity(ctx.heroHurt>0&&Math.sin(ctx.heroHurt*80)>0?135:255);
      }
      for(const b of ctx.rival){
        let x=b.x,y=b.y+Math.sin(t*2.1)*6,angle=Math.sin(t*1.7)*2;
        if(phase===3)x-=140*Math.sin(Math.PI*Math.min(1,Math.max(0,(turn-.68)/.46)));
        b.o.setPosition(x,y);b.o.setAngle(angle);b.o.setSize(b.w*(1+.022*Math.sin(t*2.1)),b.h*(1-.018*Math.sin(t*2.1)));
        b.o.setOpacity(phase===5?Math.max(0,220-turn*350):ctx.enemyHurt>0?145:255);
      }
      const halo=scene.getObjects('ShieldHalo')[0];if(halo){if(name==='Arena'&&kind===2&&phase>0&&phase<5){halo.setPosition(ctx.heroX-85,ctx.heroY-60);halo.setSize(170,170);halo.setOpacity(180+50*Math.sin(t*8));}else halo.setPosition(-400,-400);}
      // Native scene sprites show the values; only their visual interpolation is here.
      for(const [field,key,max]of [['Health','barHealth',100],['Energy','barEnergy',100],['EnemyHealth','barEnemy',40+20*num('Round')]]){
        const target=field==='EnemyHealth'?enemy:num(field);ctx[key]+=(target-ctx[key])*Math.min(1,dt*12);
        const o=scene.getObjects(field+'Bar')[0];if(o){const width=field==='EnemyHealth'?241:225;o.setWidth(Math.max(.1,width*Math.max(0,ctx[key])/max));}
      }
      for(let i=0;i<3;i++){const trophy=scene.getObjects('Trophy'+i)[0];if(trophy)trophy.setOpacity(num('Badges')>i?255:55);}
      const input=scene.getGame().getInputManager(),mx=input.getMouseX(),my=input.getMouseY();
      for(const b of ctx.buttons){const hover=mx>=b.x&&mx<=b.x+b.w&&my>=b.y&&my<=b.y+b.h;const busy=name==='Arena'&&phase>0&&['Attack','Shield','Heal'].includes(b.o.getName());b.o.setOpacity(busy?125:255);b.o.setPosition(b.x,b.y+(hover&&!busy?-2:0));}
      ctx.emission+=dt;
      if(ctx.emission>.45){ctx.emission=0;if(name==='Lab')emit('ParticleBubble',1090,338,1);else if(name==='Final')emit('ParticleSpark',180+Math.random()*920,210,3);else if(name==='Arena')emit('ParticleBubble',90+Math.random()*1100,510,1);}
      ctx.particles=ctx.particles.filter(p=>{
        p.age+=dt;if(p.age>=p.life){p.o.deleteFromScene(scene);return false;}
        if(p.projectile){const f=p.age/p.life;p.o.setPosition(340+570*f,375-Math.sin(f*Math.PI)*65);p.o.setAngle(30+f*360);}
        else{p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=35*dt;p.o.setPosition(p.x,p.y);if(p.spin)p.o.setAngle(p.o.getAngle()+p.spin*dt);}
        p.o.setOpacity(255*Math.min(1,(p.life-p.age)/.3));return true;
      });
      syncMusic();
    }
    window.addEventListener('pagehide',()=>{if(music)music.pause();if(audioContext)audioContext.suspend().catch(()=>{});});
    return {tick,events,getMusic:()=>music,inspect:()=>({scene:scene?.getName(),phase:scene?sv('Phase'):0,particles:ctx?.particles.length||0,musicOn:scene?num('MusicOn'):0,track})};
  })();
}
globalThis.MonsterWorld.tick(runtimeScene);
