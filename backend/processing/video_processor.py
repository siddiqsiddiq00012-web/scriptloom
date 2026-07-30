from pathlib import Path


class VideoProcessor:
    """
    Handles all video processing tasks.

    Future capabilities:
    - Extract metadata
    - Generate thumbnails
    - Extract audio
    - Compress videos
    - Call Whisper
    """

    def __init__(self, video_path: str):
        self.video_path = Path(video_path)

    def exists(self) -> bool:
        return self.video_path.exists()

    def process(self) -> None:
        """
        Entry point for the complete processing pipeline.
        """
        if not self.exists():
            raise FileNotFoundError(
                f"Video not found: {self.video_path}"
            )

        # Future pipeline:
        #
        # self.extract_metadata()
        # self.generate_thumbnail()
        # self.extract_audio()
        # self.transcribe()
        #
        # For now, this is intentionally empty.
        return