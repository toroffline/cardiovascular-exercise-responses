import sys,pathlib,asyncio,json,subprocess
base=pathlib.Path(__file__).parent
sys.path.insert(0,str(base/'vendor'))
import edge_tts
brief=json.loads((base/'brief.json').read_text(encoding='utf-8'))
async def main():
    sem=asyncio.Semaphore(2)
    async def generate(i,j,text):
        async with sem:
            folder=base/'audio'/'niwat';folder.mkdir(exist_ok=True)
            mp=folder/f's{i:02d}_{j:02d}.mp3'
            wav=mp.with_suffix('.wav')
            if wav.exists() and wav.stat().st_size>1000: return
            for attempt in range(6):
                try:
                    await edge_tts.Communicate(text,'th-TH-NiwatNeural',rate='+0%',receive_timeout=30).save(str(mp))
                    subprocess.run(['ffmpeg','-v','error','-y','-i',str(mp),'-ar','24000','-ac','1',str(wav)],check=True)
                    print(f'Voice {i+1}.{j+1} ready',flush=True);await asyncio.sleep(.5);return
                except Exception as e:
                    print(f'Retry {i+1}.{j+1}: {type(e).__name__}',flush=True)
                    if attempt==5: raise
                    await asyncio.sleep(2+attempt)
    await asyncio.gather(*(generate(i,j,text) for i,s in enumerate(brief) for j,text in enumerate(s['lines'])))
asyncio.run(main())
