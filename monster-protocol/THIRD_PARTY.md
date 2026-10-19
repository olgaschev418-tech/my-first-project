# Ресурсы и лицензии

Новая графика монстров, оформление, учебные тексты и код адаптера/генератора подготовлены для этого комплекта. Их можно использовать и изменять в школе по MIT-лицензии из LICENSE. Набор Kenney из переписки не был приложен; его файлы/превью не копировались.

| Компонент | Версия | Лицензия / источник |
|---|---|---|
| GDevelop runtime | 5.6.269 | MIT, https://github.com/4ian/GDevelop ; полный NOTICE в licenses/GDevelop-runtime-LICENSE.txt и браузерном экспорте |
| gdcore-tools, только сборка | 2.0.0-gd-v5.6.269-autobuild | MIT, https://github.com/arthuro555/gdcore-tools |
| TensorFlow.js | 1.3.1 | Apache-2.0, https://github.com/tensorflow/tfjs |
| @teachablemachine/image | 0.8.5 | Apache-2.0, https://github.com/googlecreativelab/teachablemachine-community |
| DejaVu Sans | системный файл | Bitstream Vera / DejaVu, licenses/DejaVu-copyright.txt |
| Playwright, только тесты | 1.56.1 | Apache-2.0, https://github.com/microsoft/playwright |

Старые версии библиотек ML закреплены по официальной peer-зависимости @teachablemachine/image 0.8.5. Локальная игра предназначена для учебного использования; обновление библиотек требует повторной проверки импорта моделей. Библиотеки включены локально в assets обоих проектов, загружаются при открытии модели. Встроенная модель карточек обучена из синтетических RGB-примеров, персональных данных в ней нет. Исходный обучающий скрипт — tools/train-demo.cjs.

GDevelop и Teachable Machine — самостоятельные проекты; этот комплект не является их официальным продуктом. Облачные функции, тарифы и правила сайтов не входят в локальный комплект.
