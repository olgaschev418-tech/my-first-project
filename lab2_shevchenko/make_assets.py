from pathlib import Path
import runpy, io, contextlib, builtins, subprocess
from unittest.mock import patch
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).parent
A = ROOT/'assets'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def transcript(name, values):
    answers=iter(map(str, values))
    def answer(prompt=''):
        value=next(answers)
        print(prompt+value)
        return value
    out=io.StringIO()
    with patch.object(builtins, 'input', answer), contextlib.redirect_stdout(out):
        runpy.run_path(str(ROOT/'programs'/name), run_name='__main__')
    result=out.getvalue()
    (A/(name+'.txt')).write_text(result)
    return result

def screenshot(text, name):
    font=ImageFont.truetype(FONT, 24)
    lines=text.rstrip().splitlines()
    width=max(int(font.getlength(line)) for line in lines)+52
    height=len(lines)*34+42
    im=Image.new('RGB',(width,height),'#101010')
    draw=ImageDraw.Draw(im)
    for i,line in enumerate(lines):
        draw.text((24,18+i*34),line,font=font,fill='white')
    im.save(A/name)

screenshot(transcript('task1_floor.py',[6,5,2,.5,.5,1,.5,.5,.5]),'figure1.png')
screenshot(transcript('task2_book.py',[300,120,30,450]),'figure3.png')
ensemble=transcript('task3_ensemble.py',[
 1,.8,10,1,.9,20,1,.85,15,3,.88,2,2,3,.88,0])
# The repeated menu is omitted only from the displayed illustration.
ensemble='\n'.join(line for line in ensemble.splitlines()
                   if not line.startswith('1 — добавить'))
screenshot(ensemble,'figure5.png')
screenshot(transcript('task4_loss.py',[.8,.2,.1]),'figure8.png')

def cls(name, attrs, methods):
    def rows(lines):
        import html
        return ''.join('<TR><TD ALIGN="LEFT">'+html.escape(l)+'</TD></TR>' for l in lines)
    return ('<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" '
            'CELLPADDING="8"><TR><TD><B>'+name+'</B></TD></TR>'
            '<HR/>'+rows(attrs)+'<HR/>'+rows(methods)+'</TABLE>>')

def graph(file, nodes, edges=''):
    dot='digraph G { graph [rankdir=TB, bgcolor="white", pad="0.12", nodesep="0.4"]; node [shape=plain, fontname="DejaVu Sans", fontsize=13]; edge [fontname="DejaVu Sans", fontsize=12];\n'
    for key,(name,attrs,methods) in nodes.items():
        dot+=key+' [label='+cls(name,attrs,methods)+'];\n'
    dot+=edges+'\n}'
    (A/(file+'.dot')).write_text(dot)
    subprocess.run(['dot','-Tpng','-Gdpi=180',str(A/(file+'.dot')),'-o',str(A/(file+'.png'))],check=True)
graph('figure2',{
'f':('Floor',['+ length: float','+ width: float','+ obstacles: list[Obstacle]'],[
'+ __init__(length: float, width: float): None',
'+ total_area(): float','+ work_area(): float',
'+ add_obstacle(width: float, length: float): None',
'+ tiles_count(tile_width: float, tile_length: float): int']),
'o':('Obstacle',['+ width: float','+ length: float'],[
'+ __init__(width: float, length: float): None','+ area(): float'])},
'f -> o [dir=both, arrowtail=diamond, arrowhead=none, taillabel="1", headlabel="0..*"];')
num='Book | int | float'
graph('figure4',{'b':('Book',['+ pages: int'],[
'+ __init__(pages: int): None',
'+ __call__(pages: int): None',
'- _operand(other: object): int | float | NotImplementedType',
'- _result(value: int | float): Book',
*[f'+ {m}(other: {num}): Book' for m in ['__add__','__sub__','__mul__','__truediv__']],
'+ reading_time(speed: float): str','+ __str__(): str'])})
graph('figure6',{
'e':('Ensemble',['+ models: list[Model]'],[
'+ __init__(): None',
'+ add_model(accuracy: float, training_time: float): None',
'+ remove_model(index: int): None',
'+ average_accuracy(): float','+ total_training_time(): float',
'+ optimal_count(target: float): int | None','+ display(): None']),
'm':('Model',['+ accuracy: float','+ training_time: float'],[
'+ __init__(accuracy: float, training_time: float): None'])},
'e -> m [dir=both, arrowtail=diamond, arrowhead=none, taillabel="1", headlabel="0..*"];')
num='Loss | int | float'
graph('figure9',{'l':('Loss',['+ value: float'],[
'+ __init__(value: float): None','+ __call__(value: float): None',
'- _number(value: int | float): float',
'- _operand(other: object): float | NotImplementedType',
*[f'+ {m}(other: {num}): Loss' for m in ['__add__','__sub__','__mul__','__truediv__']],
'+ is_converging(previous: Loss | int | float): bool',
'+ __str__(): str'])})

def sequence(name, participants, messages):
    W=1600; H=190+len(messages)*105
    im=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(im)
    font=ImageFont.truetype(REG,23)
    small=ImageFont.truetype(REG,22)
    xs=[130+i*(W-260)/(len(participants)-1) for i in range(len(participants))]
    for x,label in zip(xs,participants):
        d.rectangle((x-115,20,x+115,85),outline='black',width=2)
        for j,line in enumerate(label.split('\n')):
            d.text((x,32+25*j),line,font=font,fill='black',anchor='mt')
        for y in range(90,H-20,18):d.line((x,y,x,y+9),fill='#555555',width=2)
    for i,(src,dst,label,reply) in enumerate(messages):
        y=145+i*105; a,b=xs[src],xs[dst]
        if src==dst:
            d.line((a,y,a+105,y,a+105,y+40,a,y+40),fill='black',width=2)
            d.polygon([(a,y+40),(a+14,y+34),(a+14,y+46)],fill='black')
            d.text((a+15,y-30),label,font=small,fill='black')
        else:
            if reply:
                direction=1 if b>a else -1
                for start in range(int(a),int(b),direction*22):
                    end=start+direction*12
                    d.line((start,y,end,y),fill='black',width=2)
            else:d.line((a,y,b,y),fill='black',width=2)
            direction=1 if b>a else -1
            d.polygon([(b,y),(b-direction*15,y-7),(b-direction*15,y+7)],fill='black')
            d.text(((a+b)/2,y-12),label,font=small,fill='black',anchor='mb')
    im.save(A/(name+'.png'))
sequence('figure7',['Пользователь','e: Ensemble','m: Model'],[
(0,1,'add_model(0.8, 10)',False),
(1,2,'«create» Model(0.8, 10)',False),
(2,1,'созданная модель',True),
(1,1,'models.append(m)',False),
(0,1,'average_accuracy()',False),
(1,2,'чтение accuracy = 0.8',False),
(2,1,'0.8',True),
(1,1,'sum / len = 0.8 / 1',False),
(1,0,'0.8 (80 %)',True)])
sequence('figure10',['Пользователь','a: Loss (0.8)','b: Loss (0.2)','result: Loss'],[
(0,1,'a + b → __add__(b)',False),
(1,1,'_operand(b)',False),
(1,2,'чтение b.value',False),
(2,1,'0.2',True),
(1,1,'0.8 + 0.2 = 1.0',False),
(1,3,'«create» Loss(1.0)',False),
(3,1,'result (value = 1.0)',True),
(1,0,'новый объект Loss',True)])
print('Prepared 10 figures and 4 execution transcripts')
