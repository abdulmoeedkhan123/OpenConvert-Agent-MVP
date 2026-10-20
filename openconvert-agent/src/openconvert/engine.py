"""Safe, local conversion recipes. Never modifies source files or overwrites outputs."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageOps, UnidentifiedImageError

IMAGE_FORMATS = {
    "png": "PNG",
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "webp": "WEBP",
    "bmp": "BMP",
    "tif": "TIFF",
    "tiff": "TIFF",
}
DOCUMENT_EXTENSIONS = {".doc", ".docx", ".odt", ".rtf", ".txt", ".html", ".htm", ".odp", ".ppt", ".pptx", ".ods", ".xls", ".xlsx"}

class ConversionError(RuntimeError):
    """Raised when a conversion recipe cannot safely complete."""

def unique_output_path(path: Path) -> Path:
    """Return path if free, otherwise append a numeric suffix without overwriting."""
    if not path.exists():
        return path
    for number in range(1, 10000):
        candidate = path.with_name(f"{path.stem} ({number}){path.suffix}")
        if not candidate.exists():
            return candidate
    raise ConversionError(f"Could not find a free output name for {path.name}")

def _image_target_format(target: str) -> str:
    normalized = target.lower().lstrip(".")
    if normalized not in IMAGE_FORMATS:
        raise ConversionError(f"Unsupported image target: {target}")
    return normalized

def convert_image(source: Path, target: str, output_dir: Path | None = None) -> Path:
    source = source.expanduser().resolve()
    if not source.is_file():
        raise ConversionError(f"Input file does not exist: {source}")
    target = _image_target_format(target)
    output_dir = (output_dir or source.parent).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output = unique_output_path(output_dir / f"{source.stem}.{target}")

    try:
        with Image.open(source) as original:
            image = ImageOps.exif_transpose(original)
            # JPEG does not support alpha; composite onto white instead of silently failing.
            if IMAGE_FORMATS[target] == "JPEG":
                if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
                    rgba = image.convert("RGBA")
                    background = Image.new("RGB", rgba.size, (255, 255, 255))
                    background.paste(rgba, mask=rgba.getchannel("A"))
                    image = background
                else:
                    image = image.convert("RGB")
            elif IMAGE_FORMATS[target] in ("BMP", "TIFF") and image.mode not in ("RGB", "L", "RGBA"):
                image = image.convert("RGB")
            save_options = {}
            if IMAGE_FORMATS[target] == "WEBP":
                save_options = {"quality": 90, "method": 4}
            image.save(output, format=IMAGE_FORMATS[target], **save_options)
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        # Do not remove anything that wasn't created by this invocation.
        if output.exists():
            output.unlink()
        raise ConversionError(f"Image conversion failed: {exc}") from exc

    if not output.is_file() or output.stat().st_size == 0:
        raise ConversionError("Conversion reported success but output is missing or empty.")
    return output

def convert_to_pdf(source: Path, output_dir: Path | None = None, timeout: int = 120) -> Path:
    """Convert a document to PDF using a locally installed LibreOffice CLI."""
    source = source.expanduser().resolve()
    if not source.is_file():
        raise ConversionError(f"Input file does not exist: {source}")
    if source.suffix.lower() not in DOCUMENT_EXTENSIONS:
        raise ConversionError(f"Unsupported document input type: {source.suffix}")
    soffice = shutil.which("soffice")
    if not soffice:
        candidates = [
            Path("/Applications/LibreOffice.app/Contents/MacOS/soffice"),
            Path("/opt/homebrew/bin/soffice"),
            Path("/usr/local/bin/soffice"),
        ]
        soffice = next((str(p) for p in candidates if p.exists()), None)
    if not soffice:
        raise ConversionError("LibreOffice was not found. Install it and ensure `soffice` is available.")

    output_dir = (output_dir or source.parent).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    expected = output_dir / f"{source.stem}.pdf"

    # Convert into a private temporary directory, then move into a non-overwriting final path.
    import tempfile
    with tempfile.TemporaryDirectory(prefix="openconvert-") as tmp:
        tmp_path = Path(tmp)
        cmd = [
            soffice,
            "--headless",
            "-env:UserInstallation=file://" + str(tmp_path / "lo-profile"),
            "--convert-to", "pdf",
            "--outdir", str(tmp_path),
            str(source),
        ]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout, check=False
            )
        except subprocess.TimeoutExpired as exc:
            raise ConversionError(f"Document conversion timed out after {timeout} seconds.") from exc
        generated = tmp_path / f"{source.stem}.pdf"
        if result.returncode != 0 or not generated.is_file() or generated.stat().st_size == 0:
            detail = (result.stderr or result.stdout or "Unknown LibreOffice error").strip()
            raise ConversionError(f"Document conversion failed: {detail}")
        output = unique_output_path(expected)
        shutil.move(str(generated), str(output))

    return output

def supported_targets(source: Path) -> list[str]:
    """Return targets that this MVP can handle for a given source."""
    suffix = source.suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff", ".gif"}:
        return ["png", "jpg", "jpeg", "webp", "bmp", "tiff"]
    if suffix in DOCUMENT_EXTENSIONS:
        return ["pdf"]
    return []

def convert(source: Path, target: str, output_dir: Path | None = None) -> Path:
    normalized = target.lower().lstrip(".")
    if normalized == "pdf":
        return convert_to_pdf(source, output_dir)
    return convert_image(source, normalized, output_dir)
