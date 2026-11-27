#!/usr/bin/env python3
"""Nine deterministic offline specialist roles; stdlib only, no external AI."""
from __future__ import annotations
import json, re
from collections import Counter
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"reports"
SKIP={".git",".github","node_modules","venv",".venv","dist","build"}
RISK=("лечит","вылечивает","излечивает","предотвращает заболевание","профилактика заболевания","нормализует давление","очищает печень","выводит токсины")
CTA=("купить","ozon","wildberries","заказать","смотреть товар")

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title=self.desc=self.canonical=self.lang=""
        self.viewport=False; self.h1=[]; self.h2=[]; self.images=[]; self.links=[]
        self.text=[]; self.cap=None; self.buf=""; self.link=None; self.body=False
        self.main=0; self.nav=0
    def handle_starttag(self,t,attrs):
        a=dict(attrs)
        if t=="html": self.lang=a.get("lang","")
        if t=="meta":
            if a.get("name","").lower()=="description": self.desc=a.get("content","").strip()
            if a.get("name","").lower()=="viewport": self.viewport=bool(a.get("content","").strip())
        if t=="link" and a.get("rel","").lower()=="canonical": self.canonical=a.get("href","").strip()
        if t in ("title","h1","h2"): self.cap=t; self.buf=""
        if t=="img": self.images.append({"src":a.get("src",""),"alt":a.get("alt","")})
        if t=="a": self.link={"href":a.get("href",""),"text":""}
        if t=="main": self.main+=1
        if t=="nav": self.nav+=1
        if t=="body": self.body=True
    def handle_endtag(self,t):
        if self.cap==t:
            v=re.sub(r"\s+"," ",self.buf).strip()
            if t=="title": self.title=v
            elif t=="h1": self.h1.append(v)
            elif t=="h2": self.h2.append(v)
            self.cap=None
        if t=="a" and self.link is not None: self.links.append(self.link); self.link=None
        if t=="body": self.body=False
    def handle_data(self,d):
        if self.cap: self.buf+=d
        if self.link is not None: self.link["text"]+=d
        if self.body: self.text.append(d)

def files():
    return sorted(p for p in ROOT.rglob("*") if p.is_file()
      and not any(x in SKIP for x in p.relative_to(ROOT).parts)
      and p.suffix.lower() in {".html",".htm",".md"})

def scan(fs):
    out=[]
    for p in fs:
        if p.suffix.lower() not in {".html",".htm"}: continue
        q=Parser(); q.feed(p.read_text(encoding="utf-8",errors="replace"))
        rel=p.relative_to(ROOT).as_posix(); body=" ".join(q.text); issues=[]
        if not q.title: issues.append(("P1","Нет title"))
        if not q.desc: issues.append(("P1","Нет meta description"))
        elif not 70<=len(q.desc)<=180: issues.append(("P2",f"Description длиной {len(q.desc)} символов"))
        if not q.h1: issues.append(("P1","Нет H1"))
        elif len(q.h1)>1: issues.append(("P2",f"Несколько H1: {len(q.h1)}"))
        if not q.canonical: issues.append(("P2","Нет canonical"))
        if not q.lang: issues.append(("P2","Нет lang"))
        if not q.viewport: issues.append(("P1","Нет viewport"))
        if not q.main: issues.append(("P2","Нет main"))
        if not q.nav: issues.append(("P2","Нет nav"))
        if not q.h2: issues.append(("P3","Нет H2"))
        for im in q.images:
            if not im["alt"].strip(): issues.append(("P2","Нет alt: "+im["src"]))
        hits=[x for x in RISK if x.casefold() in body.casefold()]
        if hits: issues.append(("P0","Проверить медицинские формулировки: "+", ".join(hits)))
        out.append({"path":rel,"title":q.title,"desc":q.desc,"h1":q.h1,"h2":q.h2,
          "images":q.images,"links":q.links,"body":body,"issues":issues,
          "cta":any(x in body.casefold() for x in CTA),"bytes":p.stat().st_size})
    return out

IDEAS=[
("Паспорт товара","Показать только подтверждённые сведения: масса, форма, состав с этикетки и документы при наличии.","Клики по паспорту и переходы к товару","Средняя"),
("Редакционный маршрут","Добавить в конце статей 2–3 релевантных материала для следующего чтения.","Клики по внутренним ссылкам","Низкая"),
("Сравнение форматов","Сделать нейтральную таблицу различий на основе подтверждённых карточек.","Использование сравнения и переходы к SKU","Средняя"),
("Чек-лист этикетки","Создать памятку по чтению этикетки без неподтверждённых свойств товаров.","Переходы к каталогу","Низкая"),
("Карта знаний","Сгруппировать статьи по ботанике, качеству сырья, выбору и безопасности.","Глубина просмотра раздела","Средняя"),
("Блок доверия","Показывать только подтверждённые сведения о бренде, упаковке и документах.","Клики по блоку","Низкая"),
("Контекстные переходы","Связать обучающие материалы с релевантными категориями каталога.","CTR внутренних переходов","Низкая"),
("Дата проверки статьи","Показывать дату редакционной проверки и источники после фактчекинга.","Доля статей с источниками","Средняя"),
("Навигация по задачам","Помочь выбрать по форме и формату, не по обещаниям влияния на здоровье.","Клики по фильтрам","Средняя")]

def creative(pages):
    start=sum(x.get("bytes",0) for x in pages)%len(IDEAS)
    rows=["### 1. Гений креатива","Генератор гипотез на основе библиотеки сценариев; это не языковая модель."]
    for i in range(3):
        n,d,m,e=IDEAS[(start+i)%len(IDEAS)]
        rows.append(f"{i+1}. **{n}.** {d} Метрика: {m}. Трудоёмкость: {e}.")
    return "\n".join(rows)

def build_report():
    now=datetime.now(ZoneInfo("Asia/Barnaul")); fs=files(); ps=scan(fs)
    issues=[(p["path"],a,b) for p in ps for a,b in p["issues"]]
    counts=Counter(x[1] for x in issues)
    short=[(p["path"],len(p["body"].split())) for p in ps if 0<len(p["body"].split())<250]
    titles={}
    for p in ps:
        if p["title"]: titles.setdefault(p["title"].casefold(),[]).append(p["path"])
    dups=[v for v in titles.values() if len(v)>1]
    risky=[x for x in issues if x[1]=="P0"]
    ranked=sorted(issues,key=lambda x:({"P0":0,"P1":1,"P2":2,"P3":3}[x[1]],x[0]))
    priority="\n".join(f"- **{a}** {p} — {b}" for p,a,b in ranked[:10]) or "- По контрольному набору замечаний нет."
    sections=[
"### 2. Стратег / Project Manager\n"+priority+"\nВсе приоритеты требуют подтверждения владельцем.",
"### 3. SEO-эксперт\n"+f"- Проверено HTML-страниц: {len(ps)}. Пропуски title, description, H1, canonical и viewport внесены в реестр замечаний.\n- Позиции, индексация и поисковый спрос без Search Console не измеряются.",
"### 4. Главный редактор\n"+f"- Файлов контента: {len(fs)}; коротких HTML-текстов менее 250 слов: {len(short)}; повторяющихся title: {len(dups)}; медицинских флагов: {len(risky)}.\n"+"\n".join(f"- {p}: около {n} слов" for p,n in short[:8])+"\nЭто сигналы для ручной оценки, не автоматический вердикт качества.",
"### 5. UX/UI-дизайнер\n"+f"- Без viewport: {sum(any('viewport' in z.lower() for _,z in p['issues']) for p in ps)}; без main: {sum(any('main' in z.lower() for _,z in p['issues']) for p in ps)}; без CTA-слов: {sum(not p['cta'] for p in ps)}.\n- Визуальный рендер, контраст и реальные мобильные сценарии не проверяются.",
creative(ps),
"### 6. Маркетолог / аналитик\n"+f"- CTA-словарь найден на {sum(p['cta'] for p in ps)} из {len(ps)} HTML-страниц; это не конверсия.\n- Гипотеза: контекстные ссылки из статей к товарам, измерять CTR.\n- Гипотеза: единый блок выбора маркетплейса, измерять клики по площадкам.\n- Продажи, трафик и выручка из репозитория недоступны.",
"### 7. Исследователь конкурентов\n- Внешние сайты не открываются; конкуренты не проверялись.\n- Для ручного сравнения: ассортимент, карточки, подтверждения качества, глубина материалов и путь к покупке. Не заполнять пробелы догадками.",
"### 8. Разработчик\n"+f"- Замечаний: {len(issues)} (P0 {counts['P0']}, P1 {counts['P1']}, P2 {counts['P2']}, P3 {counts['P3']}).\n- Сначала подготовить малые исправления P0/P1 в отдельной ветке. Не генерировать автоматически alt, состав и медицинские утверждения.\n- Файлы сайта не изменяются и PR не создаётся этим запуском.",
"### 9. QA-контролёр\n"+f"- HTML-страниц: {len(ps)}; файлов контента: {len(fs)}.\n- Перед PR: unit tests, HTML-структура, локальные ссылки/ресурсы, отсутствие секретов, ручной просмотр desktop/mobile.\n- Медицинские совпадения — предварительные флаги."]
    lines=[f"# Ежедневный отчёт команды «Алтайский уезд» — {now:%d.%m.%Y}",f"Время: {now:%H:%M} (Asia/Barnaul)","**Режим:** офлайн-анализ исходников; внешние AI API и веб-запросы не используются.","","## Сводка",f"- HTML-страниц: {len(ps)}",f"- Файлов контента: {len(fs)}",f"- Замечаний: {len(issues)}","- Роли: 9 из 9","",*sections,"","## Границы достоверности","- Девять специализированных программных ролей, не девять независимых языковых моделей.","- Веб-исследование, поисковые позиции, продажи, трафик и конверсии не проверялись.","- Визуальный рендер не проверялся; научная и юридическая достоверность требует ручной оценки.","- Сайт не изменялся; merge и deploy не выполнялись.","","## Реестр замечаний"]
    lines += [f"- **{a}** {p} — {b}" for p,a,b in issues]
    summary={"date":now.strftime("%Y-%m-%d"),"mode":"offline-deterministic","agents":9,"html_pages":len(ps),"content_files":len(fs),"issues_total":len(issues),"priority_counts":dict(counts),"issues":[{"path":p,"priority":a,"issue":b} for p,a,b in issues]}
    return "\n".join(lines)+"\n",summary

def main():
    OUT.mkdir(parents=True,exist_ok=True); report,summary=build_report()
    md=OUT/f"daily-ai-report-{summary['date']}.md"; js=OUT/f"daily-ai-report-{summary['date']}.json"
    md.write_text(report,encoding="utf-8"); js.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Report written: {md.relative_to(ROOT)}")
    print(f"Agents completed: 9/9; HTML pages: {summary['html_pages']}; issues: {summary['issues_total']}")
    return 0
if __name__=="__main__": raise SystemExit(main())
