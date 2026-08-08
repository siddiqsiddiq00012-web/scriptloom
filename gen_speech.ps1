Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SetOutputToWaveFile('d:\Projects\Scriptloom\storage\speech.wav')
$synth.Speak('Hello world! This is a test video for the clip generation pipeline. It has multiple segments. We will see if the AI can extract a good clip from this amazing and very important speech.')
$synth.Dispose()
