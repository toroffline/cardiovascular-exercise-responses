import sys,pathlib,asyncio,json
b=pathlib.Path(__file__).parent;sys.path.insert(0,str(b/'vendor'))
import edge_tts
text=json.loads((b/'brief.json').read_text(encoding='utf8'))[1]['lines'][2]
async def main():
    for name,voice,s in [('period','th-TH-PremwadeeNeural',text+'.'),('short','th-TH-PremwadeeNeural',text.split(' ')[0]),('male','th-TH-NiwatNeural',text)]:
        try:
            await edge_tts.Communicate(s,voice,receive_timeout=20).save(str(b/'audio'/('probe_'+name+'.mp3')))
            print(name,'OK',flush=True)
        except Exception as e: print(name,type(e).__name__,flush=True)
asyncio.run(main())
