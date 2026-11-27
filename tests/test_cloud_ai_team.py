import os, sys, unittest
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

if __name__=="__main__": unittest.main()
