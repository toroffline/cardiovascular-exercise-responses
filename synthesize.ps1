$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$base = $PSScriptRoot
$brief = Get-Content -LiteralPath (Join-Path $base 'brief.json') -Raw -Encoding utf8 | ConvertFrom-Json
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice('Microsoft Pattara')
$synth.Rate = 0
$synth.Volume = 100
$manifest = @()
for ($i = 0; $i -lt $brief.Count; $i++) {
  for ($j = 0; $j -lt $brief[$i].lines.Count; $j++) {
    $name = 's{0:d2}_{1:d2}.wav' -f $i,$j
    $target = Join-Path (Join-Path $base 'audio') $name
    $synth.SetOutputToWaveFile($target)
    $synth.Speak([string]$brief[$i].lines[$j])
    $synth.SetOutputToNull()
    $manifest += @{scene=$i;line=$j;file=$name;text=$brief[$i].lines[$j]}
  }
  Write-Output ('Synthesized scene ' + ($i+1))
}
$synth.Dispose()
$manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $base 'audio-manifest.json') -Encoding utf8
