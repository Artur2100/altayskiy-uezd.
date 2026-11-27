#!/usr/bin/env python3
"""Free competitor research from explicitly configured public URLs; stdlib only."""
from __future__ import annotations
import json, re, time\nfrom urllib.robotparser import RobotFileParser
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, urljoin
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/"config"/"competitors.json"
OUT=ROOT/"reports"/"competitor-research.json"
UA="AltayskiyUezdResearchBot/1.0 (+respectful public-page analysis)"
MAX_BYTES=1_500_000
TIMEOUT=12

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.title=""; self.description=""; self.h1=[]; self.h2=[]
        self.text=[]; self.images=0; self.images_alt=0; self.links=[]; self.current=None; self.buf=""
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ("title","h1","h2"): self.current=tag; self.buf=""
        if tag=="meta" and a.get("name","").lower()=="description": self.description=a.get("content","")
        if tag=="img":
            self.images+=1
            if a.get("alt","").strip(): self.images_alt+=1
        if tag=="a" and a.get("href"): self.links.append(a["href"])
    def handle_endtag(self,tag):
        if self.current==tag:
            v=re.sub(r"\s+"," ",self.buf).strip()
            if tag=="title": self.title=v
            elif tag=="h1": self.h1.append(v)
            elif tag=="h2": self.h2.append(v)
            self.current=None
    def handle_data(self,data):
        if self.current: self.buf+=data
        self.text.append(data)

def fetch(url):
    parsed=urlparse(url)
    if parsed.scheme!="https" or not parsed.netloc: raise ValueError("Only absolute HTTPS URLs are allowed")
    req=Request(url,headers={"User-Agent":UA,"Accept":"text/html"})
    with urlopen(req,timeout=TIMEOUT) as r:
        if urlparse(r.geturl()).scheme!="https": raise ValueError("Redirected away from HTTPS; blocked")\n        ctype=r.headers.get("Content-Type","")
        if "text/html" not in ctype: raise ValueError("URL did not return HTML")
        raw=r.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES: raw=raw[:MAX_BYTES]
        charset=r.headers.get_content_charset() or "utf-8"
        return raw.decode(charset,errors="replace"),r.geturl()

def analyze():
    config=json.loads(CONFIG.read_text(encoding="utf-8"))
    urls=config.get("urls",[])
    results=[]
    for item in urls[:30]:
        url=item.get("url") if isinstance(item,dict) else item
        label=item.get("name","") if isinstance(item,dict) else ""
        row={"name":label,"url":url,"checked_at":datetime.now(timezone.utc).isoformat()}
        try:
            html,final=fetch(url); p=Page(); p.feed(html)
            text=" ".join(p.text); words=re.findall(r"\w+",text,flags=re.UNICODE)
            row.update({"final_url":final,"title":p.title,"description":p.description,"h1":p.h1[:8],
              "h2":p.h2[:20],"word_count":len(words),"images":p.images,
              "images_with_alt":p.images_alt,"internal_link_candidates":sum(1 for x in p.links if x.startswith("/") or urlparse(x).netloc==urlparse(final).netloc),
              "status":"ok"})
        except (HTTPError,URLError,TimeoutError,ValueError,OSError) as e:
            row.update({"status":"error","error":str(e)[:300]})
        results.append(row); time.sleep(1.0)
    OUT.parent.mkdir(exist_ok=True)
    payload={"checked_at":datetime.now(timezone.utc).isoformat(),"source":"configured public URLs; no search API or paid service","results":results,
      "limitations":["No traffic, sales, conversion, keyword ranking or private marketplace data.",
      "Only explicitly configured URLs are checked; no search engine discovery.",
      "Public pages may change, block automated access or contain incomplete information."]}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Competitor pages checked: {len(results)}; report: {OUT.relative_to(ROOT)}")
    return payload

if __name__=="__main__": analyze()
