const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const [,,wi,wn,fps,total,outdir]=process.argv; const W=+wi,WN=+wn,FPS=+fps,TOT=+total;
(async()=>{
  const browser=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const page=await browser.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  page.on('pageerror',e=>console.log('pageerror:',e.message));
  await page.goto('http://localhost:8123/index.html'+(process.env.Q||''));
  await page.waitForFunction(()=>window.READY===true,null,{timeout:120000});
  const t0=Date.now(); let n=0;
  for(let f=W+(+(process.env.START||0)); f<TOT; f+=WN){
    await page.evaluate(([t,f])=>window.seek(t,f),[f/FPS,f]);
    await page.screenshot({path:`${outdir}/f${String(f).padStart(5,'0')}.png`});
    if(++n%50===0) console.log(`w${W}: ${n} frames, ${((Date.now()-t0)/n).toFixed(0)} ms/frame`);
  }
  await browser.close(); console.log(`w${W} done`);
})();
