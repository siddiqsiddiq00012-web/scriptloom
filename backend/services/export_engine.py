import io
import json
import zipfile
from sqlalchemy.orm import Session

from backend.models.generated_content import GeneratedContent
from backend.models.media import Media


class ExportEngine:
    """
    Multi-Format Export Engine for Scriptloom.
    Renders generated assets into Markdown, Plain Text, PDF outline, or bundled ZIP archives.
    """

    def __init__(self, db: Session):
        self.db = db

    def _parse_body_json(self, asset) -> any:
        """Safely parse body_json, returning the raw string on failure."""
        try:
            if asset.body_json.startswith(("[", "{")):
                return json.loads(asset.body_json)
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
        return asset.body_json

    def export_single_content(self, content_id: int, format_type: str = "markdown") -> tuple[str, bytes, str]:
        asset = self.db.query(GeneratedContent).filter(GeneratedContent.id == content_id).first()
        if not asset:
            raise ValueError(f"Generated asset #{content_id} not found")

        fmt = format_type.lower()
        title_slug = asset.title.lower().replace(" ", "_").replace(":", "")

        if fmt == "json":
            filename = f"{title_slug}.json"
            content_bytes = asset.body_json.encode("utf-8")
            media_type = "application/json"
        elif fmt in ("txt", "text"):
            filename = f"{title_slug}.txt"
            raw_body = self._parse_body_json(asset)
            if isinstance(raw_body, list):
                text_str = "\n\n".join([str(item) for item in raw_body])
            elif isinstance(raw_body, dict):
                text_str = "\n\n".join([f"{k.upper()}:\n{v}" for k, v in raw_body.items()])
            else:
                text_str = str(raw_body)
            content_bytes = text_str.encode("utf-8")
            media_type = "text/plain"
        else:
            # Default to Markdown (.md)
            filename = f"{title_slug}.md"
            raw_body = self._parse_body_json(asset)
            if isinstance(raw_body, dict) and "markdown" in raw_body:
                md_text = raw_body["markdown"]
            elif isinstance(raw_body, list):
                md_slides = []
                for idx, slide in enumerate(raw_body):
                    if isinstance(slide, dict):
                        md_slides.append(f"### Slide {slide.get('slideNum', idx+1)}: {slide.get('headline', '')}\n\n{slide.get('body', '')}")
                    else:
                        md_slides.append(f"{idx+1}. {slide}")
                md_text = f"# {asset.title}\n\n" + "\n\n---\n\n".join(md_slides)
            elif isinstance(raw_body, dict):
                md_text = f"# {asset.title}\n\n" + "\n\n".join([f"### {k.replace('_', ' ').title()}\n{v}" for k, v in raw_body.items()])
            else:
                md_text = f"# {asset.title}\n\n{raw_body}"
            content_bytes = md_text.encode("utf-8")
            media_type = "text/markdown"

        return filename, content_bytes, media_type

    def export_campaign_zip(self, media_id: int) -> tuple[str, bytes, str]:
        media = self.db.query(Media).filter(Media.id == media_id).first()
        if not media:
            raise ValueError(f"Media #{media_id} not found")

        assets = self.db.query(GeneratedContent).filter(GeneratedContent.media_id == media_id).all()
        if not assets:
            raise ValueError(f"No campaign pack generated for media #{media_id}")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for idx, asset in enumerate(assets, 1):
                fmt = "json" if asset.content_type == "linkedin_carousel" else ("md" if asset.content_type == "newsletter" else "txt")
                fname, c_bytes, _ = self.export_single_content(asset.id, format_type=fmt)
                zip_file.writestr(f"{idx}_{fname}", c_bytes)

        zip_buffer.seek(0)
        filename = f"Scriptloom_Campaign_Pack_Media_{media_id}.zip"
        return filename, zip_buffer.getvalue(), "application/zip"
