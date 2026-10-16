from pathlib import Path
from copy import deepcopy
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from PIL import Image

ROOT=Path(__file__).parent
SOURCE='/workspace/attachments/afaf0380-61ff-4f57-86ab-da84417dd2c2/Ochet_programmirovanie_2.docx'
doc=Document(SOURCE)
# Preserve the original title page, general assignment and styles.
paras=list(doc.paragraphs)
body_style=deepcopy(paras[42]._p.pPr)
code_style=deepcopy(paras[84]._p.pPr)
caption_style=deepcopy(paras[80]._p.pPr)
listing_style=deepcopy(paras[83]._p.pPr)
conclusion_style=deepcopy(paras[398]._p.pPr)

def replace_paragraph(index,text):
    p=paras[index]
    rpr=deepcopy(p.runs[0]._r.rPr) if p.runs else None
    p.clear()
    r=p.add_run(text)
    if rpr is not None:r._r.insert(0,rpr)
    return p

# Keep run formatting and alignment of title fields.
for run in paras[25].runs:
    run.text=run.text.replace('варианта 5','варианта 2')
replace_paragraph(23,'Направленность (профиль)\t Искусственный интеллект и математическое моделирование')
replace_paragraph(28,'Обучающаяся\t\t             _____________________       Шевченко О.Н.')
# Remove the old variant's work and its drawings.
for p in paras[76:]:p._p.getparent().remove(p._p)
# Isolate the main work after the preserved assignment.

def ptext(text,kind='body',bold=False):
    p=doc.add_paragraph()
    src={'body':body_style,'code':code_style,'caption':caption_style,
         'listing':listing_style,'conclusion':conclusion_style}[kind]
    p._p.insert(0,deepcopy(src))
    r=p.add_run(text)
    r.font.name='Courier New' if kind=='code' else 'Times New Roman'
    r.font.size=Pt(12 if kind=='code' else 14)
    r.bold=bold
    pf=p.paragraph_format
    pf.widow_control=True
    if kind=='code':
        pf.alignment=WD_ALIGN_PARAGRAPH.LEFT
        pf.first_line_indent=Cm(0)
        pf.left_indent=Cm(0)
        pf.space_before=Pt(0);pf.space_after=Pt(0)
        pf.line_spacing=1
        if text.rstrip().endswith(':') or text.lstrip().startswith('@'):
            pf.keep_with_next=True
    if kind=='listing':pf.keep_with_next=True
    return p

def heading(text):
    p=ptext(text,bold=True)
    p.paragraph_format.keep_with_next=True
    return p

def figure(n,title,maxwidth=16,maxheight=18):
    image=ROOT/'assets'/f'figure{n}.png'
    width,height=Image.open(image).size
    cmwidth=min(maxwidth,maxheight*width/height)
    p=doc.add_paragraph()
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next=True
    p.paragraph_format.space_before=Pt(8)
    p.paragraph_format.space_after=Pt(0)
    run=p.add_run();run.add_picture(str(image),width=Cm(cmwidth))
    pic=run._r.xpath('.//wp:docPr')[0]
    pic.set('descr',title)
    ptext(f'Рисунок {n} – {title}','caption')

def listing(n, filename):
    ptext(f'Листинг {n} – Код программы','listing')
    for line in (ROOT/'programs'/filename).read_text().splitlines():
        ptext(line,'code')
    doc.add_paragraph()

heading('1. Расчёт напольного покрытия')
ptext('Требуется вычислить площадь укладки напольного покрытия, исключив колонны и выступы. У объектов Floor должны быть поля length, width и obstacles. Площади вычисляются по вызову методов, а не сохраняются в полях. Метод tiles_count принимает размеры одной плитки и возвращает необходимое количество плиток. Разработан консольный интерфейс (см. рисунки 1, 2).')
ptext('Я реализовала композицию Floor и Obstacle: пол создаёт и хранит препятствия. Полная площадь равна length · width, рабочая площадь равна полной площади за вычетом суммарной площади препятствий. Количество плиток вычисляется как ceil(Sраб / (a · b)). Предполагается, что препятствия не пересекаются и расположены внутри пола; запас на подрезку и ширина швов не учитываются. Проверяются положительность размеров и допустимость суммарной площади исключений.')
ptext('Контрольный пример: пол 6 × 5 м; препятствия 0,5 × 0,5 м и 1 × 0,5 м; плитка 0,5 × 0,5 м. Получено: Sраб = 30 − 0,25 − 0,5 = 29,25 м²; N = ceil(29,25 / 0,25) = 117 шт.')
figure(1,'Результат работы программы расчёта напольного покрытия')
figure(2,'UML-диаграмма классов Floor и Obstacle')
listing(1,'task1_floor.py')

heading('2. Класс Book (Книга)')
ptext('Требуется создать класс Book, содержащий целое количество страниц. Реализовать перегрузку операторов +, −, *, /; при делении округлять результат до целого. Метод reading_time принимает скорость чтения в страницах в час и возвращает строку с длительностью чтения. Вызов экземпляра как функции перезаписывает количество страниц (см. рисунки 3, 4).')
ptext('Я реализовала проверку операндов: поддерживаются Book и конечные числа int/float, логические значения исключены. Число страниц неотрицательно и целочисленно. Для сложения, вычитания и умножения нецелый результат отклоняется; при делении применяется стандартный round Python (при равном удалении — к чётному целому). Отрицательный результат и деление на ноль запрещены. Неподдерживаемый тип приводит к NotImplemented и далее к TypeError. Исходные объекты при арифметических операциях не изменяются.')
ptext('Контрольный пример: 300 и 120 страниц; сложение — 420, вычитание — 180, умножение первой книги на 2 — 600, деление на 2 — 150. При скорости 30 страниц/час чтение 300 страниц занимает 10 часов. Вызов first(450) устанавливает 450 страниц.')
figure(3,'Результат работы программы с классом Book')
figure(4,'UML-диаграмма класса Book')
listing(2,'task2_book.py')

heading('3. Ансамбль моделей (Ensemble)')
ptext('Вариант 2 для профиля «Искусственный интеллект и математическое моделирование»: ансамбль состоит из базовых моделей Model. У модели заданы точность и время обучения. Требуется добавлять и удалять модели, вычислять среднюю точность и общее время обучения, определять оптимальное количество моделей для заданной точности. Разработаны консольный интерфейс, диаграмма классов и диаграмма последовательности (см. рисунки 5–7).')
ptext('Я реализовала композицию: метод add_model создаёт Model внутри Ensemble, а remove_model удаляет её по индексу. Точность задаётся в долях единицы [0; 1], время обучения — в минутах и не может быть отрицательным. Средняя точность равна сумме точностей, делённой на число моделей. Время последовательного обучения равно сумме времён отдельных моделей. Для пустого ансамбля обе итоговые характеристики равны нулю.')
ptext('Критерий оптимальности: минимальное число моделей в непустом подмножестве со средней точностью не ниже целевой. Модели упорядочиваются по убыванию точности; проверяются средние значения префиксов. При таком критерии достаточно одной лучшей модели, если её точность достигает цели; иначе подходящего подмножества нет. Это следствие того, что среднее не может превышать максимальный элемент. Рост фактической точности совместных предсказаний здесь не моделируется: в задании не заданы прогнозы моделей или правило голосования.')
ptext('Контрольный пример: точности 0,80; 0,90; 0,85 и времена 10; 20; 15 минут. Средняя точность — 85 %, общее время — 45 минут. Для цели 0,88 достаточно одной модели с точностью 0,90. После удаления второй модели средняя точность равна 82,5 %, время — 25 минут, цель 0,88 недостижима. На рисунке 5 повторяющиеся строки меню опущены; полный протокол запуска приложен к исходникам.')
figure(5,'Результат работы программы с ансамблем моделей',maxheight=19)
figure(6,'UML-диаграмма классов Ensemble и Model')
figure(7,'Диаграмма последовательности добавления модели и расчёта точности')
listing(3,'task3_ensemble.py')

heading('4. Класс Loss (Потери)')
ptext('Вариант 2 для профиля «Искусственный интеллект и математическое моделирование»: класс Loss хранит вещественное значение функции потерь, не меньшее нуля. Требуется реализовать +, −, *, /, проверку уменьшения потерь и обновление значения через вызов экземпляра как функции. Построены диаграмма класса и диаграмма последовательности сложения (см. рисунки 8–10).')
ptext('Я реализовала операции с Loss и конечными числами int/float. Результат каждой операции — новый объект Loss; отрицательные потери, бесконечность, NaN, логические значения и деление на ноль не допускаются. Метод is_converging(previous) возвращает True, когда текущее значение строго меньше предыдущего. Это проверка уменьшения за один шаг, а не доказательство математической сходимости последовательности. Метод __call__ проверяет новое значение и только затем обновляет поле value.')
ptext('Контрольный пример: для 0,8 и 0,2 получены сумма 1, разность 0,6, произведение 0,16 и частное 4. После вызова first(0.1) значение становится 0,1; относительно 0,2 потери уменьшились.')
figure(8,'Результат работы программы с классом Loss')
figure(9,'UML-диаграмма класса Loss')
figure(10,'Диаграмма последовательности сложения объектов Loss')
listing(4,'task4_loss.py')

heading('Проверка результатов')
ptext('Я проверила программы на Python 3 с помощью unittest: выполнены 15 тестов, все завершились успешно. Проверены расчёт площади и округление числа плиток вверх, пересчёт площади при изменении размеров, полностью исключённая площадь, арифметика Book и Loss с числами и экземплярами классов, время чтения, обновление значений, расчёты ансамбля до и после удаления модели, достижимая и недостижимая точность, пустой ансамбль. Проверены также некорректные типы, выход за допустимые диапазоны и деление на ноль. Для воспроизведения: python3 -m unittest discover -s programs -v из каталога комплекта работы.')
ptext('Вывод: я изучила и практически освоила принципы композиции объектов и перегрузки операторов в объектно-ориентированном программировании на Python. Реализовала расчёт напольного покрытия, класс Book, ансамбль моделей и класс Loss для второго варианта. Сформировала навыки проектирования классов с отношением «has-a», проверки типов и граничных значений, создания консольных интерфейсов. Освоила визуальное моделирование программных сущностей с помощью UML-диаграмм классов и последовательности. Корректность основных расчётов подтвердила контрольными примерами и автоматическими тестами.','conclusion')

# Remove unused image relationships, including old author screenshots.
used=set()
for element in doc._element.iter():
    for name in (qn('r:embed'),qn('r:link'),qn('r:id')):
        value=element.get(name)
        if value:used.add(value)
for rid, rel in list(doc.part.rels.items()):
    if rel.reltype.endswith('/image') and rid not in used:
        del doc.part.rels[rid]
doc.core_properties.author='Шевченко О.Н.'
doc.core_properties.last_modified_by='Шевченко О.Н.'
doc.core_properties.title='Лабораторная работа № 2. Вариант 2'
doc.core_properties.subject='Композиция и перегрузка операторов'
doc.core_properties.comments=''
output=ROOT/'ЛР2_Шевченко_ОН_вариант_2.docx'
doc.save(output)
print(output)
