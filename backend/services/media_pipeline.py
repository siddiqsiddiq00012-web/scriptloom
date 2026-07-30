import os
from pathlib import Path
from sqlalchemy.orm import Session

from backend.models.media import Media
from backend.processing.audio_processor import AudioProcessor
from backend.processing.waveform_processor import WaveformProcessor
from backend.services.ffprobe_service import FFprobeService


class MediaPipeline:
    """
    Executes end-to-end media processing:
    1. Extract video/audio metadata
    2. Extract normalized 16kHz WAV audio
    3. Generate peak waveform JSON
    4. Update database status to 'processed'
    """

    def __init__(self, db: Session):
        self.db = db

    def process_media(self, media_id: int) -> Media | None:
        media = self.db.query(Media).filter(Media.id == media_id).first()
        if media is None:
            return None

        media.status = "processing"
        self.db.commit()

        try:
            input_path = Path(media.storage_path)

            # 1. Metadata Extraction
            metadata = FFprobeService.extract_metadata(input_path)
            media.duration = metadata.duration
            media.width = metadata.width
            media.height = metadata.height
            media.codec = metadata.codec
            media.bitrate = metadata.bitrate
            media.fps = metadata.fps

            # 2. Extract Audio WAV
            media_dir = input_path.parent
            audio_filename = f"{media.id}_audio.wav"
            audio_wav_path = media_dir / audio_filename

            AudioProcessor.extract_audio(input_path, audio_wav_path)

            # 3. Waveform Generation
            waveform_filename = f"{media.id}_waveform.json"
            waveform_json_path = media_dir / waveform_filename

            WaveformProcessor.generate_waveform(audio_wav_path, waveform_json_path)

            # 4. Status Update
            media.status = "processed"
            self.db.commit()
            self.db.refresh(media)
            return media

        except Exception as e:
            media.status = "error"
            self.db.commit()
            print(f"[MediaPipeline Error] {e}")
            return media
