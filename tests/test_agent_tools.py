import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import competitor_research as cr
import local_agent_team as team

class CompetitorParserTests(unittest.TestCase):
    def test_extracts_public_page_signals(self):
        p=cr.Page()
        p.feed('<html><head><title>Tea</title><meta name="description" content="About"></head><body><h1>Catalog</h1><h2>Herbs</h2><img src="a.jpg" alt="Product"><a href="/shop">Shop</a></body></html>')
        self.assertEqual(p.title,"Tea")
        self.assertEqual(p.description,"About")
        self.assertEqual(p.h1,["Catalog"])
        self.assertEqual(p.h2,["Herbs"])
        self.assertEqual(p.images_alt,1)
    def test_rejects_non_https(self):
        with self.assertRaises(ValueError): cr.fetch("http://example.com")
    def test_nine_local_roles_exist(self):
        self.assertEqual(len(team.ROLES),9)
        self.assertIn("Исследователь конкурентов",team.ROLES[6][0])

if __name__=="__main__": unittest.main()
