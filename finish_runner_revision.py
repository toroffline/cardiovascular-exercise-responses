"""Replace the running shots while copying all unaffected video and audio."""
import json,pathlib,subprocess,shutil,zipfile
b=pathlib.Path(__file__).parent
q=b/'qa'/'runner_revision'
old=q/'original.mp4'
def run(args,capture=False):
    return subprocess.run(args,check=True,capture_output=capture,text=capture)
for start,frames,name in [(60,6420,'middle.h264'),(290,300,'end.h264')]:
    run(['ffmpeg','-v','error','-y','-ss',str(start),'-i',str(old),'-map','0:v:0','-frames:v',str(frames),'-c:v','copy','-bsf:v','h264_mp4toannexb','-f','h264',str(q/name)])
assembled=q/'assembled.h264'
with assembled.open('wb') as output:
    for name in ['start.h264','middle.h264','conclusion.h264','end.h264']:
        with (q/name).open('rb') as source: shutil.copyfileobj(source,output)
target=b/'Cardiovascular_Responses_WebGL_runner_fixed.mp4'
run(['ffmpeg','-hide_banner','-loglevel','warning','-y','-r','30','-i',str(assembled),'-i',str(old),'-map','0:v:0','-map','1:a:0','-map_metadata','1','-map_chapters','1','-c:v','copy','-c:a','copy','-t','300','-movflags','+faststart',str(target)])
info=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(target)],True).stdout)
v=next(s for s in info['streams'] if s['codec_type']=='video')
assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'30/1',9000)
assert abs(float(info['format']['duration'])-300)<.1 and len(info['chapters'])==10
def audio_hash(file):
    return run(['ffmpeg','-v','error','-i',str(file),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],True).stdout.strip()
assert audio_hash(old)==audio_hash(target),'Audio changed'
run(['ffmpeg','-v','error','-i',str(target),'-f','null','-'])
for time in [5,49,92,139,201,232,270,284,295]:
    run(['ffmpeg','-v','error','-y','-ss',str(time),'-i',str(target),'-frames:v','1',str(q/f'final_{time:03d}.png')])
info['revision_validation']={'audio_bitstream_unchanged':True,'full_decode_passed':True,'video_frames':9000,'duration_seconds':300}
(q/'export-report.json').write_text(json.dumps(info,indent=2),encoding='utf8')
shutil.copy2(target,b/'Cardiovascular_Responses_WebGL.mp4')
shutil.copy2(assembled,b/'silent.h264')
names=['index.html','film.js','timeline.js','brief.json','narration.wav','Thai_subtitles.srt','Thai_narration.md','README.md','render.cjs','prepare_audio.py','synthesize_edge.py','finalize.py','chapters.ffmeta','cues.json']
with zipfile.ZipFile(b/'WebGL_source_and_subtitles.zip','w',zipfile.ZIP_DEFLATED) as z:
    for name in names:z.write(b/name,'cardiovascular_webgl/'+name)
    for p in (b/'audio'/'niwat').glob('*.wav'):z.write(p,'cardiovascular_webgl/audio/niwat/'+p.name)
run(['ffmpeg','-v','error','-y','-ss','2','-i',str(target),'-t','6','-an','-c:v','copy','-movflags','+faststart',str(q/'runner_preview.mp4')])
print('PASS: 1080p / 30 fps / 5 minutes / 10 chapters; unchanged audio; full decode passed.',flush=True)
