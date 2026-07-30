from pathlib import Path


class SubtitleService:
    def generate_srt(
        self,
        transcription: dict,
        output_path: str,
    ) -> str:
        """
        Generate an SRT subtitle file from Whisper transcription.
        """

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with output.open("w", encoding="utf-8") as file:
            for index, segment in enumerate(
                transcription["segments"],
                start=1,
            ):
                file.write(f"{index}\n")

                start = self._format_timestamp(segment["start"])
                end = self._format_timestamp(segment["end"])

                file.write(f"{start} --> {end}\n")
                file.write(f"{segment['text']}\n\n")

        return str(output)

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        total_milliseconds = int(round(seconds * 1000))

        hours = total_milliseconds // 3_600_000
        total_milliseconds %= 3_600_000

        minutes = total_milliseconds // 60_000
        total_milliseconds %= 60_000

        secs = total_milliseconds // 1000
        milliseconds = total_milliseconds % 1000

        return (
            f"{hours:02}:"
            f"{minutes:02}:"
            f"{secs:02},"
            f"{milliseconds:03}"
        )