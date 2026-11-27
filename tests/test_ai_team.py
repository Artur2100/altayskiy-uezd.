import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ai_team
from site_audit import PageParser
from send_telegram import main as telegram_main


class CloudflareRuntimeTests(unittest.TestCase):
    def test_extracts_cloudflare_text_response(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = json.dumps({
            "success": True, "result": {"response": "Командный анализ готов"}
        }).encode()
        with patch("ai_team.urllib.request.urlopen", return_value=response):
            result = ai_team.call_cloudflare("token", "account", "@cf/test/model", "prompt")
        self.assertEqual(result, "Командный анализ готов")

    def test_rejects_empty_cloudflare_response(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = json.dumps({"success": True, "result": {}}).encode()
        with patch("ai_team.urllib.request.urlopen", return_value=response):
            with self.assertRaisesRegex(RuntimeError, "empty response"):
                ai_team.call_cloudflare("token", "account", "@cf/test/model", "prompt")

    def test_missing_credentials_creates_safe_fallback_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(ai_team, "REPORT_DIR", Path(temp_dir)):
                with patch.dict(os.environ, {
                    "CLOUDFLARE_API_TOKEN": "",
                    "CLOUDFLARE_ACCOUNT_ID": "",
                    "CLOUDFLARE_AI_MODEL": ""
                }, clear=False):
                    self.assertEqual(ai_team.main(), 0)
                reports = list(Path(temp_dir).glob("daily-ai-report-*.md"))
                self.assertEqual(len(reports), 1)
                content = reports[0].read_text(encoding="utf-8")
                self.assertIn("платного fallback нет", content)
                self.assertIn("Безопасный режим", content)


class TelegramDeliveryTests(unittest.TestCase):
    def test_skips_cleanly_when_secrets_are_missing(self):
        from contextlib import redirect_stdout
        import io
        output = io.StringIO()
        with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": ""}):
            with redirect_stdout(output):
                self.assertEqual(telegram_main(), 0)
        self.assertIn("delivery skipped", output.getvalue())


class HtmlAuditParserTests(unittest.TestCase):
    def test_collects_basic_seo_fields(self):
        parser = PageParser()
        parser.feed('<html><head><title>Тест</title><meta name="description" content="Описание"><link rel="canonical" href="https://example.test"></head><body><h1>Заголовок</h1><img src="a.png" alt="Фото"></body></html>')
        self.assertEqual(parser.title, "Тест")
        self.assertTrue(parser.description)
        self.assertEqual(parser.h1_count, 1)
        self.assertEqual(parser.images_without_alt, 0)
        self.assertTrue(parser.canonical)

    def test_counts_missing_alt(self):
        parser = PageParser()
        parser.feed('<img src="a.png"><img src="b.png" alt="">')
        self.assertEqual(parser.images_without_alt, 1)


if __name__ == "__main__":
    unittest.main()
