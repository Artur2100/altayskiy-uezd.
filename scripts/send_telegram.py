#!/usr/bin/env python3
"""Send the generated AI team report to Telegram without exposing credentials."""
from __future__ import annotations

import json
import os
import sys
import uuid
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
MAX_CAPTION = 900


def telegram_request(token: str, method: str, fields: dict[str, str], file_path: Path | None = None) -> dict:
    boundary = "----AltayskiyUezd" + uuid.uuid4().hex
    chunks: list[bytes] = []
    for key, value in fields.items():
        chunks.extend([
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode(),
            value.encode("utf-8"),
            b"\r\n",
        ])
    if file_path is not None:
        chunks.extend([
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="document"; filename="{file_path.name}"\r\n'.encode(),
            b"Content-Type: text/markdown; charset=utf-8\r\n\r\n",
            file_path.read_bytes(),
            b"\r\n",
        ])
    chunks.append(f"--{boundary}--\r\n".encode())
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=b"".join(chunks),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"Telegram API HTTP {exc.code}: {detail}") from exc
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram API rejected request: {payload.get('description', 'unknown error')}")
    return payload


def main() -> int:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        print("Telegram delivery skipped: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not configured.")
        return 0

    reports = sorted(REPORT_DIR.glob("daily-ai-report-*.md"), key=lambda p: p.stat().st_mtime)
    if not reports:
        print("No AI report found; Telegram delivery skipped.", file=sys.stderr)
        return 1

    report = reports[-1]
    content = report.read_text(encoding="utf-8")
    heading = content.splitlines()[0] if content.splitlines() else "Ежедневный отчёт AI-команды"
    caption = f"{heading}\nПолный отчёт приложен файлом."
    if len(caption) > MAX_CAPTION:
        caption = caption[:MAX_CAPTION - 1] + "…"

    telegram_request(token, "sendDocument", {"chat_id": chat_id, "caption": caption}, report)
    print(f"Telegram report delivered: {report.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
