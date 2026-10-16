"""Build an ordinary Scratch 3 project. No custom blocks or extensions required.

The generator is a packaging tool for the teacher. Children edit the resulting
.sb3 using Scratch blocks; they do not need Python or this generator.
"""
import hashlib
import html
import json
from pathlib import Path
import zipfile
from copy import deepcopy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'web' / 'game'
OUT.mkdir(parents=True, exist_ok=True)
ASSETS = {}
SERIAL = 0
VARS = {
    'Сцена': 0, 'Здоровье': 100, 'Энергия': 50, 'Сила': 10,
    'Уровень': 1, 'Опыт': 0, 'Раунд': 1, 'Здоровье врага': 60,
    'Ход': 0, 'Защита': 0, 'Счётчик ходов': 0, 'Урон': 0,
    'Имя': 'Искрик', 'Победы': 0,
}
MESSAGES = ['Кормить', 'Тренировать', 'Отдых', 'Арена', 'Атака',
            'Защищаться', 'Лечение', 'Домой', 'Ответ врага', 'Уровень+', 'Победа']


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}">{body}</svg>')


def text(x, y, value, size=16, color='#f4f5ff', weight=700, anchor='middle'):
    return (f'<text x="{x}" y="{y}" font-family="DejaVu Sans,sans-serif" '
            f'font-size="{size}" fill="{color}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{html.escape(value)}</text>')


def costume(name, image, cx, cy):
    data = image.encode()
    md5 = hashlib.md5(data).hexdigest()
    ASSETS[md5 + '.svg'] = data
    return {'name': name, 'assetId': md5, 'dataFormat': 'svg',
            'md5ext': md5 + '.svg', 'bitmapResolution': 1,
            'rotationCenterX': cx, 'rotationCenterY': cy}


def background(kind):
    room = kind == 'Лаборатория'
    final = kind == 'Чемпион'
    color = '#172840' if room else '#201d40'
    b = f'<rect width="480" height="360" fill="{color}"/>'
    b += '<path d="M0 250L240 170 480 250V360H0Z" fill="#101d32"/>'
    b += '<path d="M0 290L480 290M0 330L480 330M240 170L80 360M240 170L400 360" stroke="#283750" stroke-width="1"/>'
    for x, y, r in [(35, 105, 2), (438, 90, 3), (80, 190, 2), (390, 190, 2), (240, 110, 2)]:
        b += f'<circle cx="{x}" cy="{y}" r="{r}" fill="#70e5c6" opacity=".6"/>'
    if room:
        b += '<rect x="20" y="110" width="98" height="100" rx="20" fill="#243b56" stroke="#416880" stroke-width="2"/>'
        b += '<path d="M37 180L58 154 79 173 99 130" fill="none" stroke="#73e2c4" stroke-width="4"/>'
        b += '<rect x="368" y="115" width="90" height="96" rx="18" fill="#263b55"/>'
        for x, h in [(383, 30), (403, 50), (423, 64)]:
            b += f'<rect x="{x}" y="{194-h}" width="12" height="{h}" rx="5" fill="#a79bff"/>'
        b += '<ellipse cx="240" cy="256" rx="85" ry="24" fill="#2f6667" opacity=".4"/>'
        b += '<ellipse cx="240" cy="251" rx="80" ry="20" fill="none" stroke="#68dfbb" stroke-width="2"/>'
    else:
        b += '<path d="M0 245L50 145 95 220 135 165 180 245M300 245L350 160 390 215 440 130 480 245" fill="#313254"/>'
        for x in [120, 360]:
            b += f'<ellipse cx="{x}" cy="260" rx="83" ry="22" fill="#393959" stroke="#9e89ff" stroke-width="2"/>'
    b += '<rect x="12" y="8" width="456" height="67" rx="14" fill="#0c172b" opacity=".95"/>'
    b += text(29, 28, 'MONSTER / AI LAB', 11, '#71e4c3', anchor='start')
    b += text(450, 28, 'АКАДЕМИЯ МОНСТРОВ', 9, '#adb9d4', anchor='end')
    label = 'ТВОЯ ЛАБОРАТОРИЯ' if room else 'АРЕНА ИСКР' if not final else 'ТЫ — ХРАНИТЕЛЬ ИСКР!'
    b += text(240, 99, label, 12, '#c7c4ef')
    b += text(240, 285, 'Ухаживай • тренируй • исследуй' if room else
              'Каждый третий удар врага — мощный. Защищайся!', 10, '#a3b3ce')
    if final:
        for x, y in [(65, 130), (410, 145), (240, 125), (80, 245), (400, 235)]:
            b += f'<path d="M{x} {y-10}l3 7 8 3-8 3-3 8-3-8-8-3 8-3Z" fill="#fbd17b"/>'
    return svg(480, 360, b)


def monster(color, enemy=False, boss=False, blink=False):
    b = '<ellipse cx="90" cy="145" rx="55" ry="10" fill="#081126" opacity=".35"/>'
    if boss:
        b += '<path d="M45 49L29 5 69 32M111 32L151 5 135 49" fill="#ffce78" stroke="#353153" stroke-width="4"/>'
    else:
        b += f'<path d="M50 57Q25 18 60 28L77 46M102 45Q147 10 133 61" fill="{color}" stroke="#23364e" stroke-width="4"/>'
    b += f'<path d="M34 101Q15 95 20 77M145 102Q168 100 160 79" fill="none" stroke="{color}" stroke-width="15" stroke-linecap="round"/>'
    b += f'<path d="M42 130Q29 83 45 57Q57 32 90 36Q136 29 143 73L145 120Q138 146 120 139L108 132Q90 149 72 133L60 140Q46 146 42 130Z" fill="{color}" stroke="#26354f" stroke-width="4"/>'
    b += '<ellipse cx="73" cy="72" rx="21" ry="24" fill="#fffdf4"/><ellipse cx="112" cy="72" rx="21" ry="24" fill="#fffdf4"/>'
    if blink:
        b += '<path d="M62 74H82M102 74H122" stroke="#25324a" stroke-width="5" stroke-linecap="round"/>'
    else:
        b += '<ellipse cx="78" cy="75" rx="8" ry="12" fill="#24314c"/><ellipse cx="108" cy="75" rx="8" ry="12" fill="#24314c"/><circle cx="81" cy="70" r="3" fill="white"/><circle cx="111" cy="70" r="3" fill="white"/>'
    b += '<path d="M74 105Q90 121 108 104" fill="#30334c" stroke="#30334c" stroke-width="3" stroke-linecap="round"/>'
    b += '<path d="M84 108H96L90 114Z" fill="white"/>'
    if not enemy:
        b += '<ellipse cx="54" cy="96" rx="10" ry="5" fill="#ffb2b8" opacity=".7"/><ellipse cx="128" cy="96" rx="10" ry="5" fill="#ffb2b8" opacity=".7"/>'
        b += '<path d="M88 126l4-8 4 8 9 1-7 5 2 8-8-4-7 4 1-8-6-5Z" fill="#fff1ad"/>'
    return svg(180, 160, b)


class Blocks:
    def __init__(self, target):
        self.t = target
        self.b = target['blocks']

    def add(self, opcode, inputs=None, fields=None, **extra):
        global SERIAL
        SERIAL += 1
        key = 'b' + str(SERIAL)
        self.b[key] = dict(opcode=opcode, next=None, parent=None,
                           inputs=inputs or {}, fields=fields or {}, shadow=False,
                           topLevel=False, **extra)
        for val in (inputs or {}).values():
            if len(val) > 1 and isinstance(val[1], str) and val[1] in self.b:
                self.b[val[1]]['parent'] = key
        return key

    def val(self, v):
        if isinstance(v, tuple):
            return [3, v[0], [4, '0']]
        if isinstance(v, str) and v.startswith('$'):
            return [3, [12, v[1:], 'v_' + v[1:]], [4, '0']]
        return [1, [4 if isinstance(v, (int, float)) else 10, str(v)]]

    def op(self, op, a, b=None):
        names = {'+': 'add', '-': 'subtract', '*': 'multiply', '/': 'divide',
                 '<': 'lt', '>': 'gt', '=': 'equals', 'and': 'and', 'or': 'or', 'mod': 'mod'}
        if op == 'not':
            return (self.add('operator_not', {'OPERAND': self.val(a)}),)
        boolean = op in ['<', '>', '=', 'and', 'or']
        left, right = ('OPERAND1', 'OPERAND2') if boolean else ('NUM1', 'NUM2')
        return (self.add('operator_' + names[op], {left: self.val(a), right: self.val(b)}),)

    def chain(self, blocks):
        items = [x for x in blocks if x]
        for a, b in zip(items, items[1:]):
            self.b[a]['next'] = b
            self.b[b]['parent'] = a
        return items[0] if items else None

    def hat(self, event, body, name=None, x=20, y=20):
        fields = {}
        if event == 'event_whenbroadcastreceived':
            fields = {'BROADCAST_OPTION': [name, 'm_' + name]}
        elif event == 'event_whenkeypressed':
            fields = {'KEY_OPTION': [name, None]}
        h = self.add(event, fields=fields)
        self.b[h].update(topLevel=True, x=x, y=y)
        first = self.chain(body)
        self.b[h]['next'] = first
        if first:
            self.b[first]['parent'] = h
        return h

    def set(self, var, value):
        return self.add('data_setvariableto', {'VALUE': self.val(value)}, {'VARIABLE': [var, 'v_' + var]})

    def change(self, var, value):
        return self.add('data_changevariableby', {'VALUE': self.val(value)}, {'VARIABLE': [var, 'v_' + var]})

    def control(self, code, body, condition=None):
        first = self.chain(body)
        ins = {'SUBSTACK': [2, first]} if first else {}
        if condition:
            ins['CONDITION'] = [2, condition[0]]
        return self.add('control_' + code, ins)

    def iff(self, condition, body):
        return self.control('if', body, condition)

    def wait(self, seconds):
        return self.add('control_wait', {'DURATION': self.val(seconds)})

    def send(self, message, wait=False):
        return self.add('event_broadcastandwait' if wait else 'event_broadcast',
                        {'BROADCAST_INPUT': [1, [11, message, 'm_' + message]]})

    def say(self, words, seconds=1.2):
        return self.add('looks_sayforsecs', {'MESSAGE': self.val(words), 'SECS': self.val(seconds)})

    def go(self, x, y):
        return self.add('motion_gotoxy', {'X': self.val(x), 'Y': self.val(y)})

    def show(self, yes=True):
        return self.add('looks_show' if yes else 'looks_hide')

    def backdrop(self, name):
        menu = self.add('looks_backdrops', fields={'BACKDROP': [name, None]})
        self.b[menu]['shadow'] = True
        return self.add('looks_switchbackdropto', {'BACKDROP': [1, menu]})


def target(name, costumes, stage=False, x=0, y=0, size=100):
    return {'isStage': stage, 'name': name, 'variables': {}, 'lists': {},
            'broadcasts': {}, 'blocks': {}, 'comments': {}, 'currentCostume': 0,
            'costumes': costumes, 'sounds': [], 'volume': 50, 'layerOrder': 0,
            **({'tempo': 60, 'videoTransparency': 50, 'videoState': 'off', 'textToSpeechLanguage': None}
               if stage else {'visible': True, 'x': x, 'y': y, 'size': size,
                              'direction': 90, 'draggable': False, 'rotationStyle': "don't rotate"})}


stage = target('Stage', [costume(n, background(n), 240, 180)
                        for n in ['Лаборатория', 'Арена', 'Чемпион']], True)
stage['variables'] = {'v_' + k: [k, v] for k, v in VARS.items()}
stage['broadcasts'] = {'m_' + n: n for n in MESSAGES}
s = Blocks(stage)
s.hat('event_whenflagclicked', [s.set(k, v) for k, v in VARS.items()] + [s.backdrop('Лаборатория')])


def room_guard():
    return s.op('and', s.op('=', '$Сцена', 0), s.op('=', '$Ход', 0))


s.hat('event_whenbroadcastreceived', [s.iff(room_guard(), [
    s.set('Ход', 1), s.change('Энергия', 20),
    s.iff(s.op('>', '$Энергия', 100), [s.set('Энергия', 100)]),
    s.change('Здоровье', 10), s.iff(s.op('>', '$Здоровье', 100), [s.set('Здоровье', 100)]),
    s.wait(.3), s.set('Ход', 0)])], 'Кормить', x=400)
s.hat('event_whenbroadcastreceived', [s.iff(s.op('and', room_guard(), s.op('>', '$Энергия', 9)), [
    s.set('Ход', 1), s.change('Энергия', -10),
    s.iff(s.op('<', '$Сила', 24), [s.change('Сила', 2)]),
    s.change('Опыт', 10), s.send('Уровень+', True), s.wait(.3), s.set('Ход', 0)])], 'Тренировать', x=800)
s.hat('event_whenbroadcastreceived', [s.iff(room_guard(), [
    s.set('Ход', 1), s.set('Здоровье', 100), s.set('Энергия', 100),
    s.wait(.4), s.set('Ход', 0)])], 'Отдых', x=1200)
s.hat('event_whenbroadcastreceived', [s.iff(s.op('>', '$Опыт', 49), [
    s.change('Опыт', -50), s.change('Уровень', 1)])], 'Уровень+', x=1600)
s.hat('event_whenbroadcastreceived', [s.iff(room_guard(), [
    s.set('Ход', 1), s.set('Сцена', 1), s.set('Счётчик ходов', 0), s.set('Защита', 0),
    s.set('Здоровье врага', s.op('+', 20, s.op('*', '$Раунд', 40))),
    s.backdrop('Арена'), s.wait(.4), s.set('Ход', 0)])], 'Арена', x=2000)
s.hat('event_whenbroadcastreceived', [s.iff(s.op('=', '$Ход', 0), [
    s.set('Ход', 1),
    s.iff(s.op('=', '$Сцена', 4), [s.set('Раунд', 1)]),
    s.set('Сцена', 0), s.backdrop('Лаборатория'), s.wait(.3), s.set('Ход', 0)])], 'Домой', y=800)


def battle_guard():
    return s.op('and', s.op('=', '$Сцена', 1), s.op('=', '$Ход', 0))


s.hat('event_whenbroadcastreceived', [s.iff(s.op('and', battle_guard(), s.op('>', '$Энергия', 7)), [
    s.set('Ход', 1), s.change('Энергия', -8),
    s.change('Здоровье врага', s.op('-', 0, s.op('+', '$Сила', s.op('*', '$Уровень', 2)))),
    s.iff(s.op('<', '$Здоровье врага', 1), [
        s.set('Здоровье врага', 0), s.send('Победа', True)]),
    s.iff(s.op('=', '$Сцена', 1), [s.send('Ответ врага', True)]),
    s.set('Ход', 0)])], 'Атака', x=400, y=800)
s.hat('event_whenbroadcastreceived', [s.iff(battle_guard(), [
    s.set('Ход', 1), s.set('Защита', 1), s.change('Энергия', 18),
    s.iff(s.op('>', '$Энергия', 100), [s.set('Энергия', 100)]),
    s.send('Ответ врага', True), s.set('Ход', 0)])], 'Защищаться', x=800, y=800)
s.hat('event_whenbroadcastreceived', [s.iff(s.op('and', battle_guard(),
    s.op('and', s.op('>', '$Энергия', 19), s.op('<', '$Здоровье', 100))), [
    s.set('Ход', 1), s.change('Энергия', -20), s.change('Здоровье', 30),
    s.iff(s.op('>', '$Здоровье', 100), [s.set('Здоровье', 100)]),
    s.send('Ответ врага', True), s.set('Ход', 0)])], 'Лечение', x=1200, y=800)
s.hat('event_whenbroadcastreceived', [
    s.wait(.45), s.change('Счётчик ходов', 1),
    s.set('Урон', s.op('+', 7, s.op('*', '$Раунд', 3))),
    s.iff(s.op('=', s.op('mod', '$Счётчик ходов', 3), 0), [s.change('Урон', 15)]),
    s.iff(s.op('=', '$Защита', 1), [s.set('Урон', 3)]),
    s.change('Здоровье', s.op('-', 0, '$Урон')), s.set('Защита', 0),
    s.iff(s.op('<', '$Здоровье', 1), [s.set('Здоровье', 0), s.set('Сцена', 3)])
], 'Ответ врага', x=1600, y=800)
s.hat('event_whenbroadcastreceived', [s.set('Сцена', 2), s.change('Победы', 1),
    s.change('Опыт', 30), s.send('Уровень+', True),
    s.iff(s.op('=', '$Раунд', 3), [s.set('Сцена', 4), s.backdrop('Чемпион')]),
    s.iff(s.op('<', '$Раунд', 3), [s.change('Раунд', 1)])
], 'Победа', x=2000, y=800)

pet = target('Искрик — твой питомец', [costume(n, monster(c), 90, 145) for n, c in
             [('Мятный', '#71dfbd'), ('Солнечный', '#ffc568'), ('Лиловый', '#af9bfa')]], x=0, y=-70, size=90)
p = Blocks(pet)
p.hat('event_whenflagclicked', [p.go(0, -70), p.say('Привет! Я Искрик. Нажми на меня — сменю цвет!', 3),
    p.control('forever', [p.iff(p.op('=', '$Сцена', 1), [p.go(-120, -75)]),
        p.iff(p.op('not', p.op('=', '$Сцена', 1)), [p.go(0, -70)]),
        p.add('motion_changeyby', {'DY': p.val(3)}), p.wait(.3),
        p.add('motion_changeyby', {'DY': p.val(-3)}), p.wait(.3)])])
p.hat('event_whenthisspriteclicked', [p.add('looks_nextcostume'), p.say('Учимся вместе! Имя можно поменять клавишей N.')], x=400)
p.hat('event_whenkeypressed', [p.iff(p.op('=', '$Сцена', 0), [
    p.add('sensing_askandwait', {'QUESTION': p.val('Как назовём питомца? Не вводи настоящее имя ребёнка.')}),
    p.set('Имя', (p.add('sensing_answer'),))])], 'n', x=800)
for i, (msg, words) in enumerate([('Кормить', 'Ням! Энергия — топливо для приключений.'),
    ('Тренировать', 'Становлюсь сильнее! Каждые 50 опыта — уровень.'),
    ('Отдых', 'Здоровье и энергия восстановлены!'), ('Победа', 'Получилось! Отдохнём перед следующим испытанием.')]):
    p.hat('event_whenbroadcastreceived', [p.say(words, 1.5)], msg, x=i*380, y=450)
p.hat('event_whenbroadcastreceived', [p.say('Искра, вперёд!', .35), p.go(-90, -65),
    p.wait(.1), p.go(-120, -75)], 'Атака', y=850)
p.hat('event_whenbroadcastreceived', [p.say('Щит! Восстанавливаю энергию.', .5)], 'Защищаться', x=400, y=850)
p.hat('event_whenbroadcastreceived', [p.say('Исцеляющая искра!', .5)], 'Лечение', x=800, y=850)

enemy = target('Соперники и босс', [costume(n, monster(c, True, boss), 90, 145) for n, c, boss in
               [('Шуршик', '#f5b86a', False), ('Тучка', '#99a1eb', False), ('Громобосс', '#f086a5', True)]], x=120, y=-75, size=90)
e = Blocks(enemy)
e.hat('event_whenflagclicked', [e.show(False), e.control('forever', [
    e.iff(e.op('=', '$Сцена', 1), [e.show()]),
    e.iff(e.op('not', e.op('=', '$Сцена', 1)), [e.show(False)]), e.wait(.1)])])
menu = e.add('looks_costume', fields={'COSTUME': ['Шуршик', None]})
# A numeric costume input selects the opponent by round, using standard Scratch behavior.
e.hat('event_whenbroadcastreceived', [e.wait(.05),
    e.add('looks_switchcostumeto', {'COSTUME': e.val('$Раунд')}), e.go(120, -75),
    e.say('Дружеский поединок! Третий удар — мощный.', 2)], 'Арена', x=400)
e.hat('event_whenbroadcastreceived', [e.wait(.55),
    e.iff(e.op('=', e.op('mod', '$Счётчик ходов', 3), 2), [e.say('Заряжаю мощный удар! Пора ставить щит.', 1.2)])], 'Ответ врага', x=800)
del enemy['blocks'][menu]

targets = [stage, pet, enemy]
BUTTONS = [
    ('Кормить', 'F · КОРМИТЬ', 'f', '#72dfbd', -175, [0]),
    ('Тренировать', 'T · ТРЕНИРОВКА', 't', '#b6a0ff', -58, [0]),
    ('Отдых', 'R · ОТДЫХ', 'r', '#8ecaf2', 58, [0]),
    ('Арена', 'B · НА АРЕНУ', 'b', '#ffd07a', 175, [0]),
    ('Атака', 'A · АТАКА', 'a', '#ffab93', -175, [1]),
    ('Защищаться', 'D · ЩИТ', 'd', '#9fc6ff', -58, [1]),
    ('Лечение', 'H · ЛЕЧЕНИЕ', 'h', '#7de0be', 58, [1]),
    ('Домой', 'Q · ДОМОЙ', 'q', '#c7b8fa', 175, [1, 2, 3, 4]),
]
for msg, label, key, color, x, scenes in BUTTONS:
    art = svg(110, 38, f'<rect x="1" y="3" width="108" height="34" rx="12" fill="#081224"/>'
              f'<rect x="1" y="1" width="108" height="32" rx="11" fill="{color}"/>' + text(55, 22, label, 9, '#19273d'))
    t = target('Кнопка ' + msg, [costume(label, art, 55, 19)], x=x, y=-142)
    b = Blocks(t)
    cond = b.op('=', '$Сцена', scenes[0])
    for scene in scenes[1:]:
        cond = b.op('or', cond, b.op('=', '$Сцена', scene))
    # Two separate conditions keep the blocks familiar to beginners.
    other = b.op('=', '$Сцена', scenes[0])
    for scene in scenes[1:]:
        other = b.op('or', other, b.op('=', '$Сцена', scene))
    b.hat('event_whenflagclicked', [b.control('forever', [b.iff(cond, [b.show()]),
        b.iff(b.op('not', other), [b.show(False)]), b.wait(.1)])])
    b.hat('event_whenthisspriteclicked', [b.send(msg)], x=400)
    b.hat('event_whenkeypressed', [b.send(msg)], key, x=800)
    targets.append(t)

# Result cards also live inside Scratch, not just in the browser shell.
for scene, title, subtitle in [
    (2, 'ПОБЕДА! +30 ОПЫТА', 'Вернись домой, отдохни и встреть следующего соперника.'),
    (3, 'ПОПРОБУЕМ ЕЩЁ РАЗ?', 'Дома отдохни. Щит поможет пережить мощный удар.'),
    (4, 'ХРАНИТЕЛЬ ИСКР!', 'Громобосс побеждён! Теперь придумай своё приключение.'),
]:
    art = svg(440, 60, '<rect x="1" y="1" width="438" height="58" rx="15" fill="#283958" stroke="#79dcbc"/>'
              + text(220, 25, title, 17, '#9ef3cf') + text(220, 46, subtitle, 10, '#cfdaed'))
    t = target('Итог ' + str(scene), [costume(title, art, 220, 30)], x=0, y=40)
    b = Blocks(t)
    b.hat('event_whenflagclicked', [b.control('forever', [
        b.iff(b.op('=', '$Сцена', scene), [b.show()]),
        b.iff(b.op('not', b.op('=', '$Сцена', scene)), [b.show(False)]), b.wait(.1)])])
    targets.append(t)

# Monitors are standard Scratch monitors, so the project works in the official editor.
monitors = []
for var, x, y, width in [('Здоровье', 20, 39, 100), ('Энергия', 135, 39, 100),
                        ('Сила', 250, 39, 90), ('Уровень', 350, 39, 110),
                        ('Опыт', 15, 106, 85), ('Здоровье врага', 310, 106, 155)]:
    monitors.append({'id': 'v_' + var, 'mode': 'default', 'opcode': 'data_variable',
        'params': {'VARIABLE': var}, 'spriteName': None, 'value': VARS[var],
        'width': width, 'height': 23, 'x': x, 'y': y, 'visible': True,
        'sliderMin': 0, 'sliderMax': 100, 'isDiscrete': True})

for i, t in enumerate(targets):
    t['layerOrder'] = i
project = {'targets': targets, 'monitors': monitors, 'extensions': [],
           'meta': {'semver': '3.0.0', 'vm': '5.0.300', 'agent': 'MONSTER AI LAB educational project'}}
with zipfile.ZipFile(OUT / 'Monster_AI_Lab.sb3', 'w', zipfile.ZIP_DEFLATED) as archive:
    archive.writestr('project.json', json.dumps(project, ensure_ascii=False))
    for name, data in ASSETS.items():
        archive.writestr(name, data)
(OUT / 'pet.svg').write_text(monster('#71dfbd'))


def save_checkpoint(filename, allowed, buttons):
    """Keep complete script trees; never leave broken references in a starter."""
    snapshot = deepcopy(project)
    snapshot['targets'] = [t for t in snapshot['targets'] if t['isStage'] or
        t['name'].startswith('Искрик') or t['name'] in ['Кнопка ' + n for n in buttons]]
    for t in snapshot['targets']:
        blocks = t['blocks']
        roots = [key for key, block in blocks.items() if block['topLevel'] and
            (block['opcode'] != 'event_whenbroadcastreceived' or
             block['fields']['BROADCAST_OPTION'][0] in allowed)]
        keep = set()

        def visit(key):
            if not key or key in keep or key not in blocks:
                return
            keep.add(key)
            block = blocks[key]
            visit(block.get('next'))
            for value in block['inputs'].values():
                for item in value[1:]:
                    if isinstance(item, str):
                        visit(item)

        for root in roots:
            visit(root)
        t['blocks'] = {k: v for k, v in blocks.items() if k in keep}
    snapshot['monitors'] = [m for m in snapshot['monitors'] if m['params']['VARIABLE'] != 'Здоровье врага']
    with zipfile.ZipFile(OUT / filename, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('project.json', json.dumps(snapshot, ensure_ascii=False))
        for name, data in ASSETS.items():
            archive.writestr(name, data)


save_checkpoint('01_Pet.sb3', [], [])
save_checkpoint('04_Care.sb3', ['Кормить', 'Тренировать', 'Отдых', 'Уровень+'], ['Кормить', 'Тренировать', 'Отдых'])
print(f'Built {len(targets)} targets, {sum(len(t["blocks"]) for t in targets)} blocks, {len(ASSETS)} SVG assets')
