import {loadProject,exportProject,gd_internal_logs} from 'gdcore-tools';
import {resolve} from 'node:path';
import {mkdir,rm} from 'node:fs/promises';
for(const name of ['demo','student-template']){
  const p=await loadProject(resolve(name,'game.json'));
  if(p.getLayoutsCount()!==4)throw Error('Expected 4 native scenes');
  await rm(resolve('build',name),{recursive:true,force:true});
  await mkdir(resolve('build',name),{recursive:true});
  exportProject(p,resolve('build',name));
  console.log('Exported native GDevelop project:',name);
  p.delete();
}
if(/^Error:|Bad resource created/m.test(gd_internal_logs))throw Error(gd_internal_logs);
console.log('GDevelop compilation: no expression errors or invalid resource types.');
