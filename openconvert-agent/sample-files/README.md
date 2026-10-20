# Sample files

Use these files to try the conversion recipes in OpenConvert:

- `image-inputs/`: valid PNG, JPEG, WebP, BMP, TIFF, and GIF files.
- `pdf-inputs/sample-document.pdf`: a three-page text PDF for PDF-to-image,
  PDF-to-DOCX/XLSX/PPTX/TXT, split, and compression tests.
- `pdf-inputs/merge-first.pdf` and `merge-second.pdf`: choose both for the
  merge-PDF action.
- `document-inputs/`: document samples in each input extension recognized by
  the conversion engine.
- `conversion-outputs/`: example results for PDF exports, merging, splitting,
  and compression.

To regenerate the whole sample set, install the project dependencies plus
LibreOffice, then run from `openconvert-agent/`:

```bash
python sample-files/generate_samples.py
```

LibreOffice is required for generating and converting office-document samples.
The PDF-to-Office examples contain selectable text; scanned PDFs are not
included because OCR is not supported.
