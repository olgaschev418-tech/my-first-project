"""Повторная генерация иллюстраций: нужны Pillow и Graphviz."""
from pathlib import Path
import html
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'assets'
A.mkdir(exist_ok=True)
MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def screenshot(text, name):
    font = ImageFont.truetype(MONO, 25)
    lines = text.rstrip().splitlines()
    width = max(int(font.getlength(line)) for line in lines) + 48
    image = Image.new('RGB', (width, len(lines) * 35 + 40), '#101010')
    draw = ImageDraw.Draw(image)
    for i, line in enumerate(lines):
        draw.text((24, 17 + 35 * i), line, font=font, fill='white')
    image.save(A / f'{name}.png')


def execute(filename):
    result = subprocess.run([sys.executable, str(ROOT / 'programs' / filename)],
                            capture_output=True, text=True, check=True)
    (A / (filename + '.txt')).write_text(result.stdout, encoding='utf-8')
    return result.stdout


screenshot(execute('task1_employees.py').replace(' -> ', '\n  → '), 'figure1')
screenshot(execute('task2_layers.py'), 'figure3')
text = execute('analytics_core.py')
prefix, remaining = text.split('Подбор k по LOO MSE:', 1)
# The full, unabridged output is also retained as a text file.
screenshot(prefix, 'figure5')
main, journal = remaining.split('Журнал:', 1)
screenshot('Подбор k по LOO MSE:' + main, 'figure6')
screenshot('Журнал:' + journal, 'figure11')

# Export a real report through the implementation, not a handwritten fixture.
sys.path.insert(0, str(ROOT / 'programs'))
from analytics_core import HybridAnalyzer
analyzer = HybridAnalyzer(metadata={'author': 'Шевченко О.Н.'})
analyzer.load_data([1, 2, 3, 4, 5], [100, 200, 300, 400, 500])
analyzer.tune_k([1, 2, 3])
analyzer.export_report(analyzer.analyze(6, 300), ROOT / 'example_report.json')


def label(name, attributes, methods):
    def rows(items):
        if not items:
            return '<TR><TD> </TD></TR>'
        return ''.join('<TR><TD ALIGN="LEFT">' + html.escape(s)
                       + '</TD></TR>' for s in items)
    return ('<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" '
            'CELLPADDING="7"><TR><TD><B>' + name + '</B></TD></TR>'
            '<HR/>' + rows(attributes) + '<HR/>' + rows(methods) + '</TABLE>>')


def graph(name, classes, edges, extra=''):
    dot = ('digraph G { graph [rankdir=BT, bgcolor="white", '
           'pad="0.15", nodesep="0.25", ranksep="0.6"]; '
           'node [shape=plain, fontname="DejaVu Sans", fontsize=12]; '
           'edge [arrowhead=empty, arrowsize=1.2];\n')
    for key, (title, attrs, methods) in classes.items():
        dot += key + ' [label=' + label(title, attrs, methods) + '];\n'
    for child, parent in edges:
        dot += f'{child} -> {parent};\n'
    dot += extra + '\n}'
    path = A / (name + '.dot')
    path.write_text(dot, encoding='utf-8')
    subprocess.run(['dot', '-Tpng', '-Gdpi=180', str(path),
                    '-o', str(A / (name + '.png'))], check=True)


graph('figure2', {
    'e': ('Employee', ['- _ids: Iterator[int]', '+ id: int'],
          ['+ __init__(): None']),
    'm': ('ManagerSkills', [], ['+ work(): str']),
    'd': ('DeveloperSkills', [], ['+ work(): str']),
    'manager': ('Manager', [], []),
    'developer': ('Developer', [], []),
    'lead': ('TeamLead', [], ['+ work(): str'])},
    [('manager', 'e'), ('manager', 'm'), ('developer', 'e'),
     ('developer', 'd'), ('lead', 'e'), ('lead', 'm'), ('lead', 'd')])

graph('figure4', {
    'l': ('Layer', ['- _ids: Iterator[int]', '+ id: int'],
          ['+ __init__(): None']),
    'd': ('DenseLayer', [], ['+ forward(): str', '+ backward(): str']),
    'c': ('ConvolutionalLayer', [], ['+ forward(): str', '+ backward(): str']),
    'dense': ('Dense', [], []), 'conv': ('Conv', [], [])},
    [('dense', 'l'), ('dense', 'd'), ('conv', 'l'), ('conv', 'c')])

# Mixin details are split into two panels for legibility.
graph('figure7a', {
    'v': ('ValidationMixin', [], [
        '+ validate_number(value: int | float): float',
        '+ validate_data(xs: list, ys: list): tuple[list, list]']),
    'c': ('CachingMixin', ['- _cache: dict'], [
        '+ __init__(**kwargs): None',
        '+ cached(key: tuple, operation: Callable): float'])}, [],
    '{ rank=same; v; c; }')
graph('figure7b', {
    'l': ('LoggingMixin', ['+ events: list[str]'], [
        '+ __init__(**kwargs): None', '+ log(message: str): None']),
    'r': ('ReportMixin', [], [
        '+ export_report(report: dict, path: str | Path | None): str'])}, [],
    '{ rank=same; l; r; }')
# Combine the two UML panels vertically at matching scale.
panels = [Image.open(A / f'figure7{x}.png').convert('RGB') for x in 'ab']
width = max(p.width for p in panels)
height = sum(p.height for p in panels) + 35
canvas = Image.new('RGB', (width, height), 'white')
y = 0
for panel in panels:
    canvas.paste(panel, ((width - panel.width) // 2, y))
    y += panel.height + 35
canvas.save(A / 'figure7.png')

classes = {
 'base': ('BaseComponent', [
     '- _ids: Iterator[int]', '+ id: int', '+ metadata: dict',
     '+ init_trace: list[str]'], [
     '+ __init__(metadata: dict | None, **kwargs): None',
     '+ describe(): str']),
 'val': ('ValidationMixin', [], ['Методы: рисунок 7']),
 'cache': ('CachingMixin', [], ['Методы: рисунок 7']),
 'log': ('LoggingMixin', [], ['Методы: рисунок 7']),
 'report': ('ReportMixin', [], ['Методы: рисунок 7']),
 'ml': ('MLModel', ['- _xs: list[float]', '- _ys: list[float]',
                    '+ k: int', '- _fitted: bool'], [
     '+ __init__(**kwargs): None', '+ describe(): str',
     '+ load_data(xs: list, ys: list): None', '+ fit(k: int): MLModel',
     '- _knn(x: float, xs: list, ys: list, k: int): float',
     '+ predict(x: float): float',
     '+ metrics(xs: list, ys: list): dict[str, float]',
     '+ tune_k(candidates: list[int]): tuple[int, dict]']),
 'eco': ('EconomicIndicator', [], [
     '+ __init__(**kwargs): None', '+ describe(): str',
     '+ roi(revenue: float, cost: float): float',
     '+ interpret(roi: float): str']),
 'hybrid': ('HybridAnalyzer', [], [
     '+ __init__(**kwargs): None', '+ describe(): str',
     '+ analyze(x: float, cost: float): dict'])}
edges = [('ml', p) for p in ['val', 'cache', 'log', 'report', 'base']]
edges += [('eco', p) for p in ['val', 'log', 'report', 'base']]
edges += [('hybrid', 'ml'), ('hybrid', 'eco')]
# Detailed business classes; complete mixin inheritance is on figure 9.
graph('figure8', {k: v for k, v in classes.items()
                  if k in ['base', 'ml', 'eco', 'hybrid']},
      [('ml', 'base'), ('eco', 'base'),
       ('hybrid', 'ml'), ('hybrid', 'eco')])
# Compact overview shows every actual direct inheritance relation.
overview = {k: (v[0], [], []) for k, v in classes.items()}
graph('figure9', overview, edges)


def sequence():
    names = ['main', 'h: HybridAnalyzer', 'Родители по MRO', 'JSON-файл']
    xs = [120, 630, 1170, 1660]
    messages = [
        (0, 1, '«create» HybridAnalyzer(metadata)', False),
        (1, 2, 'super().__init__(**kwargs)', False),
        (2, 1, 'id, metadata, cache, events', True),
        (0, 1, 'load_data(xs, ys)', False),
        (1, 2, 'validate_data(xs, ys)', False),
        (2, 1, 'проверенные данные', True),
        (0, 1, 'tune_k([1, 2, 3])', False),
        (1, 1, 'LOO → fit(k=2)', False),
        (0, 1, 'analyze(x=6, cost=300)', False),
        (1, 2, 'predict(6); roi(450, 300)', False),
        (2, 1, 'прогноз 450; ROI 50 %', True),
        (1, 0, 'report: dict', True),
        (0, 1, 'export_report(report, path)', False),
        (1, 3, 'write_text(JSON, UTF-8)', False),
        (1, 0, 'JSON-строка', True)]
    image = Image.new('RGB', (1800, 190 + len(messages) * 90), 'white')
    d = ImageDraw.Draw(image)
    font = ImageFont.truetype(REG, 23)
    for x, title in zip(xs, names):
        d.rectangle((x - 115, 18, x + 115, 80), outline='black', width=2)
        d.text((x, 48), title, anchor='mm', font=font, fill='black')
        for y in range(85, image.height - 15, 20):
            d.line((x, y, x, y + 10), fill='#555555', width=2)
    for i, (src, dst, text, reply) in enumerate(messages):
        y = 140 + i * 90
        a, b = xs[src], xs[dst]
        if a == b:
            d.line((a, y, a + 115, y, a + 115, y + 32, a, y + 32),
                   fill='black', width=2)
            d.polygon([(a, y + 32), (a + 14, y + 25),
                       (a + 14, y + 39)], fill='black')
            d.text((a + 15, y - 30), text, font=font, fill='black')
        else:
            direction = 1 if b > a else -1
            if reply:
                for start in range(a, b, 24 * direction):
                    d.line((start, y, start + 12 * direction, y),
                           fill='black', width=2)
            else:
                d.line((a, y, b, y), fill='black', width=2)
            d.polygon([(b, y), (b - 14 * direction, y - 7),
                       (b - 14 * direction, y + 7)], fill='black')
            d.text(((a + b) / 2, y - 10), text, anchor='mb',
                   font=font, fill='black')
    image.save(A / 'figure10.png')


sequence()
print('Generated execution transcripts, JSON and 11 report figures')
