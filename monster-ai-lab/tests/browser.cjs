const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
async function main(){
  const out=path.resolve(__dirname,'../test-results');fs.mkdirSync(out,{recursive:true});
  const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,
    args:['--no-sandbox','--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream']});
  try{
    const context=await browser.newContext({viewport:{width:1440,height:1050},permissions:['camera']});
    const page=await context.newPage();const errors=[],external=[],badResponses=[];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('request',r=>{if(new URL(r.url()).hostname!=='127.0.0.1')external.push(r.url());});
    page.on('response',r=>{if(r.status()>=400&&!r.url().endsWith('/favicon.ico'))badResponses.push(r.url()+': '+r.status());});
    await page.goto(process.env.LAB_URL||'http://127.0.0.1:8000');
    await page.waitForFunction(()=>window.monsterLab?.ready());
    await page.waitForTimeout(3400);
    const state=()=>page.evaluate(()=>window.monsterLab.state());
    async function click(key){
      await page.locator('[data-key="'+key+'"]').click();
      await page.waitForTimeout(120);
      await page.waitForFunction(()=>Number(window.monsterLab.state()['Ход'])===0);
    }
    await click('f');assert.equal(Number((await state())['Энергия']),70);
    await click('t');assert.equal(Number((await state())['Сила']),12);
    // Native Scratch sprite hit testing, not just HTML buttons.
    const bounds=await page.locator('#stage').boundingBox();
    await page.mouse.click(bounds.x+bounds.width*(65/480),bounds.y+bounds.height*(322/360));
    await page.waitForTimeout(500);assert.equal(Number((await state())['Энергия']),80);
    await page.keyboard.press('n');await page.locator('#answer').fill('Комета');await page.locator('#answer-form button').click();
    await page.waitForFunction(()=>window.monsterLab.state()['Имя']==='Комета');
    assert.equal(await page.locator('#ask').isHidden(),true,'name prompt closes after answering');
    await page.screenshot({path:path.join(out,'laboratory.png'),fullPage:true});
    await click('b');assert.equal(Number((await state())['Сцена']),1);
    await click('a');assert.equal(Number((await state())['Здоровье врага']),46);
    await click('d');assert.equal(Number((await state())['Здоровье']),87);
    await page.screenshot({path:path.join(out,'arena.png'),fullPage:true});
    await page.locator('#camera-toggle').click();
    await page.waitForFunction(()=>document.getElementById('camera-toggle').textContent==='Выключить камеру',{},{timeout:60000});
    await page.waitForFunction(()=>document.getElementById('ai-status').textContent.includes('Покажи одну руку'),{},{timeout:30000});
    assert.equal(await page.locator('#camera-placeholder').isHidden(),true);
    // A synthetic webcam has no hand: actual local neural inference must abstain.
    await page.waitForTimeout(1200);
    await page.locator('#camera-toggle').click();
    assert.equal(await page.evaluate(()=>document.getElementById('camera').srcObject),null);
    await page.locator('#project-file').setInputFiles(path.resolve(__dirname,'../web/game/Monster_AI_Lab.sb3'));
    await page.waitForFunction(()=>window.monsterLab.ready() && Number(window.monsterLab.state()['Сцена'])===0 && window.monsterLab.state()['Имя']==='Искрик');
    await page.setViewportSize({width:390,height:844});
    await page.screenshot({path:path.join(out,'mobile.png'),fullPage:true});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'no horizontal overflow');
    assert.deepEqual(errors,[],'no page errors');assert.deepEqual(badResponses,[],'no failed asset requests');assert.deepEqual(external,[],'all neural models and game assets served locally');
    console.log('PASS: Chromium — render, HTML/Scratch clicks, rename, battle, local neural model + fake webcam inference, camera stop, mobile layout.');
    console.log('No external network requests. Physical hand recognition still needs a real camera check.');
  }finally{await browser.close();}
}
main().catch(error=>{console.error(error);process.exitCode=1;});
