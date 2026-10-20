from pathlib import Path
from PIL import Image
import pytest

from openconvert.engine import convert_image, unique_output_path, ConversionError, supported_targets

def test_image_conversion_preserves_source_and_creates_output(tmp_path: Path):
    source = tmp_path / "sample.png"
    Image.new("RGB", (20, 10), (255, 0, 0)).save(source)
    original_bytes = source.read_bytes()
    output = convert_image(source, "webp")
    assert output.exists()
    assert output.suffix == ".webp"
    assert source.read_bytes() == original_bytes
    with Image.open(output) as image:
        assert image.size == (20, 10)

def test_existing_output_is_not_overwritten(tmp_path: Path):
    source = tmp_path / "sample.png"
    Image.new("RGB", (4, 4)).save(source)
    existing = tmp_path / "sample.webp"
    existing.write_bytes(b"keep me")
    output = convert_image(source, "webp")
    assert output.name == "sample (1).webp"
    assert existing.read_bytes() == b"keep me"

def test_unsupported_image_target(tmp_path: Path):
    source = tmp_path / "sample.png"
    Image.new("RGB", (2, 2)).save(source)
    with pytest.raises(ConversionError):
        convert_image(source, "exe")

def test_supported_targets_for_document():
    assert supported_targets(Path("report.docx")) == ["pdf"]
