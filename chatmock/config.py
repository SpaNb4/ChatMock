from __future__ import annotations

import os
import sys
from pathlib import Path


CLIENT_ID_DEFAULT = os.getenv("CHATGPT_LOCAL_CLIENT_ID") or "app_EMoamEEZ73f0CkXaXp7hrann"
OAUTH_ISSUER_DEFAULT = os.getenv("CHATGPT_LOCAL_ISSUER") or "https://auth.openai.com"
OAUTH_TOKEN_URL = f"{OAUTH_ISSUER_DEFAULT}/oauth/token"

CHATGPT_RESPONSES_URL = "https://chatgpt.com/backend-api/codex/responses"


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in ("1", "true", "yes", "on")


def _read_prompt_text(filename: str) -> str | None:
    candidates = [
        Path(__file__).parent.parent / filename,
        Path(__file__).parent / filename,
        Path(getattr(sys, "_MEIPASS", "")) / filename if getattr(sys, "_MEIPASS", None) else None,
        Path.cwd() / filename,
    ]
    for candidate in candidates:
        if not candidate:
            continue
        try:
            if candidate.exists():
                content = candidate.read_text(encoding="utf-8")
                if isinstance(content, str) and content.strip():
                    return content
        except Exception:
            continue
    return None


def read_base_instructions() -> str:
    content = _read_prompt_text("prompt.md")
    if content is None:
        raise FileNotFoundError("Failed to read prompt.md; expected adjacent to package or CWD.")
    return content


def read_gpt5_codex_instructions(fallback: str) -> str:
    content = _read_prompt_text("prompt_gpt5_codex.md")
    return content if isinstance(content, str) and content.strip() else fallback


def resolve_instruction_set(disable_repo_prompts: bool | None = None) -> tuple[str | None, str | None]:
    disabled = _env_bool("CHATGPT_LOCAL_DISABLE_REPO_PROMPTS", default=False)
    if disable_repo_prompts is not None:
        disabled = bool(disable_repo_prompts)
    if disabled:
        return None, None

    base = read_base_instructions()
    codex = read_gpt5_codex_instructions(base)
    return base, codex


BASE_INSTRUCTIONS, GPT5_CODEX_INSTRUCTIONS = resolve_instruction_set()
