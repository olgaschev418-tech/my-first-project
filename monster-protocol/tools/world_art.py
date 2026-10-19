"""Original classroom game scenery, rivals, props and music (no remote assets)."""
from PIL import Image,ImageDraw,ImageFilter
from pathlib import Path
import math,random,wave,array
S=2

def make_world(folder):
    folder=Path(folder)
    def picture(size):
        im=Image.new('RGBA',(size[0]*S,size[1]*S));return im,ImageDraw.Draw(im)
    def paint(d):
        def box(b,c,r=0,outline=None,w=1):d.rounded_rectangle(tuple(round(x*S) for x in b),radius=r*S,fill=c,outline=outline,width=w*S)
        def oval(b,c,outline=None,w=1):d.ellipse(tuple(round(x*S) for x in b),fill=c,outline=outline,width=w*S)
        def poly(p,c,outline=None,w=1):
            q=[(round(x*S),round(y*S)) for x,y in p];d.polygon(q,fill=c)
            if outline:d.line(q+[q[0]],fill=outline,width=w*S,joint='curve')
        def line(p,c,w=1):d.line([(round(x*S),round(y*S)) for x,y in p],fill=c,width=w*S,joint='curve')
        return box,oval,poly,line
    def save(im,n):im.resize((im.width//S,im.height//S),Image.Resampling.LANCZOS).save(folder/n)
    rng=random.Random(12)
    for style in range(3):
        im,d=picture((1280,800));box,oval,poly,line=paint(d)
        for y in range(800):
            t=y/800;box((0,y,1280,y+1),(int(28+25*t),int(35+14*t),int(65+18*t)))
        # Structural arches and a huge picture window into the alien valley.
        box((45,116,1235,612),'#39476c',50,'#52658a',3)
        box((345,136,917,458),'#1b294a',96,'#637da4',12)
        box((360,148,902,448),['#28425d','#423e72','#274d59'][style],83)
        oval((715,174,801,260),'#ffe8b1');oval((736,162,816,240),['#28425d','#423e72','#274d59'][style])
        for i in range(34):
            x=rng.randint(395,870);y=rng.randint(170,350);oval((x,y,x+2,y+2),'#d2edff')
        poly([(362,421),(420,330),(492,378),(588,257),(679,368),(742,314),(900,423),(900,450),(362,450)],'#455888')
        poly([(362,430),(479,394),(590,423),(702,370),(835,419),(902,392),(902,450),(362,450)],'#5a77a2')
        line([(631,148),(631,451)],'#637da4',8);line([(363,354),(902,354)],'#637da4',8)
        # Ceiling garlands.
        line([(35,123),(190,153),(345,121),(515,148),(690,120),(852,147),(1024,117),(1245,153)],'#142139',4)
        for x,y in [(95,136),(190,151),(280,136),(430,136),(515,146),(605,131),(770,132),(852,146),(957,130),(1105,131),(1190,145)]:
            oval((x-10,y-10,x+10,y+10),'#716c6c');oval((x-5,y-5,x+5,y+5),'#ffdf9d')
        # Wooden floor with perspective boards.
        poly([(0,564),(1280,564),(1280,800),(0,800)],'#65536c');line([(0,566),(1280,566)],'#b89998',7)
        for y in [608,664,744]:line([(0,y),(1280,y)],'#4d4058',3)
        for x in range(-300,1600,170):line([(640+(x-640)*.64,568),(x,800)],'#4d4058',2)
        # Left bookcase.
        box((76,207,302,461),'#202d49',16,'#7c8da9',4)
        for y in [270,351,431]:
            box((80,y,298,y+9),'#8698b1',3)
            for j,c in enumerate(['#e09c9d','#80cbbc','#b19fe6','#edcd8f']):
                x=99+j*43
                if y==270:
                    box((x,y-51,x+25,y),c,4);box((x+5,y-57,x+20,y-49),'#223754',3);line([(x+5,y-21),(x+20,y-21)],'#ffffff',2)
                elif y==351:
                    box((x,y-50+j*4,x+25,y),c,2);line([(x+6,y-42+j*4),(x+6,y-8)],'#ffffff',2)
                else:oval((x,y-31,x+30,y),c);box((x+7,y-39,x+23,y-28),'#cad8db',3)
        # Aquarium and living plants.
        box((963,222,1187,380),'#1c2c48',18,'#7b99b7',4);box((977,237,1172,365),'#315d74',12)
        oval((1015,266,1072,295),'#f0ac86');poly([(1070,280),(1088,268),(1088,294)],'#e8a77d');oval((1025,273,1031,279),'#1b2545')
        for x in [1002,1115,1145]:
            line([(x,357),(x-8,326),(x+4,299)],'#81cdb5',8)
            oval((x-20,318,x,330),'#81cdb5');oval((x,300,x+19,312),'#8de0bd')
        for x,y in [(1093,275),(1104,248),(992,283)]:oval((x,y,x+8,y+8),None,'#a0e0e1',2)
        # Ground shadow, rug, workbench, beanbag and training apparatus.
        oval((310,503,845,626),'#302d4c');oval((334,505,817,599),['#79a99c','#a59bd0','#cea57f'][style], '#cce7c9',4)
        box((58,486,278,575),'#bb8890',14,'#423d5a',4);box((72,472,264,502),'#edb4a1',12)
        for x in [82,239]:box((x,561,x+16,608),'#403c57',3)
        oval((86,480,134,505),'#45516c');oval((96,483,126,495),'#eac789')
        box((930,463,1191,556),'#9d91c3',40,'#313449',4);box((942,459,1178,499),'#c4b4e8',24);box((1067,444,1160,478),'#e5d4f4',20)
        box((944,551,962,595),'#30374e',4);box((1160,551,1178,595),'#30374e',4)
        # A tiny door to the adventure garden.
        box((800,333,914,527),'#1e2a46',50,'#6c8a9e',6);box((814,348,900,514),'#6b7f8c',42)
        oval((871,443,881,453),'#ffe1a2')
        # Upgrades visibly add furniture, not just a counter.
        if style>=1:
            box((329,405,403,528),'#8778ba',14);oval((339,417,393,470),'#1b294a');oval((351,429,382,459),'#a4efd4');box((341,485,393,494),'#f9d791',4)
        if style>=2:
            for x in [35,1200]:
                box((x,485,x+45,543),'#c5a2b4',10)
                for dx,dy in [(-8,-62),(5,-80),(20,-59)]:
                    line([(x+22,490),(x+dx+22,490+dy)],'#88beae',6);oval((x+dx+9,470+dy,x+dx+36,493+dy),'#a2e2bc')
        save(im,f'room-{style}.png')
    for scene in range(3):
        im,d=picture((1280,800));box,oval,poly,line=paint(d)
        skies=[('#102e46','#54637a'),('#252546','#786095'),('#251c43','#79557e')]
        a,b=skies[scene];a=tuple(int(a[i:i+2],16) for i in (1,3,5));b=tuple(int(b[i:i+2],16) for i in (1,3,5))
        for y in range(800):
            t=y/800;box((0,y,1280,y+1),tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3)))
        oval((533,130,733,330),'#d5dcbe' if scene==0 else '#d2c1ec');oval((560,143,741,309),skies[scene][0])
        for i in range(90):
            x=rng.randrange(1280);y=rng.randrange(130,410);sz=rng.choice([1,1,2]);oval((x,y,x+sz,y+sz),'#b9d2dd')
        for j,color in enumerate(['#344867','#2c3e5b','#23344c']):
            points=[(0,600)]+[(x,350+rng.randint(-90,90)+j*65) for x in range(-80,1400,140)]+[(1280,700)]
            poly(points,color)
        if scene==0:
            for x in [10,95,1140,1240]:
                box((x,185,x+32,583),'#172d40',15)
                for y,w in [(210,132),(290,160),(370,190)]:poly([(x+17,y-95),(x-w/2,y+58),(x+w/2,y+58)],'#1b3e49')
        elif scene==1:
            for x in [55,165,1080,1180]:
                box((x,275,x+42,560),'#585273',8,'#82789a',3);box((x-12,264,x+55,287),'#9282a6',4);box((x-12,542,x+55,567),'#403d5b',3)
        else:
            for x in [18,100,1130,1220]:
                poly([(x,582),(x-22,395),(x+27,314),(x+56,419),(x+44,582)],'#6a679a','#a6a8db',3)
                line([(x+27,332),(x+20,562)],'#9ad9ed',3)
        oval((-180,480,1480,950),'#24374d');oval((82,500,1198,760),'#566976' if scene==0 else '#685e80')
        oval((112,516,1168,719),'#354f5d' if scene==0 else '#454064','#99c5bd',3)
        oval((171,539,1109,689),None,'#658e96',2);line([(642,527),(642,718)],'#658e96',2)
        for x,y in [(120,500),(1135,500),(50,568),(1210,568)]:
            box((x,y,x+28,y+41),'#705274',8);oval((x-9,y-20,x+38,y+12),'#e8b7bd' if scene==0 else '#b5adf1','#e8dcba',2)
            oval((x+1,y-11,x+7,y-5),'#fff4cd');oval((x+19,y-3,x+25,y+3),'#fff4cd')
        save(im,f'arena-{scene}.png')
    # Three unmistakably different rivals, all transparent and editable sprites.
    for rival in range(3):
        im,d=picture((256,256));box,oval,poly,line=paint(d);ink='#172b42'
        if rival==0:
            for x in [75,143]:box((x,204,x+38,242),'#82ae89',12,ink,3)
            for x in [34,193]:oval((x,128,x+31,190),'#80b78d',ink,3)
            oval((54,68,204,224),'#9fd7a5',ink,4)
            poly([(42,98),(64,46),(100,23),(162,28),(201,61),(218,105)],'#e59391',ink,4)
            for x,y in [(83,58),(131,42),(163,73)]:oval((x,y,x+23,y+14),'#ffe5c8')
            for x in [83,143]:oval((x,114,x+32,154),'#fff7df',ink,3);oval((x+10,125,x+22,147),ink)
            d.arc((102*S,149*S,161*S,183*S),0,180,fill=ink,width=5*S)
            for x in [65,177]:oval((x,167,x+20,176),'#e4a49d')
        elif rival==1:
            for x in [69,155]:poly([(x,96),(x-4,12),(x+43,43),(x+42,113)],'#f0ca84',ink,4);poly([(x+8,77),(x+7,29),(x+29,50)],'#d9988a')
            poly([(66,79),(193,79),(213,148),(174,218),(81,219),(41,147)],'#efc77d',ink,4)
            oval((78,181,177,228),'#fff1cc',ink,3)
            for x in [69,149]:oval((x,113,x+39,153),'#fff6e0',ink,3);oval((x+17,124,x+29,147),'#2d6385')
            poly([(115,150),(141,150),(128,165)],ink)
            for x in [55,171]:poly([(x,194),(x+15,191),(x+28,235),(x+2,235)],'#ca8d78',ink,3)
            poly([(191,194),(239,164),(225,136),(246,113),(251,171),(221,209)],'#96d7e6',ink,3)
        else:
            poly([(128,25),(199,64),(225,143),(190,219),(68,219),(31,143),(56,65)],'#56618b',ink,5)
            for x in [40,175]:poly([(x,119),(x-23,171),(x+12,210),(x+40,168)],'#8c91b2',ink,4)
            for x in [79,147]:poly([(x,203),(x-6,243),(x+37,243),(x+35,203)],'#475476',ink,4)
            poly([(83,56),(83,14),(107,36),(128,0),(150,36),(176,13),(171,60)],'#a3e5e9',ink,3)
            for x in [75,143]:poly([(x,103),(x+37,109),(x+30,133),(x+5,128)],'#c0f8e5',ink,3)
            line([(90,157),(109,165),(126,158),(144,166),(166,155)],'#c0f8e5',5)
            poly([(128,182),(148,196),(128,218),(108,196)],'#a3f4da',ink,3)
            line([(71,73),(85,91)],'#b4f5eb',3);line([(184,139),(197,158),(189,174)],'#b4f5eb',3)
        save(im,f'rival-{rival}.png')
    # Small native sprites used by the scene animator.
    for name in ['spark','heart','shield','bolt','food','trophy','bubble','orb','gift']:
        im,d=picture((96,96));box,oval,poly,line=paint(d)
        if name=='spark':poly([(48,2),(57,35),(91,48),(57,57),(48,93),(36,57),(3,48),(36,35)],'#ffe8ab')
        elif name=='heart':
            oval((11,14,53,57),'#f4a3b5');oval((43,14,85,57),'#f4a3b5');poly([(12,40),(84,40),(48,84)],'#f4a3b5')
        elif name=='shield':
            poly([(48,7),(83,21),(78,59),(48,88),(18,59),(13,21)],'#a0daee','#dcf5ff',4);line([(48,24),(48,66)],'#eaf9ff',5);line([(31,45),(65,45)],'#eaf9ff',5)
        elif name=='bolt':poly([(55,1),(15,51),(40,51),(30,94),(83,35),(55,35)],'#ffdc87','#fff3c5',3)
        elif name=='food':
            oval((12,49,84,83),'#ce8393','#382f4f',3);box((12,43,84,62),'#ecafae',11,'#382f4f',3)
            for x,y in [(24,41),(45,32),(58,40)]:oval((x,y,x+19,y+18),'#f0d59a','#a67e72',2)
        elif name=='trophy':
            box((31,12,66,54),'#f5d080',12,'#6b5264',3);d.arc((12*S,12*S,42*S,51*S),80,280,fill='#f5d080',width=7*S);d.arc((55*S,12*S,85*S,51*S),-100,100,fill='#f5d080',width=7*S);box((44,51,53,73),'#f5d080',2);box((26,73,72,83),'#d1a268',5)
        elif name=='bubble':oval((18,18,78,78),None,'#b5f3df',4);oval((31,29,42,39),'#ecfff4')
        elif name=='orb':
            for j in range(20,0,-1):oval((48-j*2,48-j*2,48+j*2,48+j*2),(115,213,205,int(8+7*(20-j))))
            oval((38,38,58,58),'#defae1')
        elif name=='gift':
            box((15,35,82,85),'#bca5ed',7,'#493b65',3);box((11,27,86,44),'#dac3fb',6,'#493b65',3);box((42,28,54,85),'#ffdc9a',1);oval((29,12,48,30),None,'#ffdc9a',4);oval((48,12,67,30),None,'#ffdc9a',4)
        save(im,name+'.png')
    # Reuse the room as the workbench backdrop; creator UI stays independently editable.


def make_music(folder):
    folder=Path(folder);rate=22050
    for mode in ['home','battle']:
        beat=.4 if mode=='home' else .3;duration=beat*32;n=int(duration*rate);samples=[0.0]*n
        chords=[[60,64,67,71],[57,60,64,67],[53,57,60,64],[55,59,62,67]]
        melody=[0,2,1,3,2,1,0,2,1,3,2,0,2,1,3,2]*2
        def tone(midi,start,length,amp,soft=True):
            f=440*2**((midi-69)/12)
            for i in range(min(int(length*rate),n-int(start*rate))):
                t=i/rate;env=(1-math.exp(-t*75))*math.exp(-t*(3 if soft else 7));phase=2*math.pi*f*t
                sound=math.sin(phase)+.23*math.sin(phase*2)+.1*math.sin(phase*3)
                idx=(int(start*rate)+i)%n;samples[idx]+=amp*env*sound
        for step in range(32):
            chord=chords[step//8];tone(chord[melody[step]]+12,step*beat,beat*1.75,.075,mode=='home')
            if step%2==0:tone(chord[step%4]-12,step*beat,beat*1.8,.06)
            if mode=='battle' and step%2==0:
                for i in range(int(.1*rate)):
                    t=i/rate;idx=int(step*beat*rate)+i
                    if idx<n:samples[idx]+=.09*math.sin(2*math.pi*(95*t-260*t*t))*math.exp(-t*35)
        audio=array.array('h',(int(max(-.95,min(.95,x))*32767) for x in samples))
        with wave.open(str(folder/f'{mode}-loop.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(audio.tobytes())
