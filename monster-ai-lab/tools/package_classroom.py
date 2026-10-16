"""Package already-built local assets; never fetch anything at game launch."""
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1]
output = root.parent / 'downloads' / 'Monster_AI_Lab_Classroom.zip'
output.parent.mkdir(exist_ok=True)
if not (root / 'web/vendor/hands/hand_landmark_full.tflite').exists():
    raise SystemExit('Run npm ci && npm run build first.')
paths = [root/'web', root/'docs', root/'licenses']
files = [root/n for n in ['start_game.py', 'START_WINDOWS.bat', 'README.md', 'THIRD_PARTY.md', 'LICENSE', 'QUICK_START_RU.txt']]
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for directory in paths:
        for file in sorted(directory.rglob('*')):
            if file.is_file() and file.suffix not in ['.map']:
                archive.write(file, 'Monster_AI_Lab/' + str(file.relative_to(root)))
    for file in files:
        archive.write(file, 'Monster_AI_Lab/' + file.name)
print(output, f'({output.stat().st_size/1024/1024:.1f} MB)')
