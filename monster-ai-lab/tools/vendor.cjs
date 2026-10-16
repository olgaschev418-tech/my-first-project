const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const out = path.join(root, 'web/vendor');
fs.mkdirSync(out, {recursive: true});
for (const [source, dest] of [
  ['scratch-vm/dist/web/scratch-vm.js', 'scratch-vm.js'],
  ['scratch-render/dist/web/scratch-render.js', 'scratch-render.js'],
  ['scratch-storage/dist/web/scratch-storage.min.js', 'scratch-storage.js'],
]) fs.copyFileSync(path.join(root, 'node_modules', source), path.join(out, dest));
fs.cpSync(path.join(root, 'node_modules/@mediapipe/hands'), path.join(out, 'hands'), {recursive: true});
fs.cpSync(path.join(root, 'node_modules/scratch-storage/dist/web/chunks'), path.join(root,'web/chunks'), {recursive:true});
fs.copyFileSync(path.join(root, 'node_modules/scratch-storage/dist/web/scratch-storage.min.js.LICENSE.txt'), path.join(out, 'scratch-storage.min.js.LICENSE.txt'));
// Preserve transitive notices when distributing prebuilt upstream bundles.
const notices=path.join(root,'licenses');fs.mkdirSync(notices,{recursive:true});
function copyLicenses(dir,prefix=''){
  for(const entry of fs.readdirSync(dir,{withFileTypes:true})){
    if(entry.name.startsWith('.'))continue;
    const full=path.join(dir,entry.name);
    if(entry.isDirectory()){
      if(entry.name.startsWith('@')||entry.name==='node_modules')copyLicenses(full,prefix);
      else {
        const name=(prefix+entry.name).replace(/[^a-z0-9._-]/gi,'_');
        for(const file of fs.readdirSync(full)){
          if(/^(license|copying|notice)(\.|$)/i.test(file)&&fs.statSync(path.join(full,file)).isFile())fs.copyFileSync(path.join(full,file),path.join(notices,name+'-'+file));
        }
        if(fs.existsSync(path.join(full,'node_modules')))copyLicenses(path.join(full,'node_modules'),name+'-');
      }
    }
  }
}
copyLicenses(path.join(root,'node_modules'));
console.log('Scratch engine, renderer and local MediaPipe neural models copied.');
