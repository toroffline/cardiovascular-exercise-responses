# Cardiovascular Responses: Dynamic vs. Isometric Exercise

An original five-minute, 1920 × 1080, 30 fps educational film for master's students in sports science. English diagram labels, synthesized Thai narration, and Thai subtitles.

## Outputs

- `Cardiovascular_Responses_Subtitles_Optional.mp4` — finished H.264/AAC video with a separate Thai subtitle track. Subtitles are off by default and can be enabled through a compatible player's Subtitles/CC menu. No narration subtitles are burned into the picture. `Cardiovascular_Responses_WebGL.mp4` is a copy of this latest export.
- `watch.html` — video player with a visible **Thai subtitles: Off / On** button. Open with the MP4 and `timeline.js` in the same folder. The `Video_with_Subtitle_Toggle.zip` package contains everything needed: extract the whole folder, then open `watch.html`. This player includes a browser-compatible subtitle track because support for embedded MP4 text tracks varies by player.
- `index.html` — editable WebGL player with its own subtitle toggle. Open in a modern browser; click Play to start narration. No external JavaScript libraries or internet connection are required for playback. Thai font rendering uses the system's installed fonts. The source ZIP includes the WebGL player and narration; the separate video-player ZIP includes the MP4.
- `Thai_subtitles.srt` and `Thai_subtitles.vtt` — separate subtitle files with all 36 Thai cues.
- `brief.json` — Thai narration script and chapter timings.
- `film.js` — procedural illustrations, animation, typography, and WebGL renderer.

## Timeline

| Time | Chapter |
|---|---|
| 0:00–0:20 | Introduction: running and wall sit |
| 0:20–1:00 | Dynamic exercise |
| 1:00–1:45 | Isometric exercise |
| 1:45–2:25 | Direct comparison |
| 2:25–3:00 | MAP and the pressure equation |
| 3:00–3:25 | Compression and reactive hyperemia |
| 3:25–4:00 | Valsalva maneuver |
| 4:00–4:35 | Safety and exercise prescription |
| 4:35–4:50 | Conclusion |
| 4:50–5:00 | References |

The supplied scene 6/7 overlap has been resolved into consecutive scenes. References receive ten seconds. All illustrations and traces are conceptual, not patient data or anatomical measurements.

## Scientific framing

The comparison describes typical acute responses to moderate running versus a relatively demanding sustained isometric effort. It is not a matched-intensity experiment. Arrow counts are qualitative. Local resistance due to vessel compression is distinguished from systemic vascular resistance: systemic resistance may remain unchanged or rise and is generally higher relative to dynamic aerobic exercise. Wall sits do not invariably produce a larger blood-pressure rise than all running workloads.

MAP ≈ CO × SVR assumes that right atrial pressure is small. The exact mean-pressure relationship includes right atrial pressure. This equation does not independently predict SBP or DBP; pulsatile flow and arterial compliance also matter. Valsalva is depicted with a qualitative four-phase response, rather than a continuously rising pressure trace.

The 1985 heavy-lifting study supports discussion of heavy effort and Valsalva; its extreme measurements are not presented as wall-sit values. The 2013 meta-analysis concerns changes in resting BP after training, not acute pressure during contraction. Long-term benefit and acute pressure elevation are distinct outcomes.

## Sources

- [MacDougall et al. (1985). Arterial blood pressure response to heavy resistance exercise.](https://doi.org/10.1152/jappl.1985.58.3.785)
- [Paluch et al. (2024). Resistance Exercise Training in Individuals With and Without Cardiovascular Disease: 2023 Update. AHA Scientific Statement.](https://doi.org/10.1161/CIR.0000000000001189)
- [ACSM's Guidelines for Exercise Testing and Prescription, 12th edition.](https://acsm.org/education-resources/books/guidelines-exercise-testing-prescription/)
- [Cornelissen & Smart (2013). Exercise Training for Blood Pressure: A Systematic Review and Meta-analysis.](https://doi.org/10.1161/JAHA.112.004473)
- [Mitchell et al. (2005). Task Force 8: Classification of sports.](https://doi.org/10.1016/j.jacc.2005.02.015)
- [Valsalva Maneuver, NCBI Bookshelf.](https://www.ncbi.nlm.nih.gov/books/NBK537248/)

## Rendering

All moving anatomy, athletes, vessels, arrows, plots, layout shapes, and final compositing are drawn by WebGL 2. A 2D canvas rasterizes text into a texture atlas; glyphs are then rendered by WebGL. Deterministic frames are encoded with WebCodecs H.264 and muxed with FFmpeg. This is a rendered video, not a screen recording. `render.cjs` includes the rendering entry point and uses a locally installed Chromium/Playwright runtime. Adjust executable paths for another computer. `prepare_audio.py` aligns sentence audio with the chapter schedule.

For an export with optional subtitles, render with `node render.cjs full 0 300 silent_no_subtitles.h264`, then run `python finalize.py`. The WebGL player and renderer start with subtitles off; the MP4 receives its subtitle track during finalization. The revised natural treadmill-running animation is retained.

Thai voice: Microsoft Niwat Neural, synthesized through the Microsoft speech service. No music is included, to preserve narration clarity.
