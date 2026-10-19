// Regression for cmd.exe reading LF-only batch files as truncated commands.
const fs=require('node:fs');const assert=require('node:assert/strict');
const bytes=fs.readFileSync('tools/START_WINDOWS.bat');
assert(bytes.every(b=>b<128),'Launcher is ASCII without an encoding-dependent BOM');
const text=bytes.toString('ascii');assert(!/(?<!\r)\n/.test(text),'Every LF must be preceded by CR');
assert(!/\r(?!\n)/.test(text),'No stray CR');
assert(text.endsWith('\r\n'));
const lines=text.split('\r\n');
assert(lines.includes('py -3 "%~dp0start_demo.py"'));
assert(lines.includes('python "%~dp0start_demo.py"'));
assert(lines.some(l=>l.includes('sys.version_info < (3, 10)')));
const labels=new Set(lines.filter(l=>l.startsWith(':')).map(l=>l.slice(1)));
for(const l of lines)for(const m of l.matchAll(/\bgoto ([a-z_]+)/gi))assert(labels.has(m[1]),'Missing label '+m[1]);
console.log('PASS: ASCII/CRLF Windows launcher, quoted paths, interpreter version checks, valid goto labels.');
