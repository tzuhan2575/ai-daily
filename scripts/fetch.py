"""抓各來源，輸出 data/candidates-YYYY-MM-DD.json（標題、連結、時間、摘要）。"""
import json, re, sys, html, time, datetime, urllib.request, xml.etree.ElementTree as ET

UA = {"User-Agent": "Mozilla/5.0"}
DAYS = 7

def get(url):
    b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20).read()
    if b[:2] == b"\x1f\x8b":
        import gzip; b = gzip.decompress(b)
    return b.decode("utf-8", "ignore")

def rss(url, source, limit=8):
    out = []
    for it in ET.fromstring(re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", get(url)).lstrip("\ufeff").strip().encode()).iter("item"):
        t = lambda k: (it.findtext(k) or "").strip()
        out.append({"source": source, "title": t("title"), "url": t("link"),
                    "date": t("pubDate"), "summary": re.sub(r"<[^>]+>", "", t("description"))[:400]})
        if len(out) >= limit: break
    return out

def hn():
    d = json.loads(get(open("sources.yml").read().split("hn: ")[1].split("\n")[0]))
    cut = time.time() - DAYS * 86400
    return [{"source": "HN", "title": h["title"], "url": h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}",
             "date": h["created_at"], "summary": f"{h['points']} 分、{h['num_comments']} 則留言"}
            for h in d["hits"] if h["created_at_i"] > cut][:10]

def hf():
    return [{"source": "HF Papers", "title": p["paper"]["title"], "url": f"https://huggingface.co/papers/{p['paper']['id']}",
             "date": p["paper"].get("publishedAt", ""), "summary": (p["paper"].get("summary") or "")[:400].replace("\n", " ")}
            for p in json.loads(get("https://huggingface.co/api/daily_papers?limit=8"))]

def anthropic():
    html = get("https://www.anthropic.com/news")
    seen, out = set(), []
    for m in re.finditer(r'href="(/news/[a-z0-9-]+)"[^>]*><h\d[^>]*>([^<]+)</h\d>(?:<p[^>]*>([^<]*)</p>)?', html):
        if m.group(1) in seen: continue
        seen.add(m.group(1))
        out.append({"source": "Anthropic", "title": m.group(2).strip(), "url": "https://www.anthropic.com" + m.group(1),
                    "date": "", "summary": (m.group(3) or "").strip()[:400]})
    return out[:8]

def newsletter(url, source, limit=3, chars=9000):
    out = []
    for it in re.findall(r"(?s)<item>(.*?)</item>", get(url))[:limit]:
        g = lambda k: (re.search(rf"(?s)<{k}>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{k}>", it) or [None, ""])[1]
        body = g("content:encoded") or g("description")
        body = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(body))))
        out.append({"source": source, "title": html.unescape(g("title")).strip(), "url": g("link").strip(),
                    "date": g("pubDate"), "summary": body[:chars]})
    return out

def arxiv(cat, source, limit=4):
    time.sleep(8)  # arXiv 要求請求間隔
    x = get(f"https://export.arxiv.org/api/query?search_query=cat:{cat}&sortBy=submittedDate&sortOrder=descending&max_results={limit}")
    out = []
    for en in re.findall(r"(?s)<entry>(.*?)</entry>", x):
        g = lambda k: re.sub(r"\s+", " ", (re.search(rf"(?s)<{k}>(.*?)</{k}>", en) or [None, ""])[1]).strip()
        out.append({"source": source, "title": g("title"), "url": g("id"), "date": g("published"), "summary": g("summary")[:400]})
    return out

jobs = {"hn": hn, "hf": hf, "anthropic": anthropic,
        "openai": lambda: rss("https://openai.com/news/rss.xml", "OpenAI"),
        "hfblog": lambda: rss("https://huggingface.co/blog/feed.xml", "HF Blog", 5),
        "arxiv_ro": lambda: arxiv("cs.RO", "arXiv cs.RO"),
        "arxiv_cv": lambda: arxiv("cs.CV", "arXiv cs.CV"),
        "latent": lambda: newsletter("https://www.latent.space/feed", "Latent Space AINews"),
        "importai": lambda: newsletter("https://importai.substack.com/feed", "Import AI", 1),
        "tldr": lambda: newsletter("https://tldr.tech/api/rss/ai", "TLDR AI", 3, 1500),
        "deepmind": lambda: rss("https://deepmind.google/blog/rss.xml", "DeepMind")}
res = []
for k, f in jobs.items():
    try: res += f()
    except Exception as e: print(f"[warn] {k}: {e}", file=sys.stderr)
path = f"data/candidates-{datetime.date.today()}.json"
json.dump(res, open(path, "w"), ensure_ascii=False, indent=1)
print(len(res), "items ->", path)
