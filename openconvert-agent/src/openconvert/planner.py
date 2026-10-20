"""Optional local AI intent helper. Model output is treated as untrusted data."""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from pathlib import Path

from .engine import supported_targets

ALLOWED_ACTIONS = {"convert"}
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def deterministic_plan(prompt: str, known_files: list[Path]) -> dict:
    """Small no-AI fallback for simple requests."""
    lowered = prompt.lower()
    target = None
    for candidate in ("webp", "png", "jpeg", "jpg", "bmp", "tiff", "pdf"):
        if re.search(rf"\b{re.escape(candidate)}\b", lowered):
            target = candidate
            break
    if not target:
        return {"action": "clarify", "message": "Which output format do you want (for example PDF, PNG, or WebP)?"}
    chosen = [p for p in known_files if target in supported_targets(p)]
    if not chosen:
        chosen = [p for p in known_files if p.exists()]
    return {
        "action": "convert",
        "target": target,
        "files": [str(p) for p in chosen],
        "requires_confirmation": True,
        "message": f"Proposed conversion to {target.upper()} for {len(chosen)} file(s). Review before running."
    }

def ollama_plan(prompt: str, known_files: list[Path], model: str = "llama3.2:3b",
                endpoint: str = DEFAULT_OLLAMA_URL, timeout: int = 20) -> dict:
    """Ask a local Ollama model for structured intent; it cannot execute tools or commands."""
    allowed_files = [str(p.resolve()) for p in known_files if p.exists() and p.is_file()]
    schema_prompt = f"""
You are an intent parser for a local file converter. Do not execute anything.
Return ONLY JSON with keys action, target, file_indices, explanation.
action must be one of convert or clarify.
target must be one of png,jpg,webp,bmp,tiff,pdf or empty.
file_indices must be a list of integers referring to this numbered list:
{json.dumps(allowed_files, ensure_ascii=False)}
Only choose a target supported by the listed file type; if unclear, use clarify.
User request: {prompt}
"""
    payload = json.dumps({"model": model, "prompt": schema_prompt, "stream": False, "format": "json"}).encode()
    request = urllib.request.Request(endpoint, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = json.loads(response.read().decode("utf-8"))
        parsed = json.loads(raw.get("response", "{}"))
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
        raise RuntimeError(f"Local Ollama planner unavailable: {exc}") from exc

    action = parsed.get("action")
    target = str(parsed.get("target", "")).lower().lstrip(".")
    indices = parsed.get("file_indices", [])
    if action not in ALLOWED_ACTIONS | {"clarify"}:
        return {"action": "clarify", "message": "The local model returned an unsupported action."}
    if action != "convert" or target not in {"png", "jpg", "webp", "bmp", "tiff", "pdf"}:
        return {"action": "clarify", "message": str(parsed.get("explanation", "Please clarify the target format."))}
    if not isinstance(indices, list) or any(not isinstance(i, int) or i < 0 or i >= len(allowed_files) for i in indices):
        return {"action": "clarify", "message": "The local model returned invalid file references."}
    selected = [Path(allowed_files[i]) for i in indices]
    return {
        "action": "convert", "target": target, "files": [str(p) for p in selected],
        "requires_confirmation": True,
        "message": str(parsed.get("explanation", "Review this proposed conversion before running."))
    }
