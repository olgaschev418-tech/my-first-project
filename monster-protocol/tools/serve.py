"""Local-only static server; no upload endpoints."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import argparse,os
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8010);p.add_argument('--root',default=str(Path(__file__).resolve().parents[1]/'build'));a=p.parse_args()
os.chdir(a.root)
print(f'Local classroom server, port {a.port}',flush=True)
ThreadingHTTPServer(('127.0.0.1',a.port),SimpleHTTPRequestHandler).serve_forever()
