"""Build three complete portable classroom archives, with deterministic ZIP entries."""
from pathlib import Path
import shutil,tempfile,zipfile,hashlib,json
R=Path(__file__).resolve().parents[1]

def tree(src,dest):shutil.copytree(R/src,dest,ignore=shutil.ignore_patterns('__pycache__'),dirs_exist_ok=True)
def file(src,dest):dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/src,dest)
def validate_project(folder):
 d=json.loads((folder/'game.json').read_text());names=[]
 for r in d['resources']['resources']:
  path=(folder/r['file']).resolve()
  assert path.is_relative_to(folder.resolve()),r['file']
  assert path.is_file(),r['file']
  names.append(r['name'])
 assert len(names)==len(set(names)),'duplicate resource names'
 for scene in d['layouts']:
  objects={o['name']:o for o in scene['objects']}
  assert len([i for i in scene['instances'] if i['name']=='MonsterEyes'])==2
  for o in objects.values():
   if o['type']=='Sprite':
    for animation in o['animations']:
     assert len(animation['directions'][0]['sprites'])==1
     assert animation['directions'][0]['sprites'][0]['image'] in names

out=R/'downloads';out.mkdir(exist_ok=True)
for kind in ['Demo','Student','Teacher']:
 with tempfile.TemporaryDirectory(prefix='protocol-package-') as temp:
  root=Path(temp)/('Monster_Protocol_'+kind);root.mkdir()
  tree('docs',root/'docs');tree('licenses',root/'licenses');file('LICENSE',root/'LICENSE');file('THIRD_PARTY.md',root/'THIRD_PARTY.md')
  if kind=='Teacher':
   tree('demo',root/'demo');tree('student-template',root/'student-template');tree('teacher',root/'teacher');validate_project(root/'demo');validate_project(root/'student-template')
   (root/'README.md').write_text('# Monster Protocol — комплект преподавателя\n\nГотовая демонстрация: `START_WINDOWS.bat` (Python 3.10+) или `python3 start_demo.py`.\nБез Python откройте `demo/game.json` в GDevelop и нажмите Предпросмотр.\n\n- Готовый проект: [demo/game.json](demo/game.json).\n- Основа ученика: [student-template/game.json](student-template/game.json).\n- [Подготовка класса](docs/TEACHER_START_RU.md).\n- [12 подробных занятий](docs/LESSONS_RU.md).\n- [Точные события](docs/EVENTS_RU.md).\n- [Подключение Teachable Machine](docs/AI_RU.md).\n- [Карточки учеников](docs/STUDENT_CARDS_RU.md).\n- [Проверки и ограничения](docs/VALIDATION_RU.md).\n\nРаздавайте детям отдельную копию всей папки student-template, а не демо и не один JSON.\nКамера и качество модели требуют проверки на школьном устройстве.\n',encoding='utf-8')
  else:
   project='student-template' if kind=='Student' else 'demo';tree(project,root/'project');validate_project(root/'project')
   (root/'START_HERE.txt').write_text('MONSTER PROTOCOL — '+kind+'\n\n'+('Откройте project/game.json в настольном GDevelop.\nЭто учебный шаблон: работают примеры тела и глаз вправо; остальное — задания курса.\n' if kind=='Student' else 'Для показа: START_WINDOWS.bat (нужен Python 3.10+) или python3 start_demo.py.\nБез Python: откройте project/game.json в GDevelop, нажмите Предпросмотр.\n')+'\nПапку целиком скопируйте на компьютер и только потом открывайте проект.\nКурс: docs/LESSONS_RU.md; точные события: docs/EVENTS_RU.md; ИИ: docs/AI_RU.md.\n',encoding='utf-8')
  if kind!='Student':
   tree('build/demo',root/'play');tree('teacher/cards',root/'cards');file('tools/start_demo.py',root/'start_demo.py');file('tools/START_WINDOWS.bat',root/'START_WINDOWS.bat')
  target=out/('Monster_Protocol_'+kind+'.zip')
  with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
   for p in sorted(root.rglob('*')):
    if p.is_file():
     info=zipfile.ZipInfo(str(p.relative_to(Path(temp))),(2026,10,19,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,p.read_bytes())
  with zipfile.ZipFile(target) as z:assert z.testzip() is None
  print(target.name,target.stat().st_size,'bytes; CRC and project resources OK')
checks={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('*.zip'))}
(out/'SHA256SUMS.txt').write_text(''.join(f'{v}  {k}\n' for k,v in checks.items()))
