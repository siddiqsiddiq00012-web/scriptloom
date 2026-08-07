import os
import shutil
import tempfile
from pathlib import Path
from sqlalchemy.orm import Session

from backend.models.media import Media
from backend.processing.audio_processor import AudioProcessor
from backend.processing.waveform_processor import WaveformProcessor
from backend.services.ffprobe_service import FFprobeService
from backend.storage.manager import storage


class MediaPipeline:
    """
    Executes end-to-end media processing:
    1. Extract video/audio metadata
    2. Extract normalized 16kHz WAV audio
    3. Generate peak waveform JSON and persist to storage
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
            # 1. Materialize the media source file
            with storage.materialize(media.storage_path) as local_media_path:
                # 2. Setup temporary local workspace for intermediate files
                temp_workspace = Path(tempfile.mkdtemp(prefix="media_pipeline_"))
                temp_audio_path = temp_workspace / f"{media.id}_audio.wav"
                temp_waveform_path = temp_workspace / f"{media.id}_waveform.json"

                try:
                    # A. Metadata Extraction (using materialized path)
                    metadata = FFprobeService.extract_metadata(local_media_path)
                    media.duration = metadata.duration
                    media.width = metadata.width
                    media.height = metadata.height
                    media.codec = metadata.codec
                    media.bitrate = metadata.bitrate
                    media.fps = metadata.fps

                    # B. Extract Audio WAV (into temp workspace)
                    AudioProcessor.extract_audio(local_media_path, temp_audio_path)

                    # C. Waveform Generation (into temp workspace)
                    WaveformProcessor.generate_waveform(temp_audio_path, temp_waveform_path)

                    # D. Upload waveform JSON to persistent storage
                    waveform_key = f"projects/{media.project_id}/waveforms/{media.id}_waveform.json"
                    file_size = temp_waveform_path.stat().st_size
                    
                    with open(temp_waveform_path, "rb") as wf:
                        def _wf_generator():
                            while True:
                                chunk = wf.read(1024 * 1024)
                                if not chunk:
                                    break
                                yield chunk
                        storage.save_stream(waveform_key, _wf_generator(), file_size)

                    # E. Status Update
                    media.status = "processed"
                    self.db.commit()
                    self.db.refresh(media)
                    return media
                finally:
                    # Clean up workspace
                    if temp_workspace.exists():
                        shutil.rmtree(temp_workspace)

        except Exception as e:
            media.status = "error"
            self.db.commit()
            print(f"[MediaPipeline Error] {e}")
            return media
