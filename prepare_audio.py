import json, subprocess, wave, pathlib, array
base=pathlib.Path(__file__).parent
brief=json.loads((base/'brief.json').read_text(encoding='utf-8-sig'))
sr=24000
combined=array.array('h',[0])*(300*sr)
cues=[]
for i,scene in enumerate(brief):
    files=sorted((base/'audio'/'niwat').glob(f's{i:02d}_*.wav'))
    if not scene['lines']: continue
    if len(files)!=len(scene['lines']): raise RuntimeError(f'Missing audio scene {i}')
    durations=[]
    for f in files:
        with wave.open(str(f),'rb') as w: durations.append(w.getnframes()/w.getframerate())
    available=scene['end']-scene['start']-1.5
    gap=.32
    rate=max(1.,sum(durations)/(available-gap*(len(files)-1)))
    # Keep continuous narration at a natural pace. Leave any spare time at scene end.
    at=scene['start']+.6
    print(i+1,'raw seconds',round(sum(durations),1),'tempo',round(rate,3),flush=True)
    for j,(f,d) in enumerate(zip(files,durations)):
        out=base/'audio'/f'fit_{i:02d}_{j:02d}.wav'
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(f),'-af',f'atempo={rate},highpass=f=70,alimiter=limit=0.92','-ar',str(sr),'-ac','1',str(out)],check=True)
        with wave.open(str(out),'rb') as w: data=array.array('h',w.readframes(w.getnframes()))
        start=round(at*sr);combined[start:start+len(data)]=data
        dur=len(data)/sr;cues.append({'start':round(at,3),'end':round(at+dur,3),'text':scene['lines'][j],'scene':i})
        at+=dur+gap
with wave.open(str(base/'narration.wav'),'wb') as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(combined.tobytes())
(base/'timeline.js').write_text('const BRIEF='+json.dumps(brief,ensure_ascii=False)+';\nconst CUES='+json.dumps(cues,ensure_ascii=False)+';',encoding='utf-8')
def stamp(t):
    ms=round(t*1000);return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
(base/'Thai_subtitles.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for i,c in enumerate(cues))+'\n',encoding='utf-8-sig')
(base/'cues.json').write_text(json.dumps(cues,ensure_ascii=False,indent=2),encoding='utf-8')
