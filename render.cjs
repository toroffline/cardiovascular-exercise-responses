const {chromium}=require('C:/Users/narkk/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const http=require('http'),fs=require('fs'),path=require('path');
const base=__dirname;
const mode=process.argv[2]||'qa';
const startTime=Number(process.argv[3]||0),duration=Number(process.argv[4]||(mode==='sample'?10:300));
const outputName=process.argv[5]||'silent.h264';
const brief=JSON.parse(fs.readFileSync(path.join(base,'brief.json'),'utf8'));
if(!fs.existsSync(path.join(base,'timeline.js')))fs.writeFileSync(path.join(base,'timeline.js'),'const BRIEF='+JSON.stringify(brief)+';const CUES=[];');
const server=http.createServer((req,res)=>{let p=path.join(base,decodeURIComponent(req.url.split('?')[0]));if(req.url==='/')p=path.join(base,'index.html');if(!p.startsWith(base)){res.writeHead(403);return res.end();}fs.readFile(p,(e,d)=>{if(e){res.writeHead(404);res.end();}else{res.setHeader('Content-Type',p.endsWith('.js')?'application/javascript':p.endsWith('.html')?'text/html':p.endsWith('.wav')?'audio/wav':'application/octet-stream');res.end(d);}});});
(async()=>{await new Promise(r=>server.listen(8765,'127.0.0.1',r));
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,args:['--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required']});
 const page=await browser.newPage({viewport:{width:1920,height:1180},deviceScaleFactor:1});page.on('pageerror',e=>console.error('PAGE',e));page.on('console',m=>{if(m.type()==='log')console.log(m.text());});await page.goto('http://127.0.0.1:8765');
 console.log('Renderer',await page.evaluate(()=>GL_INFO));
 if(mode==='gait'){
  const report=await page.evaluate(()=>{
   let maxLengthError=0,maxContactError=0,maxGroundPenetration=0,maxReach=0;
   for(let i=0;i<1200;i++){
    const p=runnerPose(i/1200/(170/120));
    for(const l of[p.near,p.far]){
     maxLengthError=Math.max(maxLengthError,Math.abs(Math.hypot(l.knee[0]-p.hip[0],l.knee[1]-p.hip[1])-83),Math.abs(Math.hypot(l.ankle[0]-l.knee[0],l.ankle[1]-l.knee[1])-82));
     const toeY=l.ankle[1]+25*Math.sin(l.angle)+11*Math.cos(l.angle);
     if(l.contact)maxContactError=Math.max(maxContactError,Math.abs(toeY-170));
     maxGroundPenetration=Math.max(maxGroundPenetration,toeY-170);maxReach=Math.max(maxReach,l.distance);
    }
   }
   return {maxLengthError,maxContactError,maxGroundPenetration,maxReach};
  });
  console.log('GAIT',report);fs.writeFileSync(path.join(base,'qa','runner_revision','gait-report.json'),JSON.stringify(report,null,2));
  for(let i=0;i<12;i++){
   await page.evaluate(t=>renderFrame(t),(3+i/12)/(170/120));
   const png=await page.evaluate(()=>document.querySelector('canvas').toDataURL('image/png').split(',')[1]);
   fs.writeFileSync(path.join(base,'qa','runner_revision',`pose_${String(i).padStart(2,'0')}.png`),Buffer.from(png,'base64'));
  }
 } else if(mode==='qa'){
 console.log('Caption layout',await page.evaluate(()=>({count:CUES.length,maxLines:Math.max(0,...CUES.map(c=>wrap(c.text).length)),overflow:CUES.filter(c=>wrap(c.text).length>2).map(c=>c.text)})));
 for(let [i,t]of[5,49,92,139,172,201,232,270,284,295].entries()){await page.evaluate(t=>renderFrame(t),t);await page.locator('canvas').screenshot({path:path.join(base,'qa',`scene_${String(i+1).padStart(2,'0')}.png`)});}
 console.log('CODECS',await page.evaluate(async()=>{let out={};for(let codec of['avc1.42002a','vp09.00.40.08'])out[codec]=await VideoEncoder.isConfigSupported({codec,width:1920,height:1080,bitrate:6000000,framerate:30,hardwareAcceleration:'prefer-software',avc:{format:'annexb'}});return out;}));
 fs.writeFileSync(path.join(base,'qa','layout-report.json'),JSON.stringify(await page.evaluate(()=>({gl:GL_INFO,captions:CUES.length,captionMaxLines:Math.max(0,...CUES.map(c=>wrap(c.text).length)),atlasRows:ay+ah})),null,2));
 } else {
 const output=fs.createWriteStream(path.join(base,outputName));
 await page.exposeFunction('saveChunk',async b64=>{if(!output.write(Buffer.from(b64,'base64')))await new Promise(r=>output.once('drain',r));});
 await page.evaluate(async({startTime,duration})=>{
  const config={codec:'avc1.42002a',width:1920,height:1080,bitrate:5500000,framerate:30,hardwareAcceleration:'prefer-software',avc:{format:'annexb'},latencyMode:'quality'};
  if(!(await VideoEncoder.isConfigSupported(config)).supported)throw Error('H264 encoder unavailable');
  let pending=[],pendingSize=0,failure=null;
  const enc=new VideoEncoder({output:chunk=>{let d=new Uint8Array(chunk.byteLength);chunk.copyTo(d);pending.push(d);pendingSize+=d.length;},error:e=>{failure=e.message;}});enc.configure(config);
  async function send(){if(!pendingSize)return;let blob=new Blob(pending),buffer=new Uint8Array(await blob.arrayBuffer()),str='';for(let off=0;off<buffer.length;off+=32768)str+=String.fromCharCode(...buffer.subarray(off,off+32768));pending=[];pendingSize=0;await window.saveChunk(btoa(str));}
  const total=Math.round(duration*30);
  for(let i=0;i<total;i++){if(failure)throw Error(failure);while(enc.encodeQueueSize>6)await new Promise(r=>setTimeout(r,1));renderFrame(startTime+i/30);const frame=new VideoFrame(document.querySelector('canvas'),{timestamp:Math.round(i*1000000/30),duration:33333});enc.encode(frame,{keyFrame:i%60===0});frame.close();if(i%150===149){await enc.flush();await send();console.log('Rendered '+(i+1)+' / '+total+' frames');}}
  await enc.flush();await send();enc.close();
 },{startTime,duration});
 await new Promise(r=>output.end(r));
 }
 await browser.close();server.close();
})().catch(e=>{console.error(e);process.exit(1)});
