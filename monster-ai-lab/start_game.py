"""Launch the prepared classroom bundle. Python 3.10+, no pip packages."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import webbrowser

root = Path(__file__).resolve().parent / 'web'
if not (root / 'vendor' / 'scratch-vm.js').exists():
    raise SystemExit('Сначала выполните npm ci и npm run build, либо скачайте готовый Monster_AI_Lab_Classroom.zip.')
handler = partial(SimpleHTTPRequestHandler, directory=str(root))
# Python already knows .mjs on supported platforms, but set it explicitly for Windows.
SimpleHTTPRequestHandler.extensions_map.update({'.mjs': 'text/javascript', '.wasm': 'application/wasm'})
server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
address = f'http://127.0.0.1:{server.server_port}'
print('MONSTER AI LAB:', address, '\nОставьте это окно открытым. Ctrl+C — закончить игру.')
threading.Timer(.6, lambda: webbrowser.open(address)).start()
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    server.server_close()
