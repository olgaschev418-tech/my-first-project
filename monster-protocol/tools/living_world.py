"""Native GDevelop v2 scenes and readable turn sequencing for the classroom kit."""
from pathlib import Path
from world_art import make_world,make_music

def upgrade(data,assets,starter,api):
    Scene=api['Scene'];ev=api['ev'];ins=api['ins'];group=api['group'];comment=api['comment'];js=api['js'];variable=api['variable'];S=api['S'];SS=api['SS'];C=api['C'];SC=api['SC'];G=api['G'];say=api['say'];go=api['go'];click=api['click'];textset=api['textset'];T=api['T']
    root=Path(__file__).resolve().parents[1]
    make_world(assets);make_music(assets)
    extra={'Gold':0,'RoomStyle':0,'Badges':0,'MusicOn':1,'VisualFX':0,'PetRequest':0,'UseBattleScaffold':0,'IdleAmplitude':4,'ReactionHeight':27,'MusicVolume':25}
    data['variables'] += [variable(n,v) for n,v in extra.items()]
    data['properties']['version']='2.0.0'
    data['properties']['description']='Живая мастерская монстров: уютный дом, тренировки, три хранителя и команды камеры.'
    MINT=api['MINT'];WHITE=api['WHITE'];LILAC=api['LILAC'];PEACH=api['PEACH']
    def find(scene,name):return next(o for o in scene.data['objects'] if o['name']==name)
    def back(scene,files):find(scene,'Backdrop')['animations']=[{'name':f'Мир {i+1}','useMultipleDirections':False,'directions':[{'looping':False,'timeBetweenFrames':1,'sprites':[{'image':'assets/'+f,'originPoint':{'name':'origin','x':0,'y':0},'centerPoint':{'name':'center','x':0,'y':0,'automatic':True},'points':[],'hasCustomCollisionMask':False,'customCollisionMask':[]}]}]} for i,f in enumerate(files)]
    def common(s):
        s.sprite('HeaderShade',['panel.png'],20,14,1240,122,30)
        for o in s.data['objects']:
            if o['name']=='Brand':o['characterSize']=16;o['string']='MONSTER PROTOCOL  /  ЖИВАЯ МАСТЕРСКАЯ'
            if o['name']=='Edition':o['string']='AI GAME LAB';o['characterSize']=14
            if o['name']=='Title':o['characterSize']=30
            if o['name']=='Kicker':o['characterSize']=15
        for i in s.data['instances']:
            if i['name']=='Brand':i.update(x=44,y=24,zOrder=40)
            if i['name']=='Edition':i.update(x=930,y=26,zOrder=40)
            if i['name']=='Title':i.update(x=43,y=53,zOrder=40)
            if i['name']=='Kicker':i.update(x=45,y=98,zOrder=40)
        s.button('Music','Звук: вкл',1090,34,145,'lilac',16)
        for instance in s.data['instances']:
            if instance['name'] in ('Music','MusicLabel'):instance['zOrder']=45
        # Native click event toggles a global flag; the teacher adapter plays local audio.
        s.add(group('08 · Звук: переключатель',[ev(click('Music'),[S('MusicOn','1-GlobalVariable(MusicOn)')]),ev([C('MusicOn','=',0)],[textset('MusicLabel','"Звук: выкл"')]),ev([C('MusicOn','=',1)],[textset('MusicLabel','"Звук: вкл"')])]))
        for n,f in [('ParticleSpark','spark.png'),('ParticleHeart','heart.png'),('ParticleBubble','bubble.png'),('Projectile','bolt.png')]:s.sprite(n,[f],-400,-400,24,24,80)
        s.text('FloatingNumber','',-500,-500,30,WHITE,True)
        s.sprite('ShieldHalo',['shield.png'],-400,-400,110,110,16)
        s.data['variables'] += [variable('Phase',0),variable('TurnTime',0),variable('ActionKind',0),variable('PendingHit',0),variable('Charge',0)]
    def status(s):
        s.sprite('MessagePanel',['panel.png'],27,648,1224,37,14)
        s.text('Message','',45,657,16,'#e4e9e6');s.add(ev(actions=[textset('Message','GlobalVariableString(Message)')]))
        s.button('Creator','← Мастерская',42,697,217,'lilac',17)
        s.button('Camera','ИИ / камера',1002,697,236,'mint',17)
        s.add(ev(click('Creator'),[go('MonsterCreator')]),ev(click('Camera'),[S('AIPanel',1)]))
    def hud(s,arena=False):
        s.sprite('PlayerHUD',['panel.png'],43,146,310,88,14)
        s.text('PlayerName','',60,156,19,MINT,True)
        s.add(ev(actions=[textset('PlayerName','GlobalVariableString(Name)')]))
        for name,y,color in [('Health',190,'mint'),('Energy',214,'lilac')]:
            s.sprite(name+'Track',['soft.png'],61,y,225,11,35);s.sprite(name+'Bar',[color+'.png'],61,y,225,11,36)
            s.text(name+'Value','',294,y-7,13,WHITE)
            s.add(ev(actions=[textset(name+'Value',f'ToString(GlobalVariable({name}))')]))
        if not arena:
            s.sprite('ResearchHUD',['panel.png'],376,147,478,53,14);s.text('Stats','',392,162,17,WHITE)
            s.add(ev(actions=[textset('Stats','"Сила: "+ToString(GlobalVariable(Strength))+"    Уровень: "+ToString(GlobalVariable(Level))+"    Звёзды: "+ToString(GlobalVariable(Gold))')]))
    # Keep the editable constructor and its intentionally incomplete starter events.
    creator=data['layouts'][0]
    class Proxy:
        def __init__(self,d):self.data=d
    old=Scene('Unused','','');old.data=creator;common(old);back(old,[f'room-{i}.png' for i in range(3)])
    creator['events'].insert(0,ev(actions=[ins('ChangeAnimation','Backdrop','=',G('RoomStyle'))]))
    creator['events'].append(ev(click('MonsterBody'),[S('PetRequest',1),say('Ещё немного рожек — и можно отправляться в приключение!')]))
    # A furnished house is a world to touch, not a stats form.
    s=Scene('Lab','Дом, где растут маленькие герои.','ПОКОРМИ • ПОТРЕНИРУЙ • ОТДОХНИ • ОТПРАВЬСЯ К ТРЁМ ХРАНИТЕЛЯМ');back(s,[f'room-{i}.png' for i in range(3)]);common(s);status(s);hud(s)
    s.monster(385,241,350);s.text('NameText','',480,250,24,MINT,True);s.add(ev(actions=[textset('NameText','GlobalVariableString(Name)'),ins('ChangeAnimation','Backdrop','=',G('RoomStyle'))]))
    s.sprite('FoodBowl',['food.png'],120,454,85,85,15)
    s.sprite('Gift',['gift.png'],882,475,63,63,12)
    s.sprite('AdventurePanel',['panel.png'],964,399,244,49,12);s.text('AdventureHint','Лесные хранители →',978,414,16,MINT,True)
    s.text('RoomCaption','ТВОИ ТРОФЕИ',977,148,14,WHITE,True)
    for j in range(3):s.sprite('Trophy'+str(j),['trophy.png'],977+j*69,170,40,40,14)
    s.text('TrophiesHint','За победы над хранителями',976,212,12,'#d9d6e8')
    s.button('Feed','Угостить · +20',43,581,204,'peach',17);s.button('Train','Тренировка · −20',262,581,242,'lilac',17);s.button('Rest','Вздремнуть',519,581,201,'lilac',17)
    s.button('Decor','Дом +1 · 20 звёзд',735,581,241,'peach',16);s.button('Battle','В путь →',992,581,246,'mint',19)
    s.add(ev(click('MonsterBody'),[S('PetRequest',1),say('Почеши за рожками! А потом — тренировка или прогулка.')]))
    if not starter:
        s.add(group('03 · Уход: правила, реакции и улучшение дома',[
            ev(click('Feed'),[S('Energy','min(100,GlobalVariable(Energy)+20)'),S('VisualFX',1),say('Ням! +20 энергии. Крошки и счастье разлетаются во все стороны.')]),
            ev(click('FoodBowl'),[S('Energy','min(100,GlobalVariable(Energy)+20)'),S('VisualFX',1),say('Миска тоже работает! Монстрик рад угощению.')]),
            ev(click('Rest'),[S('Energy',100),S('Health',100),S('VisualFX',3),say('Тихий час: здоровье и энергия полностью восстановлены.')]),
            ev(click('Train')+[C('Energy','<',20)],[S('VisualFX',6),say('Для тренировки нужно 20 энергии. Загляни в миску или отдохни.')]),
            ev(click('Train')+[C('Energy','>=',20)],[S('Energy','GlobalVariable(Energy)-20'),S('Strength','min(30,GlobalVariable(Strength)+4)'),S('XP','GlobalVariable(XP)+1'),S('Level','1+floor(GlobalVariable(XP)/3)'),S('VisualFX',2),say('Прыг! +4 силы. Каждые три тренировки дают новый уровень.')]),
            ev(click('Decor')+[C('RoomStyle','<',2),C('Gold','<',20)],[S('VisualFX',6),say('Улучшение стоит 20 звёзд. Победи хранителя и забери награду!')]),
            ev(click('Decor')+[C('RoomStyle','>=',2)],[S('PetRequest',1),say('Дом уже полностью обустроен. Теперь можно придумать собственные украшения!')]),
            ev(click('Decor')+[C('RoomStyle','<',2),C('Gold','>=',20)],[S('Gold','GlobalVariable(Gold)-20'),S('RoomStyle','GlobalVariable(RoomStyle)+1'),S('VisualFX',4),say('В доме новое оборудование! Награды делают его по-настоящему твоим.')]),
            ev(click('Gift'),[S('PetRequest',1),say('В коробке — воображение. Придумай своему монстрику новую способность!')]),
            ev(click('Battle')+[C('Wins','<',3)],[S('Round','GlobalVariable(Wins)+1'),S('EnemyHP','40+20*GlobalVariable(Round)'),say('Хранитель ждёт. Красный знак предупреждает об усиленном ответе — ставь щит!'),go('Arena')])]))
    else:s.add(comment('УРОК 6: добавьте Feed/Train/Rest и VisualFX 1/2/3. Миска — второй способ вызвать кормление. УРОК 8: Battle задаёт Round и EnemyHP.'))
    if not starter:s.add(ev(click('Battle')+[C('Wins','>=',3)],[go('Final')]))
    lab=s.data
    s=Scene('Arena','Три хранителя звёздной долины.','ТВОЙ ХОД → ТВОЙ УДАР → ОТВЕТ ХРАНИТЕЛЯ. СЛЕДИ ЗА ПРЕДУПРЕЖДЕНИЕМ.');back(s,[f'arena-{i}.png' for i in range(3)]);common(s);status(s);hud(s,True)
    s.monster(127,228,355)
    s.sprite('Rival',[f'rival-{i}.png' for i in range(3)],794,224,355,355,10)
    s.sprite('EnemyHUD',['panel.png'],899,146,337,90,14)
    s.text('EnemyTitle','Моховик',916,156,19,PEACH,True);s.text('EnemyHPValue','',1170,191,14,WHITE)
    s.sprite('EnemyHealthTrack',['soft.png'],916,191,241,12,35);s.sprite('EnemyHealthBar',['peach.png'],916,191,241,12,36)
    s.text('RoundText','',1065,216,13,WHITE)
    s.text('PhaseText','Твой ход',474,158,22,MINT,True);s.text('EnemyIntent','',435,191,15,PEACH)
    s.text('NameText','',195,551,23,MINT,True)
    s.text('CombatStats','',891,551,16,WHITE)
    s.add(ev(actions=[ins('ChangeAnimation','Backdrop','=',G('Round')+'-1'),ins('ChangeAnimation','Rival','=',G('Round')+'-1'),textset('NameText','GlobalVariableString(Name)'),textset('EnemyHPValue','ToString(GlobalVariable(EnemyHP))'),textset('CombatStats','"Соперник: "+ToString(GlobalVariable(EnemyHP))+" HP"'),textset('RoundText','"ХРАНИТЕЛЬ "+ToString(GlobalVariable(Round))+" / 3"')]))
    for round_,name in [(1,'Моховик · лесной друг'),(2,'Искра · быстрая лиса'),(3,'Кристаллус · страж ночи')]:s.add(ev([C('Round','=',round_)],[textset('EnemyTitle',api['json'].dumps(name,ensure_ascii=False))]))
    s.button('Attack','Атака · −10',291,586,214,'peach',19);s.button('Shield','Щит · +14',521,586,205,'lilac',19);s.button('Heal','Лечение · −20',742,586,246,'mint',18)
    s.button('Retreat','Домой',275,697,170,'lilac',17)
    s.add(ev(click('Retreat'),[say('Дома можно отдохнуть. Текущий хранитель начнёт бой заново.'),go('Lab')]))
    # Temporal state machine is visible GDevelop logic. Presentation never changes HP or wins.
    init=ev([ins('SceneJustBegins','')],[SS('Phase',0),SS('TurnTime',0),SS('Charge',0),SS('ActionKind',0)])
    combat=[comment('Phase: 0 выбор; 1 замах игрока; 2 попадание; 3 ответ; 4 завершение; 5 победа. TurnTime — секунды с начала хода.'),init,
        ev(actions=[SS('Command',0)]),ev([SC('Phase','>',0)],[SS('TurnTime','Variable(TurnTime)+TimeDelta()')]),
        ev(click('Attack')+[SC('Phase','=',0)],[SS('Command',1)]),ev(click('Shield')+[SC('Phase','=',0)],[SS('Command',2)]),ev(click('Heal')+[SC('Phase','=',0)],[SS('Command',3)]),
        ev([C('AICommand','>',0),SC('Phase','=',0)],[SS('Command',G('AICommand')),S('AICommand',0)]),ev([C('AICommand','>',0),SC('Phase','>',0)],[S('AICommand',0)]),
        ev([SC('Command','=',1),C('Energy','<',10)],[S('VisualFX',6),say('Не хватает энергии! Щит восстановит силы и смягчит удар.')]),
        ev([SC('Command','=',1),C('Energy','>=',10)],[S('Energy','GlobalVariable(Energy)-10'),SS('PendingHit',G('Strength')),SS('ActionKind',1),SS('Phase',1),SS('TurnTime',0),SS('Charge','Variable(Charge)+1'),say('Звёздный выпад! Теперь дождись ответа хранителя.')]),
        ev([SC('Command','=',2)],[S('Energy','min(100,GlobalVariable(Energy)+14)'),SS('PendingHit',0),SS('ActionKind',2),SS('Phase',1),SS('TurnTime',0),SS('Charge','Variable(Charge)+1'),say('Защитный купол! +14 энергии, даже сильный удар нанесёт только 3 урона.')]),
        ev([SC('Command','=',3),C('Energy','<',20)],[S('VisualFX',6),say('Лечение стоит 20 энергии. Попробуй щит.')]),
        ev([SC('Command','=',3),C('Energy','>=',20)],[S('Energy','GlobalVariable(Energy)-20'),S('Health','min(100,GlobalVariable(Health)+25)'),SS('PendingHit',0),SS('ActionKind',3),SS('Phase',1),SS('TurnTime',0),SS('Charge','Variable(Charge)+1'),S('VisualFX',5),say('Целебное сияние! +25 здоровья. Хранитель готовит ответ.')]),
        ev([SC('Phase','=',1),SC('TurnTime','>=',.28)],[S('EnemyHP','max(0,GlobalVariable(EnemyHP)-Variable(PendingHit))'),SS('Phase',2)]),
        ev([SC('Phase','=',2),C('EnemyHP','>',0),SC('TurnTime','>=',.68)],[SS('Damage','6+2*GlobalVariable(Round)'),SS('Phase',3)]),
        ev([SC('Phase','=',3),SC('Charge','>=',3)],[SS('Damage','2*(6+2*GlobalVariable(Round))')]),
        ev([SC('Phase','=',3),SC('ActionKind','=',2)],[SS('Damage',3)]),
        ev([SC('Phase','=',3),SC('TurnTime','>=',1.08)],[S('Health','max(0,GlobalVariable(Health)-Variable(Damage))'),SS('Phase',4)]),
        ev([SC('Phase','=',4),SC('Charge','>=',3)],[SS('Charge',0)]),
        ev([SC('Phase','=',4),SC('TurnTime','>=',1.58),C('Health','>',0)],[SS('Phase',0),SS('ActionKind',0)]),
        ev([SC('Phase','=',4),SC('TurnTime','>=',1.58),C('Health','<=',0)],[say('Хранитель оказался сильнее. Дома тебя ждут отдых и новая попытка.'),go('Lab')]),
        ev([SC('Phase','=',2),C('EnemyHP','<=',0),SC('TurnTime','>=',.85)],[S('Wins','GlobalVariable(Wins)+1'),S('Badges','max(GlobalVariable(Badges),GlobalVariable(Wins))'),S('Gold','GlobalVariable(Gold)+20'),S('VisualFX',4),SS('Phase',5),SS('TurnTime',0),say('Победа! +20 звёзд и новый трофей для дома.')]),
        ev([SC('Phase','=',5),SC('TurnTime','>=',1.15),C('Wins','<',3)],[go('Lab')]),ev([SC('Phase','=',5),SC('TurnTime','>=',1.15),C('Wins','>=',3)],[go('Final')])]
    if not starter:s.add(group('04 · Анимированный ход и честный ответ хранителя',combat))
    else:
        # Teacher can activate a visual native-events scaffold, then pupils wire their own buttons.
        s.add(group('04.1 · УЧИТЕЛЬ: подготовка хода (UseBattleScaffold = 1)',[ev([C('UseBattleScaffold','=',1)],events=[init,combat[2],combat[3],combat[8]])]))
        s.add(group('04.2 · УЧЕНИК: добавь кнопки и AICommand ЗДЕСЬ',[comment('Attack + Phase=0 → Command=1. Shield → 2. Heal → 3. AICommand>0 + Phase=0 → Command=AICommand, AICommand=0. Все цены и ответы ниже в обычных событиях.')]))
        s.add(group('04.3 · УЧИТЕЛЬ: готовый анимированный ход (можно изучать и менять)',[ev([C('UseBattleScaffold','=',1)],events=combat[9:])]))
        s.add(comment('UseBattleScaffold=0: механики боя выключены для старта курса. На уроке 7 учитель меняет глобальную переменную на 1. Ребёнок добавляет свои команды в 04.2.'))
    s.add(ev([SC('Phase','=',0)],[textset('PhaseText','"Твой ход"'),textset('EnemyIntent','"Хранитель ответит после твоего действия"')]),ev([SC('Phase','=',0),SC('Charge','=',2)],[textset('EnemyIntent','"ГОТОВИТ СИЛЬНЫЙ УДАР — ИСПОЛЬЗУЙ ЩИТ!"')]),ev([SC('Phase','>',0)],[textset('PhaseText','"Смотри за боем…"')]),ev([SC('Phase','=',3)],[textset('PhaseText','"Хранитель отвечает!"')]),ev([SC('Phase','=',5)],[textset('PhaseText','"ПОБЕДА! +20 звёзд"')]))
    arena=s.data
    s=Scene('Final','Твой монстр стал легендой долины!','ТРИ ХРАНИТЕЛЯ ПОБЕЖДЕНЫ. ДОМА ПОЯВИЛИСЬ ТРОФЕИ, А У ТЕБЯ — СВОЯ ИГРА.');back(s,['arena-2.png']);common(s);status(s)
    s.monster(192,250,390);s.sprite('GrandTrophy',['trophy.png'],850,201,160,160,10)
    s.text('NameText','',294,599,28,MINT,True);s.add(ev(actions=[textset('NameText','GlobalVariableString(Name)')]))
    s.text('Badge','ХРАНИТЕЛЬ ДРУЖБЫ',734,371,27,MINT,True)
    s.text('FinalText','Три приключения. Три трофея.\nОдин неповторимый герой.\n\nВернись домой, укрась лабораторию\nили начни новое приключение.',737,421,21,WHITE)
    s.button('Again','Новое приключение',738,582,360,'peach',20);s.button('Home','В свой дом →',465,697,245,'mint',18)
    s.add(ev(click('Home'),[go('Lab')]))
    if not starter:s.add(ev(click('Again'),[S('Wins',0),S('Round',1),S('Health',100),S('Energy',60),S('Strength',10),S('XP',0),S('Level',1),say('Новое приключение. Дом, награды и внешность сохранились.'),go('Lab')]))
    final=s.data
    # Only the original creator's adapter group was retained; replace all service groups consistently.
    layouts=[creator,lab,arena,final]
    for layout in layouts:
        layout['events']=[e for e in layout['events'] if not e.get('name','').startswith('99 ·')]
        layout['events'].append(group('09 · Живой мир: готовая анимационная и звуковая заготовка преподавателя',[js((root/'teacher/presentation.js').read_text())]))
        layout['events'].append(group('99 · Служебный адаптер преподавателя: имя, сохранение, Teachable Machine',[js((root/'teacher/bridge.js').read_text())]))
    data['layouts']=layouts
    return data
