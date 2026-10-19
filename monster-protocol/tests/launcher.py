"""An occupied port must never send the user to a previously launched copy."""
from pathlib import Path
import json, shutil, socket, subprocess, sys, tempfile
from urllib.request import urlopen

with tempfile.TemporaryDirectory(prefix='monster-launcher-') as temp:
    root = Path(temp)
    shutil.copy2(Path(__file__).resolve().parents[1] / 'tools/start_demo.py', root / 'start_demo.py')
    (root / 'play').mkdir()
    (root / 'play/index.html').write_text('THIS EXTRACTED COPY 2.0.1')
    (root / 'BUILD_INFO.json').write_text(json.dumps({'version': '2.0.1'}))
    with socket.socket() as occupied:
        occupied.bind(('127.0.0.1', 0))
        occupied.listen()
        port = occupied.getsockname()[1]
        child = subprocess.Popen([sys.executable, str(root / 'start_demo.py'), '--no-browser', '--port', str(port)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        try:
            lines = [child.stdout.readline() for _ in range(3)]
            url = lines[-1].split(': ', 1)[1].strip()
            assert f':{port}/' not in url, url
            assert url.endswith('/?version=2.0.1'), url
            with urlopen(url, timeout=5) as response:
                assert response.read() == b'THIS EXTRACTED COPY 2.0.1'
                assert 'no-store' in response.headers['Cache-Control']
            assert str(root) in lines[1]
        finally:
            child.terminate()
            child.wait(timeout=5)
print('PASS: occupied port opens this extracted copy at a new address; version and no-store headers verified.')
