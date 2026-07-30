from backend.ai.services.gemini_service import GeminiService

transcript = """
Today I'll explain three mistakes that stop most people from growing.
The first mistake is trying to learn everything at once.
The second mistake is not taking action after learning.
The third mistake is giving up too early.
"""

service = GeminiService()

clips = service.analyze_transcript(transcript)

for clip in clips:
    print()
    print("Title :", clip.title)
    print("Start :", clip.start)
    print("End   :", clip.end)
    print("Reason:", clip.reason)