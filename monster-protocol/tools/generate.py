"""Generate editable GDevelop scenes and original, aligned monster parts."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, shutil, uuid
ROOT=Path(__file__).resolve().parents[1]
CATS=[('Body','Тело',6),('Eyes','Глаза',8),('Mouth','Рот',6),('Arms','Руки',4),('Legs','Ноги',4),('Horns','Рога',4),('Nose','Нос',4),('Ears','Уши',4),('Tail','Хвост',4),('Wings','Крылья',4)]
INK='#302446'; WHITE='#fff8ed'; MINT='#baf5d2'; LILAC='#bca7ff'; PEACH='#ffbca1'

def art(folder):
    folder.mkdir(parents=True,exist_ok=True)
    def canvas(size=(256,256)):
        im=Image.new('RGBA',(size[0]*2,size[1]*2)); return im,ImageDraw.Draw(im)
    def save(im,name): im.resize((im.width//2,im.height//2),Image.Resampling.LANCZOS).save(folder/name)
    def shapes(d):
        def el(box,fill,outline=INK,w=3):d.ellipse(tuple(int(v*2) for v in box),fill,outline,width=w*2)
        def rect(box,fill,r=15,outline=INK,w=3):d.rounded_rectangle(tuple(int(v*2) for v in box),r*2,fill,outline,width=w*2)
        def poly(points,fill,outline=INK,w=3):
            p=[(int(x*2),int(y*2)) for x,y in points];d.polygon(p,fill);d.line(p+[p[0]],outline,width=w*2,joint='curve')
        def line(points,fill=INK,w=3):d.line([(int(x*2),int(y*2)) for x,y in points],fill,width=w*2,joint='curve')
        return el,rect,poly,line
    colors=['#baf5d2','#bca7ff','#ffbca1','#9cd8ff','#ffdc85','#f6a7ce']
    for cat,_,count in CATS:
        for i in range(count):
            im,d=canvas((64,64) if cat=='Eyes' else (256,256));el,rect,poly,line=shapes(d)
            c=colors[i%6]
            if cat=='Body':
                if i%3==0:rect((57,49,199,219),c,62)
                elif i%3==1:el((49,47,207,222),c)
                else:poly([(70,215),(45,154),(60,94),(90,52),(160,52),(196,100),(211,160),(190,215)],c)
                el((76,175,180,208),'#fff8ed',outline=c,w=0)
                el((72,73,87,85),'#fff8ed',outline=c,w=0)
                for x,y in [(70,150),(181,130),(174,176)]:el((x,y,x+7,y+7),'#71627e',outline=c,w=0)
            elif cat=='Eyes':
                el((5,6,59,59),WHITE);el((20,18,46,49),['#473375','#227a67','#4168b5','#bd5472'][i%4]);el((29,25,41,44),INK);el((26,20,34,28),'white',outline='white',w=0)
                if i in [1,5]:poly([(3,3),(61,20),(61,3)],c)
                if i in [2,6]:line([(7,8),(30,1),(58,8)],w=5)
                if i==3:line([(6,35),(56,35)],w=4)
                if i==7:el((13,12,51,53),PEACH);el((24,22,40,44),INK)
            elif cat=='Mouth':
                if i%3==0:
                    rect((99,151,157,181),INK,14);poly([(106,154),(119,154),(113,166)],WHITE);poly([(137,154),(149,154),(143,166)],WHITE)
                    if i==3:el((121,170,144,181),'#fc8299',outline=INK,w=1)
                elif i%3==1:
                    d.arc((100*2,139*2,156*2,179*2),0,180,fill=INK,width=7)
                    if i==4:el((109,174,122,186),PEACH,outline=PEACH,w=0)
                else:el((112,151,144,179),INK);el((121,165,139,177),'#fc8299',outline=INK,w=1)
            elif cat=='Arms':
                for side in [0,1]:
                    x=30 if side==0 else 198
                    el((x,132,x+28,193),c)
                    if i>=2:
                        for j in range(3):el((x-4+j*12,171,x+6+j*12,193),c,w=2)
                    if i==1:line([(x+8,147),(x+20,147)],w=2)
            elif cat=='Legs':
                for x in [80,144]:
                    rect((x,205,x+31,246),c,10)
                    if i>=2:rect((x-7,228,x+37,249),PEACH if i==2 else LILAC,10)
            elif cat=='Horns':
                if i:
                    for x in [75,155]:poly([(x,72),(x-9,16 if i==1 else 30),(x+30,65)],'#ffdc85' if i!=3 else LILAC)
            elif cat=='Nose':
                if i==1:el((120,132,139,146),PEACH)
                if i==2:poly([(128,128),(118,145),(139,145)],LILAC)
                if i==3:
                    for x in [118,133]:el((x,136,x+7,143),INK)
            elif cat=='Ears':
                if i:
                    for x in [35,183]:
                        el((x,70,x+37,120),c);el((x+10,79,x+27,110),PEACH,w=1)
            elif cat=='Tail':
                if i:
                    line([(183,199),(229,206),(240,166),(228,151)],c,w=17)
                    line([(183,199),(229,206),(240,166),(228,151)],INK,w=3)
                    if i>=2:poly([(216,150),(241,138),(241,163)],PEACH)
            elif cat=='Wings':
                if i:
                    for side in [0,1]:
                        pts=[(64,150),(10,77),(12,145),(35,133),(57,178)]
                        if side:pts=[(256-x,y) for x,y in pts]
                        poly(pts,LILAC if i==1 else PEACH if i==2 else '#9cd8ff')
            save(im,f'{cat.lower()}-{i}.png')
    for name,color in [('panel','#251f39'),('soft','#332b48'),('mint',MINT),('lilac',LILAC),('peach',PEACH),('ink',INK)]:
        im,d=canvas((320,160));d.rounded_rectangle((1,1,639,319),radius=40,fill=color,outline='#ffffff18',width=2);save(im,name+'.png')
    im,d=canvas((1280,800))
    for y in range(1600):
        t=y/1600;d.line((0,y,2560,y),fill=(int(22+10*t),int(18+5*t),int(34+15*t)))
    d.ellipse((1150,-400,2850,1050),fill='#241c38');d.ellipse((-450,900,1200,2300),fill='#262239')
    for x in range(60,2560,72):
        for y in range(60,1600,72):d.ellipse((x,y,x+2,y+2),fill='#534563')
    save(im,'background.png')

def ins(t,*p):return {'type':{'value':t,'inverted':False},'parameters':list(p),'subInstructions':[]}
def ev(conditions=(),actions=(),events=()):return {'type':'BuiltinCommonInstructions::Standard','disabled':False,'folded':False,'conditions':list(conditions),'actions':list(actions),'events':list(events)}
def comment(s):return {'type':'BuiltinCommonInstructions::Comment','color':{'r':186,'g':245,'b':210,'textR':35,'textG':25,'textB':50},'comment':s,'comment2':''}
def group(s,events):return {'type':'BuiltinCommonInstructions::Group','name':s,'source':'','color':{'r':150,'g':130,'b':200},'events':events}
def js(code):return {'type':'BuiltinCommonInstructions::JsCode','inlineCode':code.splitlines(),'parameterObjects':'','useStrict':True,'eventsSheetExpanded':False}
def G(v):return f'GlobalVariable({v})'
def S(v,expr,op='='):return ins('ModVarGlobal',v,op,str(expr))
def T(v,expr):return ins('ModVarGlobalTxt',v,'=',expr)
def C(v,op,x):return ins('VarGlobal',v,op,str(x))
def SC(v,op,x):return ins('VarScene',v,op,str(x))
def SS(v,x):return ins('ModVarScene',v,'=',str(x))
def click(o):return [ins('MouseButtonReleased','','Left'),ins('SourisSurObjet',o,'','',''),ins('BuiltinCommonInstructions::Once')]
def go(name):return ins('Scene','',json.dumps(name),'')
def say(s):return T('Message',json.dumps(s,ensure_ascii=False))
def textset(o,e):return ins('TextObject::String',o,'=',e.replace(r'\n', '" + NewLine() + "'))
def variable(n,v):return {'name':n,'type':'string' if isinstance(v,str) else 'number','value':str(v)}
class Scene:
    def __init__(self,name,title,kicker):
        self.data={'name':name,'mangledName':name,'r':22,'v':18,'b':34,'title':title,'stopSoundsOnStartup':True,'standardSortMethod':True,'disableInputWhenNotFocused':True,'objects':[],'objectsGroups':[],'instances':[],'variables':[variable('Command',0),variable('TakenTurn',0),variable('Damage',0)],'events':[],'layers':[{'name':'','visibility':True,'cameras':[{'defaultSize':True,'defaultViewport':True,'width':0,'height':0,'viewportLeft':0,'viewportTop':0,'viewportRight':1,'viewportBottom':1}],'effects':[]}],'behaviorsSharedData':[],'uiSettings':{'grid':False,'snap':False,'windowMask':True,'zoomFactor':0.7}}
        self.sprite('Backdrop',['background.png'],0,0,1280,800,0)
        self.text('Brand','MONSTER / PROTOCOL',52,28,23,MINT,True)
        self.text('Edition','AI GAME LAB    /    GDEVELOP',912,34,16,'#b7a8ca')
        self.text('Title',title,52,86,42,WHITE,True)
        self.text('Kicker',kicker,54,143,18,'#b7a8ca')
    def sprite(self,n,files,x,y,w,h,z=3):
        if not any(o['name']==n for o in self.data['objects']):
            self.data['objects'].append({'name':n,'type':'Sprite','variables':[],'behaviors':[],'updateIfNotVisible':False,'animations':[{'name':f'Вариант {i+1}','useMultipleDirections':False,'directions':[{'looping':False,'timeBetweenFrames':1,'sprites':[{'image':'assets/'+f,'originPoint':{'name':'origin','x':0,'y':0},'centerPoint':{'name':'center','x':0,'y':0,'automatic':True},'points':[],'hasCustomCollisionMask':False,'customCollisionMask':[]}]}]} for i,f in enumerate(files)]})
        self.data['instances'].append({'name':n,'x':x,'y':y,'zOrder':z,'angle':0,'width':w,'height':h,'customSize':True,'layer':'','locked':False,'numberProperties':[],'stringProperties':[],'initialVariables':[]})
    def text(self,n,s,x,y,size=20,color=WHITE,bold=False):
        rgb=tuple(int(color.lstrip('#')[i:i+2],16) for i in (0,2,4))
        self.data['objects'].append({'name':n,'type':'TextObject::Text','variables':[],'behaviors':[],'string':s,'font':'assets/DejaVuSans.ttf','characterSize':size,'bold':bold,'italic':False,'underlined':False,'smoothed':True,'textAlignment':'left','color':dict(zip(['r','g','b'],rgb))})
        self.data['instances'].append({'name':n,'x':x,'y':y,'zOrder':20,'angle':0,'width':0,'height':0,'customSize':False,'layer':'','locked':False,'numberProperties':[],'stringProperties':[],'initialVariables':[]})
    def button(self,n,label,x,y,w=200,color='mint',size=19):
        self.sprite(n,[color+'.png'],x,y,w,56,10);self.text(n+'Label',label,x+18,y+15,size,INK,True)
    def monster(self,x=155,y=239,size=350,enemy=False):
        for cat,_,n in CATS:
            if cat=='Eyes':
                for dx in [94,134]:self.sprite('MonsterEyes',[f'eyes-{i}.png' for i in range(n)],x+size*dx/256,y+size*93/256,size*41/256,size*41/256,8)
            else:self.sprite('Monster'+cat,[f'{cat.lower()}-{i}.png' for i in range(n)],x,y,size,size,{'Wings':1,'Tail':2,'Legs':3,'Arms':4,'Ears':4,'Body':5,'Horns':6,'Mouth':9,'Nose':10}.get(cat,6))
        if not enemy:
            self.data['events'].append(group('01 · Внешность: применяем номера анимаций ко ВСЕМ экземплярам', [ev(actions=[ins('ChangeAnimation','Monster'+cat,'=',G(cat+'Variant')) for cat,_,_ in CATS])]))
    def add(self,*events):self.data['events'].extend(events)

def project(folder,starter=False):
    assets=folder/'assets';art(assets);shutil.copy('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',assets/'DejaVuSans.ttf')
    variables={cat+'Variant':0 for cat,_,_ in CATS};variables.update(Name='Искрик',Health=100,Energy=60,Strength=10,XP=0,Level=1,Wins=0,Round=1,EnemyHP=60,AICommand=0,AIPanel=0,NamePanel=0,SaveRequest=0,LoadRequest=0,Message='Собери друга. Придумай его историю.')
    props={'name':'Monster Protocol — '+('шаблон ученика' if starter else 'демонстрация'),'description':'Собери монстра. Заботься. Обучи команды. Победи на арене.','author':'AI GAME LAB','version':'1.0.0','packageName':'school.aigame.monsterprotocol','windowWidth':1280,'windowHeight':800,'maxFPS':60,'minFPS':15,'verticalSync':False,'scaleMode':'linear','pixelsRounding':False,'adaptGameResolutionAtRuntime':False,'sizeOnStartupMode':'adaptWidth','projectFile':'','folderProject':False,'orientation':'landscape','currentPlatform':'GDevelop JS platform','platforms':[{'name':'GDevelop JS platform'}],'useExternalSourceFiles':True,'loadingScreen':{'showGDevelopSplash':False},'extensions':[],'latestCompilationDirectory':'','platformSpecificAssets':{},'authorIds':[],'authorUsernames':[],'categories':[],'playableDevices':['desktop'],'extensionProperties':[], 'watermark':{'showWatermark':True,'placement':'bottom-left'}}
    scenes=[]
    s=Scene('MonsterCreator','Сначала — твой монстр.','01 / КОНСТРУКТОР     •     Детали независимы. История — только твоя.')
    if starter:
        for o in s.data['objects']:
            if o['name']=='Kicker':o['string']='ШАБЛОН УЧЕНИКА / Работают стрелки тела и глаз вправо. Остальное создадим на занятиях.'
    s.sprite('PortraitPanel',['panel.png'],50,196,540,469,1);s.sprite('PartPanel',['panel.png'],615,196,615,469,1)
    s.monster();s.text('NameText','Искрик',105,598,31,MINT,True);s.text('Combination','Собран из отдельных спрайтов',105,637,15,'#b7a8ca')
    switches=[]
    for j,(cat,label,n) in enumerate(CATS):
        col=j//5; row=j%5;x=638+col*293;y=220+row*85
        s.text(cat+'Title',label,x+3,y,18,'#b7a8ca');s.button(cat+'Prev','‹',x,y+26,48,'lilac',22);s.button(cat+'Next','›',x+219,y+26,48,'lilac',22)
        s.text(cat+'Count',f'1 / {n}',x+82,y+42,19,WHITE,True)
        switches.append(ev(click(cat+'Next'),[S(cat+'Variant',f'mod({G(cat+"Variant")}+1,{n})')]))
        switches.append(ev(click(cat+'Prev'),[S(cat+'Variant',f'mod({G(cat+"Variant")}+{n}-1,{n})')]))
        s.add(ev(actions=[textset(cat+'Count',f'ToString({G(cat+"Variant")}+1)+" / {n}"')]))
    s.button('Random','Случайный',52,680,191,'lilac');s.button('Rename','Имя',255,680,114,'peach');s.button('Save','Сохранить',381,680,190,'lilac');s.button('Load','Загрузить',583,680,180,'lilac');s.button('ToLab','В лабораторию →',940,680,288,'mint')
    if starter:
        s.add(comment('СТАРТ УЧЕНИКА: монстр уже состоит из отдельных объектов. Двигай/масштабируй детали в редакторе. Каждый вариант — отдельная анимация с ОДНИМ кадром.'),group('02 · Образцы событий: тело вправо и глаза вправо',[switches[0],switches[2]]),comment('УРОКИ 3–4: скопируй эти события для стрелок влево и остальных категорий. Число вариантов смотри в объекте.'),comment('УРОКИ 5–12: добавляй события по docs/LESSONS_RU.md. Серые сцены — заготовки, не готовые механики.'))
    else:
        s.add(group('02 · Выбор деталей: один щелчок, циклический номер',switches),group('03 · Случайная комбинация',[ev(click('Random'),[S(cat+'Variant',f'Random({n-1})') for cat,_,n in CATS])]),ev(click('ToLab'),[go('Lab')]))
    s.add(ev(click('Rename'),[S('NamePanel',1)]),ev(click('Save'),[S('SaveRequest',1)]),ev(click('Load'),[S('LoadRequest',1)]),ev(actions=[textset('NameText','GlobalVariableString(Name)')]))
    scenes.append(s)
    for scene,title,kicker in [('Lab','Забота делает сильнее.','02 / ЛАБОРАТОРИЯ     •     Сначала ресурсы и тренировки, затем арена.'),('Arena','Сила. Тактика. Твой ход.','03 / АРЕНА     •     Атака тратит энергию. Щит помогает восстановиться.'),('Final','Маленький монстр. Большая победа.','04 / ФИНАЛ     •     Три соперника позади. Твой проект готов к показу.')]:
        s=Scene(scene,title,kicker);s.sprite('PortraitPanel',['panel.png'],50,197,540,433,1);s.monster(155,216,350)
        s.text('NameText','Искрик',100,570,30,MINT,True);s.add(ev(actions=[textset('NameText','GlobalVariableString(Name)')]))
        s.text('Message','',55,650,19,'#cabbdf');s.add(ev(actions=[textset('Message','GlobalVariableString(Message)')]))
        s.button('Creator','← Конструктор',52,690,250,'lilac');s.button('Camera','ИИ / камера',924,690,304,'mint')
        s.add(ev(click('Creator'),[go('MonsterCreator')]),ev(click('Camera'),[S('AIPanel',1)]))
        if scene=='Lab':
            s.sprite('StatsPanel',['panel.png'],615,197,615,433,1)
            s.text('StatsTitle','ПАСПОРТ ИССЛЕДОВАТЕЛЯ',647,220,20,MINT,True)
            s.text('Stats','',649,274,26,WHITE)
            s.add(ev(actions=[textset('Stats','"Здоровье   " + ToString(GlobalVariable(Health)) + " / 100\\nЭнергия      " + ToString(GlobalVariable(Energy)) + " / 100\\nСила             " + ToString(GlobalVariable(Strength)) + " / 30\\nУровень       " + ToString(GlobalVariable(Level)) + "\\nПобеды         " + ToString(GlobalVariable(Wins)) + " / 3"')]))
            s.button('Feed','Кормить  +20',643,510,257,'peach');s.button('Train','Тренировать',918,510,282,'lilac');s.button('Rest','Отдых  ♥',643,579,257,'lilac');s.button('Battle','На арену →',918,579,282,'mint')
            if not starter:
                s.add(ev(click('Feed'),[S('Energy',f'min(100,{G("Energy")}+20)'),say('Энергия восстановлена. Максимум — 100.')]),ev(click('Rest'),[S('Energy',100),S('Health',100),say('Отдохнули! Здоровье и энергия восстановлены.')]),ev(click('Train')+[C('Energy','>=',20)],[S('Energy',G('Energy')+'-20'),S('Strength',f'min(30,{G("Strength")}+4)'),S('XP',G('XP')+'+1'),S('Level',f'1+floor({G("XP")}/3)'),say('Тренировка: +4 силы, −20 энергии. Каждые 3 тренировки — уровень.')]),ev(click('Train')+[C('Energy','<',20)],[say('Нужно 20 энергии. Покорми монстра или отдохни.')]),ev(click('Battle'),[S('Round',G('Wins')+'+1'),S('EnemyHP','40+20*GlobalVariable(Round)'),say('Твой ход. Команды работают кнопками и через обученную камеру.'),go('Arena')]))
        if scene=='Arena':
            s.sprite('EnemyPanel',['panel.png'],615,197,615,433,1)
            # Rival is a single composed silhouette, distinct from editable player's parts.
            s.sprite('Rival',['body-1.png'],840,245,260,260,5);s.sprite('RivalEyes',['eyes-1.png'],930,344,55,55,8);s.sprite('RivalMouth',['mouth-3.png'],840,245,260,260,9)
            s.text('EnemyTitle','УЧЕБНЫЙ СПАРРИНГ',647,220,20,PEACH,True);s.text('CombatStats','',647,542,23,WHITE)
            s.add(ev(actions=[textset('CombatStats','"Раунд " + ToString(GlobalVariable(Round)) + " / 3     Соперник: " + ToString(GlobalVariable(EnemyHP)) + " HP\\nТы: " + ToString(GlobalVariable(Health)) + " HP     Энергия: " + ToString(GlobalVariable(Energy))')]))
            s.button('Attack','Атака  −10',630,615,185,'peach');s.button('Shield','Щит  +14',827,615,180,'lilac');s.button('Heal','Лечение −20',1019,615,210,'mint');s.button('Retreat','В лабораторию',329,690,267,'lilac')
            s.add(ev(click('Retreat'),[say('Можно отдохнуть и попробовать снова. Победы сохранены.'),go('Lab')]))
            if not starter:
                combat=[comment('Команда 1 = атака, 2 = щит, 3 = лечение. Камера пишет такую же команду. Одна команда — один ход.'),ev(actions=[SS('Command',0),SS('TakenTurn',0),SS('Damage','6+2*GlobalVariable(Round)')]),ev(click('Attack'),[SS('Command',1)]),ev(click('Shield'),[SS('Command',2)]),ev(click('Heal'),[SS('Command',3)]),ev([C('AICommand','>',0)],[SS('Command',G('AICommand')),S('AICommand',0)]),ev([SC('Command','=',1),C('Energy','>=',10)],[S('EnemyHP','max(0,GlobalVariable(EnemyHP)-GlobalVariable(Strength))'),S('Energy',G('Energy')+'-10'),SS('TakenTurn',1),say('Атака! Соперник отвечает, если ещё не побеждён.')]),ev([SC('Command','=',1),C('Energy','<',10),SC('TakenTurn','=',0)],[say('Мало энергии для атаки. Используй щит.')]),ev([SC('Command','=',2)],[S('Energy','min(100,GlobalVariable(Energy)+14)'),SS('Damage',3),SS('TakenTurn',1),say('Щит: +14 энергии. Ответ соперника ослаблен до 3.')]),ev([SC('Command','=',3),C('Energy','>=',20)],[S('Energy',G('Energy')+'-20'),S('Health','min(100,GlobalVariable(Health)+25)'),SS('TakenTurn',1),say('Лечение: +25 здоровья, −20 энергии. Соперник отвечает.')]),ev([SC('Command','=',3),C('Energy','<',20),SC('TakenTurn','=',0)],[say('Нужно 20 энергии для лечения. Используй щит.')]),ev([SC('TakenTurn','=',1),C('EnemyHP','>',0)],[S('Health','max(0,GlobalVariable(Health)-Variable(Damage))')]),ev([SC('TakenTurn','=',1),C('EnemyHP','<=',0)],[S('Wins',G('Wins')+'+1'),say('Победа! Восстановись в лаборатории перед следующим раундом.')]),ev([C('EnemyHP','<=',0),C('Wins','<',3)],[go('Lab')]),ev([C('Wins','>=',3)],[go('Final')]),ev([C('Health','<=',0),C('EnemyHP','>',0)],[say('Тренировочное поражение. Отдохни и попробуй другую тактику.'),go('Lab')])]
                s.add(group('04 · Пошаговый бой — без тайного кода',combat))
        if scene=='Final':
            s.text('Badge','ПРОТОКОЛ ЗАВЕРШЁН',648,234,24,MINT,True);s.text('FinalText','Ты создал героя из деталей.\nНаучился заботиться о нём.\nВыбрал собственную тактику.\n\nСледующая цель:\nобучи свои команды камеры!',648,298,24,WHITE)
            s.button('Again','Новая кампания',649,554,340,'peach')
            if not starter:s.add(ev(click('Again'),[S('Wins',0),S('Round',1),S('Health',100),S('Energy',60),S('Strength',10),S('XP',0),S('Level',1),say('Новая кампания. Внешность и имя остались твоими.'),go('Lab')]))
        if starter:s.add(comment('ЗАГОТОВКА УЧЕНИКА: интерфейс готов. Добавляйте события по плану занятий. За образцом смотрите сцену с тем же именем в демонстрационном проекте.'))
        scenes.append(s)
    for scene in scenes:
        if scene.data['name']=='Lab':
            events=scene.data['events']
            training=[e for e in events if any(c.get('parameters',[None])[0]=='Train' for c in e.get('conditions',[]) if c.get('parameters'))]
            if len(training)==2:
                a,b=training
                index=events.index(a);events.remove(b);events.insert(index,b)
    bridge=(ROOT/'teacher/bridge.js').read_text()
    for s in scenes:
        s.add(group('99 · Служебный адаптер преподавателя: имя, локальное сохранение, Teachable Machine',[js(bridge)]))
    resources=[]
    for f in sorted(assets.iterdir()):
        if f.suffix not in ('.png','.ttf'):continue
        resources.append({'name':'assets/'+f.name,'file':'assets/'+f.name,'kind':'font' if f.suffix=='.ttf' else 'image','metadata':'','smoothed':True,'userAdded':True,'alwaysLoaded':False})
    # JavaScript resources preserve local ML libraries through native GDevelop export.
    for name,source in [('tf.min.js','@tensorflow/tfjs/dist/tf.min.js'),('tm.min.js','@teachablemachine/image/dist/teachablemachine-image.min.js')]:
        shutil.copy(ROOT/'node_modules'/source,assets/name)
        resources.append({'name':'assets/'+name,'file':'assets/'+name,'kind':'javascript','metadata':'','userAdded':True})
    shutil.copy(ROOT/'teacher/demo-model/bundle.json', assets/'demo-bundle.json')
    resources.append({'name':'assets/demo-bundle.json','file':'assets/demo-bundle.json','kind':'json','metadata':'','userAdded':True})
    data={'firstLayout':'MonsterCreator','gdVersion':{'major':5,'minor':6,'build':269,'revision':0},'properties':props,'resources':{'resources':resources,'resourceFolders':[]},'variables':[variable(n,v) for n,v in variables.items()],'objects':[],'objectsGroups':[],'layouts':[s.data for s in scenes],'externalEvents':[],'externalLayouts':[],'eventsFunctionsExtensions':[],'externalSourceFiles':[]}
    (folder/'game.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (folder/'START_HERE.txt').write_text('MONSTER PROTOCOL\nОткройте game.json в настольном GDevelop 5.6.269 или новее.\nПереносите ВСЮ папку проекта вместе с assets.\n'+('Это стартовый шаблон: игровую логику дети добавляют на уроках.\n' if starter else 'Это готовый образец результата курса.\n')+'План занятий и точные события находятся в папке docs основного комплекта.\n',encoding='utf-8')
if __name__=='__main__':
    for name,starter in [('demo',False),('student-template',True)]:
        folder=ROOT/name;folder.mkdir(exist_ok=True);project(folder,starter)
    print('Generated: demo + student-template, 4 scenes each, 48 aligned part variants.')
