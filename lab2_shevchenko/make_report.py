"""Сборка отчёта с точными абзацными параметрами Proga_otchet.docx."""
import argparse
import json
from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt
from docx.oxml.ns import qn
from PIL import Image

ROOT = Path(__file__).resolve().parent
DEFAULT = ROOT / 'templates' / 'report_format.docx'
parser = argparse.ArgumentParser()
parser.add_argument('--template', type=Path, default=DEFAULT)
args = parser.parse_args()
doc = Document(args.template)
paragraphs = list(doc.paragraphs)
# These Word properties and spacer paragraphs are copied from Proga_otchet.docx.
roles = {p.text[1:]: deepcopy(p._p.pPr) for p in paragraphs
         if p.text.startswith('@')}

for index, content in [
        (14, 'ЛАБОРАТОРНАЯ РАБОТА №2'),
        (16, 'Тема: «КОМПОЗИЦИЯ И ПЕРЕГРУЗКА ОПЕРАТОРОВ»'),
        (23, 'Направленность (профиль)\t Искусственный интеллект и '
             'математическое моделирование'),
        (28, 'Обучающаяся\t\t             _____________________       '
             'Шевченко О.Н.')]:
    p = paragraphs[index]
    formatting = deepcopy(p.runs[0]._r.rPr) if p.runs else None
    p.clear()
    r = p.add_run(content)
    if formatting is not None:
        r._r.insert(0, formatting)
for paragraph in paragraphs[43:]:
    paragraph._p.getparent().remove(paragraph._p)


def paragraph(role):
    p = doc.add_paragraph()
    p._p.insert(0, deepcopy(roles[role]))
    return p


def gap(role, keep=False):
    p = paragraph(role)
    if keep:
        p.paragraph_format.keep_with_next = True
    return p


def text(content, bold=False, kind='body'):
    p = paragraph(kind)
    r = p.add_run(content)
    r.font.name = 'Courier New' if kind == 'code' else 'Times New Roman'
    r.font.size = Pt(12 if kind == 'code' else 14)
    r.bold = bold
    if kind in ('body', 'conclusion'):
        p.paragraph_format.widow_control = True
    if kind == 'code':
        # Keep source indentation and the sample's single line spacing.
        if content.rstrip().endswith(':') or content.lstrip().startswith('@'):
            p.paragraph_format.keep_with_next = True
    return p


def heading(content, centered=False):
    if doc.paragraphs[-1].text.strip():
        gap('work_before' if centered else 'heading_before')
    p = paragraph('work_heading' if centered else 'heading')
    r = p.add_run(content)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)
    r.bold = True
    p.paragraph_format.keep_with_next = True
    gap('work_after' if centered else 'heading_after', keep=True)
    return p


def figure(number, caption, width=16, height=19):
    path = ROOT / 'assets' / f'figure{number}.png'
    w, h = Image.open(path).size
    role = 'image' if number in (1, 3, 5, 8) else 'diagram'
    p = paragraph(role)
    p.paragraph_format.keep_with_next = True
    r = p.add_run()
    r.add_picture(str(path), width=Cm(min(width, height * w / h)))
    r._r.xpath('.//wp:docPr')[0].set('descr', caption)
    text(f'Рисунок {number} – {caption}', kind='caption')


def listing(number, filename):
    gap('listing_before')
    p = text(f'Листинг {number} – Код программы', kind='listing')
    p.paragraph_format.keep_with_next = True
    for index, line in enumerate((ROOT / 'programs' / filename).read_text(
            encoding='utf-8').splitlines()):
        p = text(line, kind='code')
        if index < 4:
            p.paragraph_format.keep_with_next = True
    gap('listing_after')


# The content is preserved separately from its paragraph formatting.
blocks = json.loads((ROOT / 'report_content.json').read_text(encoding='utf-8'))
for block in blocks:
    kind = block['kind']
    if kind == 'goal':
        p = paragraph('goal')
        p.paragraph_format.page_break_before = True
        label, rest = block['text'].split(':', 1)
        p.add_run(label + ':').bold = True
        p.add_run(rest).bold = False
        for run in p.runs:
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
    elif kind == 'heading':
        heading(block['text'], centered=block['text'] == 'Ход работы')
    elif kind == 'figure':
        figure(block['number'], block['caption'], width=block['width'], height=19)
    elif kind == 'listing':
        listing(block['number'], block['file'])
    elif kind == 'conclusion':
        gap('conclusion_before')
        p = paragraph('conclusion')
        p.paragraph_format.widow_control = True
        label, rest = block['text'].split(':', 1)
        p.add_run(label + ':').bold = True
        p.add_run(rest).bold = False
        for run in p.runs:
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
    else:
        text(block['text'])

used = set()
for element in doc._element.iter():
    for attr in (qn('r:embed'), qn('r:link'), qn('r:id')):
        value = element.get(attr)
        if value:
            used.add(value)
for rid, relation in list(doc.part.rels.items()):
    if relation.reltype.endswith('/image') and rid not in used:
        del doc.part.rels[rid]
doc.core_properties.author = 'Шевченко О.Н.'
doc.core_properties.last_modified_by = 'Шевченко О.Н.'
doc.core_properties.title = 'Лабораторная работа № 2. Вариант 2'
doc.core_properties.subject = 'Композиция и перегрузка операторов'
doc.core_properties.comments = ''
output = ROOT / 'ЛР2_Шевченко_ОН_вариант_2.docx'
doc.save(output)
print(output)
