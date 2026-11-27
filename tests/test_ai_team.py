import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stdout
import io

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ai_team
from site_audit import PageParser
from send_telegram import main as telegram_main


class OfflineAgentTests(unittest.TestCase):
    def test_all_nine_roles_are_present(self):
        report, summary = ai_team.build_report()
        self.assertEqual(summary["agents"], 9)
        for role in ("Гений креатива", "SEO-эксперт", "QA-контролёр"):
            self.assertIn(role, report)

    def test_no_ai_credentials_are_needed(self):
        with patch.dict("os.environ", {}, clear=True):
            report, summary = ai_team.build_report()
        self.assertIn("внешние AI API", report)
        self.assertEqual(summary["mode"], "offline-deterministic")

    def test_creative_agent_produces_measurable_ideas(self):
        report = ai_team.creative([{"bytes": 321}])
        self.assertIn("Метрика", report)
        self.assertIn("Гений креатива", report)

    def test_parser_extracts_seo_and_semantics(self):
        p = PageParser()
        p.feed('<html lang="ru"><head><title>Тест</title><meta name="description" content="Описание"><meta name="viewport" content="width=device-width"><link rel="canonical" href="https://example.test"></head><body><nav></nav><main><h1>Заголовок</h1><h2>Раздел</h2><img src="a.png" alt="Фото"><a href="/shop">Купить</a></main></body></html>')
        self.assertEqual(p.title, "Тест")
        self.assertEqual(p.h1, ["Заголовок"])
        self.assertTrue(p.description)
        self.assertTrue(p.viewport)
        self.assertEqual(p.links[0]["href"], "/shop")

    def test_medical_word_is_in_controlled_vocabulary(self):
        self.assertIn("лечит", ai_team.RISK)


class TelegramDeliveryTests(unittest.TestCase):
    def test_skips_cleanly_when_secrets_are_missing(self):
        output = io.StringIO()
        with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": ""}):
            with redirect_stdout(output):
                self.assertEqual(telegram_main(), 0)
        self.assertIn("delivery skipped", output.getvalue())


if __name__ == "__main__":
    unittest.main()
