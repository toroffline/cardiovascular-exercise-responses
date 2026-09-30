const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const deps='C:/Users/narkk/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/';
const {chromium}=require(deps+'playwright'),{PNG}=require(deps+'pngjs');
const base=path.resolve(__dirname,'../..'),mode=process.argv[2]||'webgl';
function assert(value,message){if(!value)throw Error(message);}
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,args:['--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required']});
 const page=await browser.newPage({viewport:{width:1600,height:1060}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(base,mode==='webgl'?'index.html':'watch.html')).href);
 if(mode==='webgl'){
  const button=page.locator('#subtitles');
  assert(await button.getAttribute('aria-pressed')==='false','Subtitles should default off');
  await page.evaluate(()=>{const seek=document.querySelector('#seek');seek.value='5';seek.dispatchEvent(new Event('input'));});
  const data=async()=>Buffer.from(await page.evaluate(()=>document.querySelector('canvas').toDataURL('image/png').split(',')[1]),'base64');
  const off=await data();fs.writeFileSync(path.join(__dirname,'webgl_off.png'),off);
  await button.click();assert(await button.getAttribute('aria-pressed')==='true','On toggle failed');
  const on=await data();fs.writeFileSync(path.join(__dirname,'webgl_on.png'),on);
  const a=PNG.sync.read(off),b=PNG.sync.read(on);let changed=0,outside=0;
  for(let y=0;y<1080;y++)for(let x=0;x<1920;x++){let i=(y*1920+x)*4;if(a.data[i]!==b.data[i]||a.data[i+1]!==b.data[i+1]||a.data[i+2]!==b.data[i+2]){changed++;if(x<82||x>=1838||y<929||y>=1027)outside++;}}
  assert(changed>1000&&outside===0,'Toggle must change only the subtitle area');
  await button.click();assert(await button.getAttribute('aria-pressed')==='false','Off toggle failed');
  assert(off.equals(await data()),'Turning off must restore the clean frame');
  fs.writeFileSync(path.join(__dirname,'webgl-controls.json'),JSON.stringify({passed:true,default:'off',changedPixels:changed,changesOutsideSubtitles:outside,cleanFrameRestored:true},null,2));
  console.log('PASS: WebGL toggle works both ways and changes only subtitle pixels.');
 }else{
  await page.waitForFunction(()=>document.querySelector('#video').readyState>=1);
  await page.evaluate(()=>{document.querySelector('#video').currentTime=5;});
  await page.waitForFunction(()=>{const v=document.querySelector('#video');return !v.seeking&&v.readyState>=2;});
  await page.evaluate(()=>document.querySelector('#video').play());
  await page.waitForFunction(()=>document.querySelector('#video').currentTime>5.8);
  await page.evaluate(()=>document.querySelector('#video').pause());
  await page.waitForFunction(()=>document.querySelector('#video').readyState===4);
  await page.waitForTimeout(500);
  const button=page.locator('#cc');assert(await button.getAttribute('aria-pressed')==='false','Video subtitles should default off');
  await page.screenshot({path:path.join(__dirname,'player_off.png')});
  await button.click();
  await page.waitForFunction(()=>Array.from(document.querySelector('#video').textTracks).some(t=>t.mode==='showing'&&t.activeCues.length===1));
  const status=await page.evaluate(()=>{const v=document.querySelector('#video');const t=Array.from(v.textTracks).find(t=>t.mode==='showing');return {duration:v.duration,width:v.videoWidth,height:v.videoHeight,cueCount:t.cues.length,activeText:t.activeCues[0].text,mode:t.mode};});
  console.log('PLAYER',JSON.stringify(status));
  assert(Math.abs(status.duration-300)<.1&&status.width===1920&&status.cueCount===36,'Video or subtitle track incorrect');
  await page.screenshot({path:path.join(__dirname,'player_on.png')});
  await button.click();assert(await button.getAttribute('aria-pressed')==='false','Video off toggle failed');
  assert(await page.evaluate(()=>Array.from(document.querySelector('#video').textTracks).every(t=>t.mode!=='showing')),'Subtitle track remains visible');
  fs.writeFileSync(path.join(__dirname,'video-controls.json'),JSON.stringify({passed:true,default:'off',...status,toggleOffVerified:true},null,2));
  console.log('PASS: Offline video loads; 36 Thai cues toggle on and off.');
 }
 assert(errors.length===0,errors.join('\n'));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
