import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ai_team import response_text
from site_audit import PageParser


class ResponseParsingTests(unittest.TestCase):
    def test_extracts_text_from_message_items(self):
        payload = {"output": [{"type": "message", "content": [
            {"type": "output_text", "text": "Отчёт готов"}
        ]}]}
        self.assertEqual(response_text(payload), "Отчёт готов")

    def test_ignores_non_message_items(self):
        self.assertEqual(response_text({"output": [{"type": "reasoning"}]}), "")


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
