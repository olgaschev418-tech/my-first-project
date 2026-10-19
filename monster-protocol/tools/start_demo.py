"""Serve this extracted copy, without stale browser cache or port collisions."""
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import argparse, json, threading, webbrowser

p = argparse.ArgumentParser()
p.add_argument('--no-browser', action='store_true')
p.add_argument('--port', type=int, default=8011)
a = p.parse_args()
folder = Path(__file__).resolve().parent
root = folder / 'play'
if not (root / 'index.html').is_file():
    raise SystemExit('Не найдена папка play. Распакуйте весь архив, не запускайте файл внутри ZIP.')
info_path = folder / 'BUILD_INFO.json'
info = json.loads(info_path.read_text(encoding='utf-8')) if info_path.exists() else {}
version = info.get('version', '2.0.1')

class FreshFiles(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, max-age=0')
        super().end_headers()

handler = partial(FreshFiles, directory=str(root))
try:
    server = ThreadingHTTPServer(('127.0.0.1', a.port), handler)
except OSError:
    # Another extracted copy may still be running. Never reuse its server.
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
url = f'http://127.0.0.1:{server.server_port}/?version={version}'
print(f'MONSTER PROTOCOL {version} — ЖИВАЯ МАСТЕРСКАЯ', flush=True)
print('Папка этой игры: ' + str(folder), flush=True)
print('Адрес для этого запуска: ' + url, flush=True)
print('Закройте это окно или нажмите Ctrl+C для остановки.', flush=True)
if not a.no_browser:
    threading.Timer(.5, lambda: webbrowser.open(url)).start()
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    server.server_close()
