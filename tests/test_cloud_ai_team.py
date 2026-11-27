import json, os, re, sys, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import cloud_ai_team as cloud

class CloudTeamTests(unittest.TestCase):
 def test_exactly_nine_distinct_llm_roles(self):
  self.assertEqual(len(cloud.ROLES),9)
  self.assertEqual(len({x["name"] for x in cloud.ROLES}),9)
 def test_only_free_model_is_allowed(self):
  self.assertEqual(cloud.MODEL,"gemini-2.5-flash-lite")
  self.assertEqual(cloud.MAX_MODEL_CALLS,9)
  self.assertEqual(cloud.MAX_GROUNDED_CALLS,1)
 def test_competitor_research_role_uses_search(self):
  role=next(x for x in cloud.ROLES if x["name"]=="Исследователь конкурентов")
  self.assertIn("Google Search",role["task"])
 def test_no_api_key_stops_before_import_or_requests(self):
  with patch.dict(os.environ,{"GEMINI_API_KEY":""},clear=False):
   with self.assertRaisesRegex(RuntimeError,"Missing GEMINI_API_KEY"):
    cloud.main()


class SiteFoundationTests(unittest.TestCase):
 def test_homepage_canonical_and_open_graph_match(self):
  html=(ROOT/"index.html").read_text(encoding="utf-8")
  canonical=re.search(r'<link rel="canonical" href="([^"]+)"',html)
  og=re.search(r'<meta property="og:url" content="([^"]+)"',html)
  self.assertIsNotNone(canonical)
  self.assertIsNotNone(og)
  self.assertEqual(canonical.group(1),og.group(1))

 def test_catalog_variants_are_preserved_and_grouped_in_shop(self):
  data=json.loads((ROOT/"content/products.json").read_text(encoding="utf-8"))
  items=data["items"]
  self.assertEqual(len(items),10)
  self.assertEqual(len({item["id"] for item in items}),len(items))
  shop=(ROOT/"shop.html").read_text(encoding="utf-8")
  self.assertIn("const grouped=new Map()",shop)
  self.assertIn("item.weights=[...new Set",shop)
  nettle=[x for x in items if x["name"]=="Крапива"]
  self.assertEqual(sorted({w for x in nettle for w in x["weights"]}),[50,100])

 def test_library_has_one_primary_heading(self):
  html=(ROOT/"library.html").read_text(encoding="utf-8")
  self.assertEqual(len(re.findall(r"<h1\b",html,re.I)),1)

 def test_sitemap_article_urls_exist(self):
  sitemap=(ROOT/"sitemap.xml").read_text(encoding="utf-8")
  article_files={p.name for p in (ROOT/"articles").glob("*.html")}
  urls=re.findall(r"<loc>https://altayskiy-uezd\.ru/articles/([^<]+)</loc>",sitemap)
  self.assertTrue(urls)
  self.assertEqual(set(urls)-article_files,set())

if __name__=="__main__": unittest.main()
