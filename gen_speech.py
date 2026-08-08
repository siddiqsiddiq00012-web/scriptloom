import win32com.client
import time

speaker = win32com.client.Dispatch("SAPI.SpVoice")
# Save speech to a wav file
stream = win32com.client.Dispatch("SAPI.SpFileStream")
from comtypes.gen import SpeechLib
stream.Open("storage/speech.wav", SpeechLib.SSFMCreateForWrite)
speaker.AudioOutputStream = stream
speaker.Speak("Hello world! This is a test video for the clip generation pipeline. It has multiple segments. We will see if the AI can extract a good clip from this amazing and very important speech.")
stream.Close()
