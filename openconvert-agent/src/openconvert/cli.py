from __future__ import annotations
import argparse
import sys
from pathlib import Path

from .engine import convert, merge_pdfs, split_pdf, compress_pdf, ConversionError
from .planner import deterministic_plan, ollama_plan

def main() -> int:
    parser = argparse.ArgumentParser(prog="openconvert", description="Local-first file conversion")
    sub = parser.add_subparsers(dest="command", required=True)

    c = sub.add_parser("convert", help="Convert a file using a supported local recipe")
    c.add_argument("files", nargs="+", type=Path)
    c.add_argument("--to", required=True, help="Target format, e.g. webp or pdf")
    c.add_argument("--output-dir", type=Path, default=None)

    m = sub.add_parser("merge-pdf", help="Merge two or more PDF files")
    m.add_argument("files", nargs="+", type=Path)
    m.add_argument("--output-dir", type=Path, default=None)

    s = sub.add_parser("split-pdf", help="Split a PDF into one file per page")
    s.add_argument("file", type=Path)
    s.add_argument("--output-dir", type=Path, default=None)

    z = sub.add_parser("compress-pdf", help="Compress a PDF locally")
    z.add_argument("file", type=Path)
    z.add_argument("--output-dir", type=Path, default=None)

    p = sub.add_parser("plan", help="Propose a conversion from natural language")
    p.add_argument("prompt")
    p.add_argument("--file", action="append", default=[], type=Path, help="Known file path (repeatable)")
    p.add_argument("--ollama", action="store_true", help="Use local Ollama instead of deterministic planner")
    p.add_argument("--model", default="llama3.2:3b")

    g = sub.add_parser("gui", help="Launch desktop UI")
    args = parser.parse_args()

    if args.command == "convert":
        failed = False
        for source in args.files:
            try:
                output = convert(source, args.to, args.output_dir)
                outputs = output if isinstance(output, list) else [output]
                for path in outputs:
                    print(f"OK\t{source}\t{path}")
            except ConversionError as exc:
                failed = True
                print(f"ERROR\t{source}\t{exc}", file=sys.stderr)
        return 1 if failed else 0

    if args.command == "merge-pdf":
        try:
            print(f"OK\t{merge_pdfs(args.files, args.output_dir)}")
            return 0
        except ConversionError as exc:
            print(f"ERROR\t{exc}", file=sys.stderr)
            return 1

    if args.command == "split-pdf":
        try:
            for output in split_pdf(args.file, args.output_dir):
                print(f"OK\t{output}")
            return 0
        except ConversionError as exc:
            print(f"ERROR\t{exc}", file=sys.stderr)
            return 1

    if args.command == "compress-pdf":
        try:
            print(f"OK\t{compress_pdf(args.file, args.output_dir)}")
            return 0
        except ConversionError as exc:
            print(f"ERROR\t{exc}", file=sys.stderr)
            return 1

    if args.command == "plan":
        paths = [p.expanduser().resolve() for p in args.file]
        try:
            plan = ollama_plan(args.prompt, paths, model=args.model) if args.ollama else deterministic_plan(args.prompt, paths)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        import json
        print(json.dumps(plan, indent=2))
        return 0

    if args.command == "gui":
        try:
            from .gui import run_gui
        except ImportError:
            print("Desktop UI dependencies missing. Install with: pip install -e '.[ui]'", file=sys.stderr)
            return 2
        return run_gui()

if __name__ == "__main__":
    raise SystemExit(main())
