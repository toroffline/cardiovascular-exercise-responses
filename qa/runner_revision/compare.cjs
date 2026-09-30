const fs=require('fs'),path=require('path'),http=require('http');
const deps='C:/Users/narkk/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/';
const {chromium}=require(deps+'playwright'),{PNG}=require(deps+'pngjs');
const base=path.resolve(__dirname,'../..');
const server=http.createServer((req,res)=>{const p=path.join(base,req.url==='/'?'index.html':req.url);fs.readFile(p,(e,d)=>{res.writeHead(e?404:200,{'Content-Type':p.endsWith('.js')?'application/javascript':p.endsWith('.html')?'text/html':'application/octet-stream'});res.end(e?'':d);});});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,args:['--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const current=await browser.newPage(),previous=await browser.newPage();
 await previous.route('**/film.js',route=>route.fulfill({contentType:'application/javascript',body:fs.readFileSync(path.join(__dirname,'original_film.js'))}));
 await Promise.all([current.goto(`http://127.0.0.1:${server.address().port}/`),previous.goto(`http://127.0.0.1:${server.address().port}/`)]);
 const report=[];
 for(const t of[5,49,92,139,172,201,232,270,284,295]){
  const screenshots=await Promise.all([current,previous].map(async p=>{await p.evaluate(t=>renderFrame(t),t);return PNG.sync.read(Buffer.from(await p.evaluate(()=>document.querySelector('canvas').toDataURL('image/png').split(',')[1]),'base64'));}));
  const runner=t<60||t>=275&&t<290;
  const bounds=t<20||t>=275?[180,300,560,742]:[100,300,455,745];
  let changed=0,outside=0;
  for(let y=0;y<1080;y++)for(let x=0;x<1920;x++){
   const q=(y*1920+x)*4;
   if(screenshots[0].data[q]!==screenshots[1].data[q]||screenshots[0].data[q+1]!==screenshots[1].data[q+1]||screenshots[0].data[q+2]!==screenshots[1].data[q+2]){
    changed++;if(!runner||x<bounds[0]||x>=bounds[2]||y<bounds[1]||y>=bounds[3])outside++;
   }
  }
  report.push({time:t,changedPixels:changed,changesOutsideRunner:outside});
  if(outside)throw Error('Unexpected change outside runner at '+t);
 }
 fs.writeFileSync(path.join(__dirname,'scope-report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
 await browser.close();server.close();
})().catch(e=>{console.error(e);process.exit(1)});
