"""Finalize the current clean render with optional Thai subtitles."""
import pathlib,runpy
runpy.run_path(str(pathlib.Path(__file__).with_name('finalize_subtitles.py')),run_name='__main__')
