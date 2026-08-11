import subprocess
from pathlib import Path

from backend.core.config import settings


class ClipExtractionService:
    def extract_clip(
        self,
        input_video: str,
        output_video: str,
        start: float,
        end: float,
        subtitles: str | None = None,
    ) -> str:
        """
        Extract a clip from a video, optionally burning subtitles.
        """

        output = Path(output_video)
        output.parent.mkdir(parents=True, exist_ok=True)

        # Use input-seek (-ss before -i) for speed, combined with -t (duration)
        # after -i. Since -ss before -i resets output timestamps to 0,
        # -t is relative to the seek point — which gives the correct clip duration.
        command = [
            settings.FFMPEG_PATH,
            "-y",
            "-ss",
            str(start),
            "-i",
            input_video,
            "-t",
            str(end - start),
        ]

        if subtitles:
            subtitle_path = (
                Path(subtitles)
                .resolve()
                .as_posix()
                .replace(":", "\\:")
            )

            style = (
                "FontName=Arial,"
                "FontSize=20,"
                "PrimaryColour=&HFFFFFF&,"
                "OutlineColour=&H000000&,"
                "Outline=2,"
                "Shadow=1,"
                "Alignment=2,"
                "MarginV=40,"
                "Bold=1"
            )

            command.extend(
                [
                    "-vf",
                    f"subtitles='{subtitle_path}':force_style='{style}'",
                ]
            )

        command.extend(
            [
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-movflags",
                "+faststart",
                str(output),
            ]
        )

        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"FFmpeg failed:\n{e.stderr}"
            ) from e

        return str(output)