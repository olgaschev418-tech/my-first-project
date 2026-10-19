"""Run the exported GDevelop game locally, opening the default browser."""
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import argparse,threading,webbrowser
p=argparse.ArgumentParser();p.add_argument('--no-browser',action='store_true');p.add_argument('--port',type=int,default=8011);a=p.parse_args()
root=Path(__file__).resolve().parent/'play'
if not (root/'index.html').is_file():raise SystemExit('Не найдена папка play. Распакуйте весь архив, не запускайте файл внутри ZIP.')
try:
    server=ThreadingHTTPServer(('127.0.0.1',a.port),partial(SimpleHTTPRequestHandler,directory=str(root)))
except OSError as error:
    raise SystemExit('Порт занят или недоступен. Закройте предыдущий запуск либо запустите с --port 8012. '+str(error))
url=f'http://127.0.0.1:{server.server_port}/'
print('MONSTER PROTOCOL — локальная игра. Закройте окно терминала или нажмите Ctrl+C для остановки.',flush=True)
print('Адрес для этого запуска: '+url,flush=True)
if not a.no_browser:threading.Timer(.5,lambda:webbrowser.open(url)).start()
try:server.serve_forever()
except KeyboardInterrupt:pass
finally:server.server_close()
