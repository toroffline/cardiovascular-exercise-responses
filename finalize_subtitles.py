"""Mux optional Thai subtitles into the clean WebGL render and package players."""
import json,pathlib,re,shutil,subprocess,zipfile
b=pathlib.Path(__file__).parent
qa=b/'qa'/'subtitles_revision';qa.mkdir(parents=True,exist_ok=True)
def run(args,capture=False):
    return subprocess.run(args,check=True,capture_output=capture,text=capture,encoding='utf-8' if capture else None)
srt=(b/'Thai_subtitles.srt').read_text(encoding='utf-8-sig')
vtt='WEBVTT\n\n'+re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{3})',r'\1.\2',srt)
(b/'Thai_subtitles.vtt').write_text(vtt,encoding='utf-8')
reference=b/'Cardiovascular_Responses_WebGL_runner_fixed.mp4'
audio=reference if reference.exists() else b/'narration.wav'
audio_args=['-c:a','copy'] if reference.exists() else ['-c:a','aac','-b:a','160k','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-ar','48000']
target=b/'Cardiovascular_Responses_Subtitles_Optional.mp4'
run(['ffmpeg','-hide_banner','-loglevel','warning','-y','-r','30','-i',str(b/'silent_no_subtitles.h264'),'-i',str(audio),'-sub_charenc','UTF-8','-i',str(b/'Thai_subtitles.srt'),'-i',str(b/'chapters.ffmeta'),'-map','0:v:0','-map','1:a:0','-map','2:s:0','-map_metadata','3','-map_chapters','3','-c:v','copy',*audio_args,'-c:s','mov_text','-metadata:s:s:0','language=tha','-metadata:s:s:0','handler_name=Thai subtitles','-metadata:s:s:0','title=Thai','-metadata:s:a:0','language=tha','-disposition:s:0','0','-t','300','-movflags','+faststart',str(target)])
info=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(target)],True).stdout)
# This installed FFmpeg enables the first MP4 subtitle track even when its
# default disposition is cleared. Clear just that track's tkhd enabled bit;
# its media, timing, alternate group, and manual selection remain intact.
initial_sub=next(s for s in info['streams'] if s['codec_type']=='subtitle')
if initial_sub['disposition']['default']:
    data=target.read_bytes();wanted_id=int(initial_sub['id'],0)
    def boxes(start,end):
        pos=start
        while pos+8<=end:
            size=int.from_bytes(data[pos:pos+4],'big');kind=data[pos+4:pos+8];header=8
            if size==1:size=int.from_bytes(data[pos+8:pos+16],'big');header=16
            if size==0:size=end-pos
            assert size>=header and pos+size<=end,'Invalid MP4 box'
            yield kind,pos+header,pos+size
            pos+=size
    edits=[]
    for kind,body,end in boxes(0,len(data)):
        if kind!=b'moov':continue
        for tk,tb,te in boxes(body,end):
            if tk!=b'trak':continue
            for hk,hb,he in boxes(tb,te):
                if hk!=b'tkhd':continue
                id_offset=hb+(20 if data[hb]==1 else 12)
                if int.from_bytes(data[id_offset:id_offset+4],'big')==wanted_id:
                    flags=int.from_bytes(data[hb+1:hb+4],'big')&~1
                    edits.append((hb+1,flags.to_bytes(3,'big')))
    assert len(edits)==1,'Subtitle track header not uniquely identified'
    with target.open('r+b') as output:
        for offset,value in edits:output.seek(offset);output.write(value)
    info=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(target)],True).stdout)
video=next(s for s in info['streams'] if s['codec_type']=='video')
sub=next(s for s in info['streams'] if s['codec_type']=='subtitle')
assert (video['width'],video['height'],video['r_frame_rate'],int(video['nb_frames']))==(1920,1080,'30/1',9000)
assert abs(float(info['format']['duration'])-300)<.1 and len(info['chapters'])==10
assert sub['codec_name']=='mov_text' and sub['tags']['language']=='tha'
assert sub['disposition']['default']==0 and sub['disposition']['forced']==0
extracted=run(['ffmpeg','-v','error','-i',str(target),'-map','0:s:0','-f','srt','-'],True).stdout
def cues(text):
    return [(m[1],m[2],m[3].strip()) for m in re.finditer(r'(?m)^\d+\r?\n(\d\d:\d\d:\d\d,\d\d\d) --> (\d\d:\d\d:\d\d,\d\d\d)\r?\n(.*?)(?=\r?\n\r?\n|\Z)',text,re.S)]
assert cues(extracted)==cues(srt),'Subtitle timings or Thai text changed during muxing'
assert len(cues(extracted))==36
(qa/'extracted_subtitles.srt').write_text(extracted,encoding='utf-8')
if reference.exists():
    def audio_hash(file):
        return run(['ffmpeg','-v','error','-i',str(file),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],True).stdout.strip()
    assert audio_hash(reference)==audio_hash(target),'Narration changed'
run(['ffmpeg','-v','error','-i',str(target),'-map','0:v:0','-map','0:a:0','-f','null','-'])
for t in [5,49,139,232,284,295]:
    run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(target),'-frames:v','1',str(qa/f'clean_{t:03d}.png')])
info['validation']={'subtitle_cues':36,'default_subtitles':'off','subtitle_text_and_timing_verified':True,'full_decode_passed':True}
(qa/'export-report.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
shutil.copy2(target,b/'Cardiovascular_Responses_WebGL.mp4')
names=['index.html','watch.html','film.js','timeline.js','brief.json','narration.wav','Thai_subtitles.srt','Thai_subtitles.vtt','Thai_narration.md','README.md','render.cjs','prepare_audio.py','synthesize_edge.py','finalize.py','finalize_subtitles.py','chapters.ffmeta','cues.json']
with zipfile.ZipFile(b/'WebGL_source_and_subtitles.zip','w',zipfile.ZIP_DEFLATED) as z:
    for name in names:z.write(b/name,'cardiovascular_webgl/'+name)
    for p in (b/'audio'/'niwat').glob('*.wav'):z.write(p,'cardiovascular_webgl/audio/niwat/'+p.name)
with zipfile.ZipFile(b/'Video_with_Subtitle_Toggle.zip','w',zipfile.ZIP_DEFLATED) as z:
    z.write(target,'Cardiovascular_video/'+target.name,compress_type=zipfile.ZIP_STORED)
    for name in ['watch.html','timeline.js','Thai_subtitles.srt','Thai_subtitles.vtt']:
        z.write(b/name,'Cardiovascular_video/'+name)
    z.writestr('Cardiovascular_video/START_HERE.txt','Extract this entire folder, then open watch.html in a browser.\nUse the Thai subtitles button to switch captions on or off.\nThai narration is always included.\nThe MP4 also contains an optional Thai subtitle track for compatible video players.\nSubtitles are off by default.\n')
print('PASS: clean 1080p video, 30 fps, 300 seconds, 36 optional Thai subtitle cues, unchanged narration.',flush=True)
print('Packaged the offline video player and updated WebGL source.',flush=True)
