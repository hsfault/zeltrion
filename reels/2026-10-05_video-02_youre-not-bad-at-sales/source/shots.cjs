const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async()=>{
  const times=process.argv.slice(2).map(Number);
  const browser=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--enable-webgl']});
  const page=await browser.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  page.on('console',m=>console.log('console:',m.text())); page.on('pageerror',e=>console.log('pageerror:',e.message));
  await page.goto('http://localhost:8123/index.html');
  await page.waitForFunction(()=>window.READY===true,null,{timeout:120000});
  for(const t of times){ const t0=Date.now(); await page.evaluate(t=>window.seek(t),t); await page.screenshot({path:`../shots/t${t.toFixed(2)}.png`}); console.log(t,Date.now()-t0,'ms'); }
  await browser.close();
})();
