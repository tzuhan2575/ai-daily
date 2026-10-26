"""讀 data/digests/*.json，產生 docs/ 靜態網站（首頁、每日頁、所有日期、名詞表）。"""
import json, glob, pathlib, html, datetime, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
CATS = {  # 分類 → (代表色, 簡短說明)
    "模型發布": "#e4572e", "政策安全": "#2e86ab", "資安": "#c0392b",
    "產業觀點": "#7b4bb7", "硬體": "#8a6f1d", "研究": "#2a9d8f", "工具": "#d97706",
}
WEEK = "一二三四五六日"
e = html.escape

issues = []
for p in sorted(glob.glob(str(ROOT / "data/digests/*.json"))):
    issues.append(json.load(open(p)))
issues.sort(key=lambda d: d["date"], reverse=True)
weeklies = sorted((json.load(open(p)) for p in glob.glob(str(ROOT / "weekly/*.json"))), key=lambda w: w["week"], reverse=True)
_cur = ROOT / "learning/curriculum.json"
curriculum = json.load(open(_cur)) if _cur.exists() else {"weeks": []}
LV = {"use": ("🔧 可立即用", "use"), "watch": ("👀 值得追蹤", "watch"), "skip": ("💤 略知即可", "skip")}

def wk(d): return "週" + WEEK[datetime.date.fromisoformat(d).weekday()]

def head(title, root, desc="每天 5 分鐘，看懂 AI 圈發生什麼"):
    return f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#faf7f2" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#14120f" media="(prefers-color-scheme: dark)">
<link rel="manifest" href="{root}manifest.webmanifest"><link rel="icon" href="{root}assets/icon.svg"><link rel="apple-touch-icon" href="{root}assets/icon-180.png">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="AI 日報">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap">
<link rel="stylesheet" href="{root}assets/site.css"></head><body><div class="wrap">'''

def nav(root, cur, cur_date=None):
    items = [("index.html", "今日", "today"), ("learn.html", "學習", "learn"), ("weekly.html", "每週", "weekly"),
             ("archive.html", "所有日期", "archive"), ("glossary.html", "名詞表", "glossary")]
    out = '<div class="sticky"><nav class="nav">' + "".join(
        f'<a href="{root}{h}" class="{"on" if k == cur else ""}">{t}</a>' for h, t, k in items) + "</nav>"
    if cur_date:
        out += '<div class="dates">' + "".join(
            f'<a href="{root}issue/{d["date"]}.html" class="{"on" if d["date"] == cur_date else ""}">'
            f'<small>{wk(d["date"])}</small>{d["date"][5:].replace("-", "/")}</a>' for d in issues[:14]) + "</div>"
    return out + "</div>"

def foot(root):
    return f'</div><script src="{root}assets/app.js"></script></body></html>'

def chips(cats, root):
    return '<div class="chips" role="tablist"><button class="chip on" data-cat="">全部</button>' + "".join(
        f'<button class="chip" data-cat="{e(c)}" style="--c:{CATS.get(c, "#666")}">{e(c)}</button>' for c in cats) + "</div>"

def impact_html(it):
    im = it.get("impact")
    if not im: return ""
    lab, cls = LV[im["level"]]
    act = f'<div class="act">▶ {e(im["action"])}</div>' if im.get("action") else ""
    return f'<div class="impact lv-{cls}"><b>🎯 對你的影響　{lab}</b><div>{e(im["text"])}</div>{act}</div>'

def lesson_btn(d):
    L = d.get("lesson")
    if not L: return ""
    return (f'<a class="lessonbtn" href="#lesson"><span>📘 今日一課 · {L["minutes"]} 分鐘</span><b>{e(L["title"])}</b></a>')

def toc_html(d):
    rows = "".join(f'<a href="#{e(it["id"])}" style="--c:{CATS.get(it["cat"], "#666")}"><i></i><span>{e(it["title"])}</span>'
                   f'<em>{LV[it["impact"]["level"]][0][:2] if it.get("impact") else ""}</em></a>' for it in d["items"])
    if d.get("lesson"): rows += f'<a href="#lesson" style="--c:#2a9d8f"><i></i><span>📘 今日一課：{e(d["lesson"]["title"])}</span><em></em></a>'
    return f'<div class="toc" id="toc"><b>本期目錄</b>{rows}</div>'

def lesson_html(d):
    L = d.get("lesson")
    if not L: return ""
    secs = "".join(f"<h4>{e(a)}</h4><p>{e(b)}</p>" for a, b in L["sections"])
    prac = "".join(f'<label class="chk"><input type="checkbox" data-k="{d["date"]}-{n}"><span>{e(t)}</span></label>' for n, t in enumerate(L["practice"]))
    ex = f'<h4>範例檔案</h4><pre>{e(L["example"])}</pre>' if L.get("example") else ""
    srcs = "；".join(e(x) for x in L["sources"])
    return (f'<section class="card lesson" id="lesson" style="--c:#2a9d8f"><span class="tag">📘 今日一課 · {L["minutes"]} 分鐘</span><h2>{e(L["title"])}</h2>'
            f'<div class="mut">為什麼今天學這個</div><p>{e(L["why_today"])}</p>{secs}'
            f'<h4>動手做（勾選記錄進度）</h4><div class="checks">{prac}</div>{ex}'
            f'<h4>貼給 Claude Code 的指令</h4><pre id="cp">{e(L["claude_prompt"])}</pre><button class="copy" data-t="cp">複製指令</button>'
            f'<div class="mut" style="margin-top:14px">來源：{srcs}</div><a class="up" href="#toc">↑ 回目錄</a></section>')

def card(it, i, issue_date, link=False):
    c = CATS.get(it["cat"], "#666")
    deep = ""
    if it.get("deep"):
        deep = f'<details><summary>📖 展開完整解析（{len(it["deep"])} 段）</summary><div class="deep">' + "".join(
            f'<h4>{e(a)}</h4><p>{e(b)}</p>' for a, b in it["deep"]) + "</div></details>"
    return f'''<article class="card{" hero" if i == 0 else ""}" id="{e(it["id"])}" data-cat="{e(it["cat"])}" style="--c:{c}">
<span class="tag">{it["emoji"]} {e(it["cat"])}</span><h2>{e(it["title"])}</h2><div class="mut">{e(it["src"])}</div>
<p class="what">{e(it["what"])}</p><div class="plain"><b>白話：</b>{e(it["plain"])}</div>
<div class="why"><b>💡 為什麼重要</b>{e(it["why"])}</div>{impact_html(it)}{deep}<a class="up" href="#toc">↑ 回目錄</a></article>'''

def issue_page(d, idx, root, is_home):
    cats = list(dict.fromkeys(i["cat"] for i in d["items"]))
    prev_ = issues[idx + 1] if idx + 1 < len(issues) else None
    next_ = issues[idx - 1] if idx > 0 else None
    mins = max(3, round(sum(len(i["what"]) + len(i["plain"]) + len(i["why"]) for i in d["items"]) / 450))
    base = "issue/" if is_home else ""
    pn = '<div class="pn">'
    pn += f'<a href="{base}{prev_["date"]}.html">← {prev_["date"]}</a>' if prev_ else "<span></span>"
    pn += (f'<a href="{base}{next_["date"]}.html">{next_["date"]} →</a>' if next_ else "<span></span>") + "</div>"
    terms = "".join(f'<div class="term"><b>{e(a)}</b>{e(b)}</div>' for a, b in d["terms"])
    return (head(f'AI 日報 {d["date"]}', root) + nav(root, "today" if is_home else "archive", d["date"]) +
        f'<header class="top"><div class="kick">AI DAILY · 第 {d["issue"]} 期</div><h1>今天 AI 圈發生了什麼</h1>'
        f'<div class="meta">{d["date"]} {wk(d["date"])} · {len(d["items"])} 則 · 約 {mins} 分鐘</div></header>'
        + lesson_btn(d) + toc_html(d) + chips(cats, root) + "<main>" + "".join(card(it, i, d["date"]) for i, it in enumerate(d["items"])) + "</main>" + lesson_html(d) + ('<a class="fab" id="fab" href="#lesson">📘 今日一課</a>' if d.get("lesson") else "")
        + f'<h2 class="sec">📚 今日新名詞</h2><div class="terms">{terms}</div>' + pn + foot(root))

def archive_page():
    cats = list(dict.fromkeys(i["cat"] for d in issues for i in d["items"]))
    body = ""
    for d in issues:
        body += f'<h3 class="day">{d["date"]} {wk(d["date"])}</h3>'
        for it in d["items"]:
            c = CATS.get(it["cat"], "#666")
            body += (f'<a class="row" href="issue/{d["date"]}.html#{e(it["id"])}" data-cat="{e(it["cat"])}" data-impact="{it.get("impact", {}).get("level", "")}" style="--c:{c}">'
                     f'<span class="tag">{it["emoji"]} {e(it["cat"])}</span><b>{e(it["title"])}</b><small>{e(it["what"][:60])}…</small></a>')
    return (head("所有日期｜AI 日報", "") + nav("", "archive") + '<header class="top"><h1>所有日期</h1><div class="meta">依分類篩選過去每一則</div></header>'
            + chips(cats, "") + '<label class="usef"><input type="checkbox" id="useonly"> 只看 🔧 可立即用</label>' + f"<main>{body}</main>" + foot(""))

def glossary_page():
    seen = {}
    for d in reversed(issues):
        for a, b in d["terms"]: seen.setdefault(a, (b, d["date"]))
    rows = "".join(f'<div class="term" data-q="{e(a.lower())} {e(b)}"><b>{e(a)}</b>{e(b)}<small> · {dt}</small></div>' for a, (b, dt) in sorted(seen.items()))
    return (head("名詞表｜AI 日報", "") + nav("", "glossary") + f'<header class="top"><h1>名詞表</h1><div class="meta">累積 {len(seen)} 個，之後越來越多</div></header>'
            '<input id="q" class="search" placeholder="搜尋名詞…" type="search">' + f'<div class="terms" id="terms">{rows}</div>' + foot(""))

def learn_page():
    weeks = ""
    for w in curriculum["weeks"]:
        st = {"current": "進行中", "done": "已完成", "next": "預計"}.get(w["status"], "")
        weeks += (f'<div class="wk {w["status"]}"><div class="wkh"><b>第 {w["week"]} 週・{e(w["title"])}</b><span>{st}</span></div>'
                  + "".join(f'<i>{e(t)}</i>' for t in w["topics"]) + "</div>")
    lessons = ""
    for d in issues:
        L = d.get("lesson")
        if L: lessons += f'<a class="row" href="issue/{d["date"]}.html#lesson" style="--c:#2a9d8f"><span class="tag">📘 {d["date"]} · {L["minutes"]} 分鐘</span><b>{e(L["title"])}</b><small>{e(L["why_today"][:60])}…</small></a>'
    return (head("學習｜AI 日報", "") + nav("", "learn") + '<header class="top"><h1>學習路徑</h1><div class="meta">'
            + e(curriculum.get("track", "")) + '・每週日更新</div></header>' + weeks + '<h2 class="sec">📘 今日一課列表</h2>' + (lessons or "<p>還沒有課程。</p>") + foot(""))

def weekly_card(w):
    acts = "".join(f'<div class="act-item"><b>{n}. {e(a["title"])}</b><p>{e(a["why"])}</p><p class="how">▶ {e(a["how"])}</p></div>' for n, a in enumerate(w["actions"], 1))
    summ = "".join(f"<li>{e(x)}</li>" for x in w["summary"])
    return f'<article class="card" id="{e(w["week"])}"><span class="tag">🗓 {e(w["week"])}・{e(w["range"])}</span><h2>本週我該做什麼</h2>{acts}<h4>本週脈絡</h4><ul>{summ}</ul></article>'

def weekly_index():
    body = "".join(weekly_card(w) for w in weeklies) if weeklies else '<div class="card"><p>第一份週報會在週日 08:00（台灣時間）自動產生：把一週的新聞整理成 3 到 5 件「我該做什麼」，並更新學習路徑。</p></div>'
    return head("每週｜AI 日報", "") + nav("", "weekly") + '<header class="top"><h1>每週清單</h1><div class="meta">本週我該做什麼</div></header>' + body + foot("")

CSS = r'''
:root{--bg:#faf7f2;--fg:#1f1b16;--mut:#7a7066;--card:#fff;--line:#e8e1d6;--acc:#e4572e;--hero:#ffe9c7;--herofg:#1f1b16}
@media(prefers-color-scheme:dark){:root{--bg:#14120f;--fg:#f3ede4;--mut:#a69b8d;--card:#1e1b17;--line:#2f2a24;--hero:#3b2f1d;--herofg:#f6ecd9}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.95 -apple-system,BlinkMacSystemFont,"Noto Sans TC",sans-serif;letter-spacing:.03em}
.wrap{max-width:720px;margin:0 auto;padding:12px 16px calc(80px + env(safe-area-inset-bottom))}
a{color:inherit}
.nav{display:flex;gap:6px;margin:4px 0 8px;position:sticky;top:0;background:var(--bg);padding:8px 0;z-index:5}
.nav a{text-decoration:none;padding:6px 14px;border-radius:99px;font-size:14px;color:var(--mut)}.nav a.on{background:var(--fg);color:var(--bg);font-weight:700}
header.top{padding:18px 0 14px;border-bottom:2px solid var(--fg);margin-bottom:14px}
.kick{font-size:12px;letter-spacing:.2em;color:var(--acc);font-weight:700}
h1{font:700 34px/1.25 -apple-system,BlinkMacSystemFont,"Noto Sans TC",sans-serif;margin:6px 0}
.meta,.mut{color:var(--mut);font-size:14px}
.chips{display:flex;gap:8px;overflow-x:auto;padding:4px 0 10px;scrollbar-width:none}.chips::-webkit-scrollbar{display:none}
.chip{flex:none;border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:99px;padding:6px 14px;font:inherit;font-size:14px;cursor:pointer}
.chip.on{background:var(--c,var(--fg));color:#fff;border-color:transparent;font-weight:700}
.chip[data-cat=""].on{background:var(--fg);color:var(--bg)}
.card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:26px 24px;margin:22px 0}
.card.hero{background:var(--hero);color:var(--herofg);border:none}.card.hero .mut{color:inherit;opacity:.65}
.tag{display:inline-block;font-size:12px;font-weight:700;padding:3px 10px;border-radius:99px;background:color-mix(in srgb,var(--c) 16%,transparent);color:var(--c);line-height:1.8}
h2{font:700 22px/1.45 -apple-system,BlinkMacSystemFont,"Noto Sans TC",sans-serif;margin:10px 0 4px}
.what{margin:14px 0}
.plain{border-left:4px solid var(--acc);background:color-mix(in srgb,var(--acc) 8%,transparent);padding:10px 14px;border-radius:0 12px 12px 0;margin:14px 0;font-size:15px}
.plain b{color:var(--acc)}.hero .plain{background:rgba(255,255,255,.5)}[data-theme] .hero .plain{background:rgba(255,255,255,.5)}
@media(prefers-color-scheme:dark){.hero .plain{background:rgba(255,255,255,.08)}}
.why{font-size:15px}.why b{margin-right:6px}
details{margin-top:16px;border-top:1px dashed var(--line);padding-top:12px}
summary{cursor:pointer;font-weight:700;color:var(--acc);list-style:none}summary::-webkit-details-marker{display:none}
.deep h4{margin:18px 0 0;font-size:15px}.deep p{margin:0;font-size:15px}
.sec{font-size:20px;margin:36px 0 10px}
.terms{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.term{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px 14px;font-size:14px;line-height:1.7}.term b{display:block;color:var(--acc);font-size:15px}.term small{color:var(--mut)}
.pn{display:flex;justify-content:space-between;margin-top:30px}.pn a{text-decoration:none;color:var(--acc);font-weight:700}
.day{margin:28px 0 6px;font-size:15px;color:var(--mut)}
.row{display:block;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px 16px;margin:8px 0;text-decoration:none}
.row b{display:block;font-size:16px;margin-top:2px}.row small{color:var(--mut);font-size:13px;line-height:1.6;display:block}
.search{width:100%;padding:10px 14px;border-radius:12px;border:1px solid var(--line);background:var(--card);color:var(--fg);font:inherit;margin-bottom:14px}
[hidden]{display:none!important}
.lessonbtn{display:block;text-decoration:none;background:linear-gradient(135deg,#2a9d8f,#1f7a6f);color:#fff;border-radius:16px;padding:14px 18px;margin:0 0 12px;line-height:1.6}
.lessonbtn span{display:block;font-size:12px;opacity:.85;letter-spacing:.08em}.lessonbtn b{font-size:17px}
.fab{position:fixed;right:16px;bottom:calc(16px + env(safe-area-inset-bottom));background:#2a9d8f;color:#fff;text-decoration:none;font-weight:700;font-size:15px;padding:10px 16px;border-radius:99px;box-shadow:0 4px 14px rgba(0,0,0,.25);z-index:6;transition:opacity .2s}
.fab.gone{opacity:0;pointer-events:none}
.sticky{position:sticky;top:0;background:var(--bg);z-index:5;margin:0 -16px;padding:0 16px 4px}
.nav{position:static;overflow-x:auto;scrollbar-width:none;margin:4px 0 4px;padding:8px 0}.nav::-webkit-scrollbar{display:none}.nav a{flex:none}
.dates{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;padding:2px 0 6px}.dates::-webkit-scrollbar{display:none}
.dates a{flex:none;text-decoration:none;text-align:center;border:1px solid var(--line);background:var(--card);border-radius:12px;padding:3px 10px;font-size:14px;line-height:1.5}
.dates a small{display:block;font-size:11px;color:var(--mut)}.dates a.on{background:var(--fg);color:var(--bg);border-color:transparent}.dates a.on small{color:inherit;opacity:.7}
.card{scroll-margin-top:118px}
.toc{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px 16px;margin:0 0 10px;font-size:15px}
.toc>b{display:block;margin-bottom:4px}.toc a{display:flex;gap:10px;align-items:baseline;text-decoration:none;padding:5px 0;line-height:1.6}
.toc i{flex:none;width:8px;height:8px;border-radius:50%;background:var(--c);transform:translateY(-1px)}.toc span{flex:1}.toc em{font-style:normal;font-size:12px;color:var(--mut)}
.impact{margin:16px 0;border-radius:14px;padding:12px 14px;font-size:15px;border:1px solid transparent}
.impact>b{display:block;margin-bottom:2px}.impact .act{margin-top:6px;font-weight:700}
.lv-use{background:color-mix(in srgb,#16a34a 12%,transparent);border-color:color-mix(in srgb,#16a34a 40%,transparent)}
.lv-watch{background:color-mix(in srgb,#d97706 12%,transparent);border-color:color-mix(in srgb,#d97706 35%,transparent)}
.lv-skip{background:color-mix(in srgb,#888 10%,transparent)}
.hero .impact{color:var(--herofg)}
.up{display:block;text-align:right;margin-top:14px;font-size:13px;color:var(--mut);text-decoration:none}
.lesson h4{margin:18px 0 0;font-size:15px}.lesson p{margin:0;font-size:15px}
pre{background:color-mix(in srgb,var(--fg) 7%,transparent);border-radius:12px;padding:12px 14px;white-space:pre-wrap;word-break:break-word;font:13px/1.7 ui-monospace,Menlo,monospace;letter-spacing:0;margin:8px 0}
.copy{background:var(--acc);color:#fff;border:0;border-radius:10px;padding:8px 16px;font:inherit;font-size:14px;cursor:pointer}
.chk{display:flex;gap:10px;align-items:flex-start;font-size:15px;padding:4px 0;cursor:pointer}.chk input{margin-top:8px;width:18px;height:18px;flex:none}.chk input:checked+span{opacity:.5;text-decoration:line-through}
.wk{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px 16px;margin:12px 0}.wk.current{border:2px solid var(--acc)}.wk.done{opacity:.6}
.wkh{display:flex;justify-content:space-between;align-items:baseline}.wkh span{font-size:12px;color:var(--mut)}
.wk i{display:inline-block;font-style:normal;font-size:13px;background:color-mix(in srgb,var(--acc) 10%,transparent);border-radius:99px;padding:1px 10px;margin:6px 6px 0 0}
.act-item{margin:14px 0}.act-item p{margin:0;font-size:15px}.how{font-weight:700;color:var(--acc)}
.usef{display:block;margin:4px 0 8px;font-size:14px;cursor:pointer}
@media(max-width:520px){.card{scroll-margin-top:112px}.terms{grid-template-columns:1fr}h1{font-size:28px}.card{padding:22px 18px}}
'''

JS = r'''
(function(){
  var chips=document.querySelectorAll(".chip"),items=document.querySelectorAll("[data-cat]:not(.chip)");
  function sel(c){chips.forEach(function(b){b.classList.toggle("on",b.dataset.cat===c)});
    items.forEach(function(x){x.hidden=!!c&&x.dataset.cat!==c});}
  chips.forEach(function(b){b.addEventListener("click",function(){sel(b.dataset.cat)})});
  var uo=document.getElementById("useonly");
  function ap(){var c=(document.querySelector(".chip.on")||{dataset:{cat:""}}).dataset.cat,u=uo&&uo.checked;
    items.forEach(function(x){x.hidden=(!!c&&x.dataset.cat!==c)||(u&&x.dataset.impact!=="use")});}
  if(uo){chips.forEach(function(b){b.addEventListener("click",function(){setTimeout(ap,0)})});uo.addEventListener("change",ap)}
  document.querySelectorAll(".copy").forEach(function(b){b.addEventListener("click",function(){
    var t=document.getElementById(b.dataset.t).textContent;
    (navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(function(){b.textContent="已複製 ✓"},function(){var r=document.createRange();r.selectNode(document.getElementById(b.dataset.t));getSelection().removeAllRanges();getSelection().addRange(r);b.textContent="已選取，請按複製"})})});
  document.querySelectorAll(".chk input").forEach(function(c){var k="aid-"+c.dataset.k;
    try{c.checked=localStorage.getItem(k)==="1"}catch(e){}
    c.addEventListener("change",function(){try{localStorage.setItem(k,c.checked?"1":"0")}catch(e){}})});
  var fab=document.getElementById("fab"),ls=document.getElementById("lesson");
  if(fab&&ls&&window.IntersectionObserver){new IntersectionObserver(function(en){fab.classList.toggle("gone",en[0].isIntersecting)},{threshold:.05}).observe(ls)}
  var q=document.getElementById("q");
  if(q)q.addEventListener("input",function(){var v=q.value.trim().toLowerCase();
    document.querySelectorAll(".term").forEach(function(t){t.hidden=!!v&&t.dataset.q.indexOf(v)<0})});
  if(location.hash){var t=document.querySelector(location.hash);if(t){var d=t.querySelector("details");if(d)d.open=true}}
})();
'''

ICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="22" fill="#e4572e"/><text x="50" y="66" font-size="46" font-weight="800" text-anchor="middle" fill="#fff" font-family="-apple-system,Helvetica,Arial,sans-serif">AI</text></svg>'''

def main():
    (DOCS / "assets").mkdir(parents=True, exist_ok=True); (DOCS / "issue").mkdir(exist_ok=True)
    (DOCS / "assets/site.css").write_text(CSS); (DOCS / "assets/app.js").write_text(JS); (DOCS / "assets/icon.svg").write_text(ICON)
    (DOCS / "manifest.webmanifest").write_text(json.dumps({"name": "AI 日報", "short_name": "AI 日報", "start_url": "./index.html", "display": "standalone",
        "background_color": "#faf7f2", "theme_color": "#e4572e", "icons": [{"src": "assets/icon-180.png", "sizes": "180x180", "type": "image/png"}, {"src": "assets/icon.svg", "sizes": "any", "type": "image/svg+xml"}]}, ensure_ascii=False))
    try:
        from PIL import Image, ImageDraw, ImageFont
        im = Image.new("RGB", (180, 180), "#e4572e"); dr = ImageDraw.Draw(im)
        f = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 92)
        w = dr.textlength("AI", font=f); dr.text(((180 - w) / 2, 34), "AI", fill="white", font=f); im.save(DOCS / "assets/icon-180.png")
    except Exception as ex: print("icon png skipped:", ex)
    (DOCS / "index.html").write_text(issue_page(issues[0], 0, "", True))
    for i, d in enumerate(issues):
        (DOCS / f"issue/{d['date']}.html").write_text(issue_page(d, i, "../", False))
    (DOCS / "learn.html").write_text(learn_page()); (DOCS / "weekly.html").write_text(weekly_index())
    (DOCS / "archive.html").write_text(archive_page()); (DOCS / "glossary.html").write_text(glossary_page())
    (DOCS / ".nojekyll").write_text("")
    print("built", len(issues), "issues,", sum(len(d["items"]) for d in issues), "items")
main()
