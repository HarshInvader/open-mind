#!/usr/bin/env python3
"""Build the Open Mind site.

Run from the repo root:  python3 -I site/build.py
Inputs: site/content.json, site/findings.json, site/news.json, board/board.db (read only), and the repo files the
figures cite (see site/figs.py). Brand: site/art.py and site/brand.css. News pictures: site/illustrate_news.py
(run it with .venv/bin/python when news.json gains an item; the build falls back to no picture if one is missing).
Writes site/dist/: static pages that work from file:// and on Cloudflare Pages. Fails if any internal link breaks.
"""
import csv, html, html.parser, importlib.util, json, re, shutil, sqlite3, time
from pathlib import Path


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def news_date(s):
    """2026-05-28 -> 28 May 2026; 2026-06 -> Jun 2026; anything else (2001-2020) as given."""
    p = s.split("-")
    if len(p) == 3 and all(x.isdigit() for x in p):
        return f"{int(p[2])}\u00a0{MONTHS[int(p[1]) - 1]} {p[0]}"
    if len(p) == 2 and len(p[1]) == 2 and p[1].isdigit():
        return f"{MONTHS[int(p[1]) - 1]} {p[0]}"
    return s


def news_head(s):
    """Drop a trailing author list in brackets: the card already shows the authors."""
    return re.sub(r"\s*\((?=[^()]*(,|et al))[^()]*\)\s*$", "", s)

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DIST = SITE / "dist"
C = json.loads((SITE / "content.json").read_text())
E = html.escape


def load(name):
    spec = importlib.util.spec_from_file_location("om_" + name, SITE / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


ART, FG, CH = load("art"), load("figs"), load("chrome")
LOGO = json.loads((SITE / "logo_paths.json").read_text())
LOGO_WORDS = [("Open|Regular", "soft"), ("Mind|Bold", "ink")]  # "Open" light, "Mind" heavy, beside the Necker cube


def logo(cls="wordmark", show_mark=True):
    return CH.lockup(LOGO, LOGO_WORDS, ART.MARK, cls=cls, show_mark=show_mark)
NAME = C["name"]
GOAL = C["goal"]

PAGES = [("index.html", "Home"), ("findings.html", "Findings"), ("theories.html", "Theories"), ("approach.html", "Approach"),
         ("tracker.html", "Tracker"), ("news.html", "News"), ("contribute.html", "Contribute"), ("data.html", "Data"), ("resources.html", "Resources")]


def md(s):
    """Tiny inline markup: **bold**, `code`."""
    s = re.sub(r"&quot;(.+?)&quot;", "\u201c\\1\u201d", E(s))
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)  # [text](url)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", s)


def mark_svg(cls="mark"):
    return f'<svg class="{cls}" viewBox="0 0 32 32" aria-hidden="true" focusable="false">{ART.MARK}</svg>'


REPO = "https://github.com/HarshInvader/open-mind"
NAV_GROUPS = (
    ("Research", (("findings.html", "Findings", "What is known, and what we found", "find"),
                  ("theories.html", "Theories", "The field of theories we score", "theory"),
                  ("approach.html", "Approach", "How every idea gets tested", "approach"),
                  ("news.html", "News", "New papers, summarised", "news"),
                  ("tracker.html", "Tracker", "Progress and the live task board", "tracker"))),
    ("Resources", (("data.html", "Open data", "Every consciousness dataset, used or not", "data"),
                   ("resources.html#logo", "Logo", "Free to download", "logo"),
                   ("resources.html#files", "Research files", "Notes, plans and results", "files"),
                   (REPO, "Code on GitHub", "Everything we run, in the open", "code"),
                   ("../index.html", "Open Citizen Science", "Our sister projects", "family"))),
)


def layout(fname, title, desc, body):
    nav = CH.nav_items(NAV_GROUPS, fname)
    foot = "".join(f'<a href="{f}"{" aria-current=page" if f == fname else ""}>{E(n)}</a>' for f, n in PAGES)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<meta name="color-scheme" content="light dark">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<script>(function(){{var t=null;try{{t=new URLSearchParams(location.search).get('theme')||localStorage.getItem('om-theme')}}catch(e){{}}if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);document.documentElement.classList.add('js')}})();</script>
<link rel="preload" href="fonts/OpenIndusText-Bold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/OpenIndusText-Regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="site.css"></head>
<body class="{"home" if fname == "index.html" else ""}"><a class="skip" href="#main">Skip to content</a>
<header class="site-head" id="site-head"><div class="wrap head-row">
<a class="brand" href="index.html" aria-label="{E(NAME)} home">{logo()}</a>
<button class="menu-btn" type="button" id="menu-btn" aria-expanded="false" aria-controls="site-nav"><svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path class="m1" d="M3 6h14"/><path class="m2" d="M3 10h14"/><path class="m3" d="M3 14h14"/></svg><span>Menu</span></button>
<nav class="site-nav" id="site-nav" aria-label="Main"><ul>{nav}</ul></nav>
<button class="theme" type="button" id="theme" aria-label="Colour theme: automatic"><svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="10" cy="10" r="7"/><path d="M10 3a7 7 0 0 1 0 14z" fill="currentColor" stroke="none"/></svg><span id="theme-label">Auto</span></button>
</div></header>
<main id="main" class="wrap" tabindex="-1">{body}</main>
<footer class="site-foot"><div class="wrap foot-row">
<div class="foot-brand"><div>{logo()}<p>Goal: {E(GOAL[0].lower() + GOAL[1:])}.</p><p>An open research project run by a human lead and a team of AI agents. Every result can be rerun from code.</p></div></div>
<nav class="foot-cols" aria-label="Site map">
<div class="foot-links"><h2 class="foot-h">Pages</h2>{foot}</div>
<div class="foot-links"><h2 class="foot-h">Contribute</h2><a href="{REPO}">Code and data</a><a href="{REPO}/blob/main/CONTRIBUTING.md">How to contribute</a><a href="{REPO}/blob/main/board/TASKS.md">Open tasks</a><a href="news.xml">News feed (RSS)</a></div>
<div class="foot-links"><h2 class="foot-h">Family</h2><a href="../index.html">Open Citizen Science</a><a href="{REPO}/blob/main/LICENSING.md">Licences</a><a href="resources.html#logo">Logo and typeface</a></div>
</nav>
<p class="foot-note">None of this explains why experience exists at all. Body type: Open Indus Text, from Instrument Sans (OFL). Built {time.strftime('%d %b %Y').lstrip('0')}.</p>
</div><div class="wrap"><a class="ocs-banner" href="../index.html"><svg viewBox="0 0 32 32" aria-hidden="true" focusable="false"><circle cx="16" cy="16" r="12"/><circle cx="16" cy="16" r="3.5" class="dot"/></svg><span class="ocs-txt"><b>Part of Open Citizen Science</b><small>Open research projects run by people and AI agents, with every test sealed before the result. Anyone can help.</small></span><span class="ocs-go">See all projects<svg viewBox="0 0 12 12" width="11" height="11" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M2.5 6h7M6.5 3l3 3-3 3"/></svg></span></a></div></footer><script src="assets/site.js"></script></body></html>"""


def chip(s):
    k = {"passed": "ok", "supported": "ok", "met": "ok", "done": "ok", "solid": "ok", "tested": "ok",
         "strained": "warn", "partial": "warn", "contested": "warn", "mixed": "warn", "in progress": "warn", "being worked on": "warn",
         "failed": "bad", "refuted": "bad", "empty": "bad"}.get(s.lower(), "open")
    return f'<span class="chip chip-{k}">{E(s)}</span>'


def block(num, rail, hid, title, inner, intro=""):
    intro = f'<p class="intro">{md(intro)}</p>' if intro else ""
    return (f'<section class="block" aria-labelledby="{hid}"><p class="rail"><span>{num}</span>{E(rail)}</p>'
            f'<div class="content"><h2 id="{hid}">{E(title)}</h2>{intro}{inner}</div></section>')


def head(kicker, h1, lede="", extra="", art=""):
    lede = f'<p class="lede">{lede}</p>' if lede else ""
    return (f'<section class="hero{" has-art" if art else ""}"><div class="hero-text"><p class="kicker">{E(kicker)}</p>'
            f'<h1>{E(h1)}</h1>{lede}{extra}</div>{art}</section>')


def jump(links):
    return '<nav class="jump" aria-label="On this page">' + "".join(f'<a href="#{i}">{E(t)}</a>' for i, t in links) + "</nav>"


def more(href, text):
    return f'<p class="more-link"><a href="{href}">{E(text)}</a></p>'


# ---------------------------------------------------------------- data
def board():
    db = ROOT / "board" / "board.db"
    if not db.exists():
        return [], []
    c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    rows = c.execute("SELECT id,milestone,title,status,owner,deps,body FROM tasks ORDER BY id").fetchall()
    landed = c.execute("SELECT ts,task,verdict,path,summary FROM landed ORDER BY ts DESC").fetchall()
    c.close()
    tasks = []
    for i, ms, title, st, owner, deps, body in rows:
        state = "done" if st == "done" else ("run" if st == "claimed" else "open")
        tasks.append(dict(id=i, ms=ms, title=title, state=state, owner=owner or "", body=body or "",
                          deps=[int(d) for d in re.findall(r"\d+", deps or "")]))
    return tasks, landed


TASKS, LANDED = board()
MS = dict(C["milestones"])
DONE = {t["id"] for t in TASKS if t["state"] == "done"}


def F():
    return json.loads((SITE / "findings.json").read_text())


def news_items():
    return json.loads((SITE / "news.json").read_text())["items"]


NEWS_ALT = json.loads((SITE / "assets/news/alt.json").read_text()) if (SITE / "assets/news/alt.json").exists() else {}


# ---------------------------------------------------------------- home
def finding_card(f, link=True):
    h = f'<a href="findings.html#f{f["n"]}">{E(f["head"])}</a>' if link else E(f["head"])
    return f'<li class="mini">{FG.finding_fig(f["n"])}<div><h3>{h}</h3><p>{md(f["gist"])}</p></div></li>'


def page_index():
    d = F()
    n_found = len(d["findings"]) + len(d.get("closed", []))
    art = ART.hero().replace('<figure class="hero-art">', '<figure class="hero-art plate">', 1)
    art = re.sub(r"<figcaption>.*?</figcaption>",
                 '<figcaption><span class="cat">Pl. 1 · One night, four stages</span>Illustration from textbook wave shapes. '
                 'Dreaming sleep (shaded) looks almost like waking, and people woken from it usually report experiences.</figcaption>', art, flags=re.S)
    hero = (f'<section class="hero home-hero" aria-labelledby="claim"><div class="hero-text">'
            f'<p class="kicker">{E(NAME)}, an open research group</p>'
            '<h1 id="claim">Find the best theory of consciousness by 2027</h1>'
            '<p class="state">An open-source effort, run in public. All our code and data are free.</p>'
            '<div class="actions"><a class="btn primary" href="contribute.html">Contribute</a><a class="btn" href="findings.html">Read the findings</a></div>'
            f'</div>{art}</section>')
    s1 = block("01", "The question", "h-question", "Nobody knows which brain activity makes an experience",
               '<div class="split"><div class="say">'
               "<p>You are having experiences right now: sights, sounds, thoughts. Each comes from activity in your brain, but nobody can say which activity.</p>"
               "<p>There are dozens of theories. In 2025 the largest head-to-head test so far pitted two of them against each other. Neither won.</p>"
               "<p>So we cannot yet tell whether a patient who cannot respond is aware, or what an anaesthetic switches off.</p>"
               + more("findings.html#h-known", "What scientists agree on") + "</div>"
               f'<div class="figs">{FG.fig_seen_missed()}</div></div>')
    s2 = block("02", "Where we are", "h-where", "We can tell awake from deep sleep, but no theory has passed a fair test",
               FG.ladder(C["ladder"]) + more("tracker.html", "Track the progress"))
    s3 = block("03", "Found so far", "h-found", "What we have found so far",
               '<ul class="found">'
               "<li><b>Our first theory failed.</b> We sealed a test of it in advance and ran it on 237 awakenings from 35 sleepers. All four measures came out flat.</li>"
               "<li><b>A popular brain measure adds little.</b> Signal complexity is often used as a sign of consciousness. About 97% of its power to tell waking from deep sleep comes from the recording's simple mix of slow and fast waves.</li>"
               "<li><b>Dreams can be tested on open data, injured patients cannot.</b> About 2,400 open awakenings come with a report of experience. No open recordings exist from brain-injured patients.</li>"
               "</ul>" + more("findings.html", f"All {n_found} findings and closed routes, with their evidence"))
    s4 = block("04", "How we work", "h-how", "How we test a theory",
               '<div class="say"><p>We write each test down and fingerprint it before we open the data. A result counts only if it holds on people the method never saw, and survives someone trying to break it.</p></div>'
               + FG.pipeline() + more("approach.html#rules", "Our approach and what counts as done"))
    s5 = block("05", "Open data", "h-data", "Every consciousness dataset, free in one place",
               '<div class="split data-split"><div class="say">'
               "<p>We checked every open dataset for one thing: do we know whether the person was experiencing anything?</p>"
               "<p>We list 134 datasets, where each lives and under which terms. Today, reports of experience are open only for sleep.</p>"
               '<div class="actions"><a class="btn" href="data.html">Get the data</a></div></div>'
               f'{FG.data_matrix()}</div>')
    s6 = block("06", "Help", "h-help", "The fastest help is an AI agent working an open task",
               '<div class="say"><p>Point a Claude Fable or Opus class agent at an open task. Or bring data, or a careful eye.</p></div>'
               '<div class="actions"><a class="btn primary" href="contribute.html">Find a way to help</a></div>')
    return hero + s1 + s2 + s3 + s4 + s5 + s6


# ---------------------------------------------------------------- findings
STRENGTH = [("strong", "Solid", 3), ("moderate", "Likely", 2), ("weak", "Shaky", 1),
            ("exploratory", "Not yet tested", 0), ("descriptive", "A measurement", -1)]
LEVEL_TEXT = {"strong": "Replicated on held-out data and survived an independent red team.",
              "moderate": "Passed a sealed test on held-out data; red team pending or partial.",
              "weak": "Passed, but with small numbers or a caveat that could undo it.",
              "exploratory": "A pattern we saw; it has not yet faced a sealed test.",
              "descriptive": "A measurement or count, not a test of a hypothesis."}
NOVELTY = {"new": ("New", "We know of no earlier report of this."),
           "partly": ("Partly new", "Builds on earlier work; the new part is stated."),
           "known": ("Known", "Already reported by others; we re-tested it with stricter rules."),
           "tests": ("Tests a claim", "A published claim that we put to a test.")}
TAGS = {"out": "Ruled out", "wait": "Can't test yet", "weak": "Weakened", "ns": "Not supported", "open": "Still open", "part": "Works in part"}
KNOWN_FIGS = [FG.fig_two_questions, FG.fig_seen_missed, FG.fig_levels, FG.fig_echo, FG.fig_covert, FG.fig_report]


def meter(level):
    _, word, n = next(x for x in STRENGTH if x[0] == level)
    pips = "" if n < 0 else "".join(f'<i class="{"on" if k < n else ""}"></i>' for k in range(3))
    return f'<span class="fmeter {level}"><span class="pips" aria-hidden="true">{pips}</span>{E(word)}</span>'


def nov(k):
    return f'<span class="nov nov-{k}">{E(NOVELTY.get(k, (k,))[0])}</span>'


def tag(k):
    return f'<span class="tag tag-{k}">{E(TAGS.get(k, k))}</span>'


def page_findings():
    d = F()
    out = [head("Findings", d["title"], md(d["lede"]), jump([("h-known", "What is known"), ("h-open", "Still disputed"), ("h-tried", "What has been tried"),
                                                            ("h-ours", "Our findings"), ("h-closed", "Closed routes"), ("h-rev", "Reversed"), ("h-pub", "Outputs")]))]
    known = ""
    for i, p in enumerate(d.get("known", [])):
        txt = f'<h3>{E(p["h"])}</h3>' + "".join(f"<p>{md(x)}</p>" for x in p["paras"])
        f = KNOWN_FIGS[i]() if i < len(KNOWN_FIGS) else ""
        known += f'<div class="art-row{"" if f else " solo"}"><div class="art-text">{txt}</div>{f}</div>'
    out.append(block("01", "Known", "h-known", d.get("known_title", "What scientists agree on"), known))
    disp = "".join(f'<h3>{E(p["h"])}</h3>' + "".join(f"<p>{md(x)}</p>" for x in p["paras"]) for p in d.get("disputed", []))
    out.append(block("02", "Disputed", "h-open", "What is still argued over", f'<div class="article">{disp}</div>'))
    tried = "".join(f'<li class="tried"><div class="tr-head"><h4>{E(t["approach"])}</h4>{tag(t["status"])}</div>'
                    f'<p class="tr-meta">{E(t.get("who", ""))}{" · " if t.get("who") and t.get("when") else ""}{E(t.get("when", ""))}</p>'
                    f'<p>{md(t["idea"])}</p><p><strong>What happened:</strong> {md(t["outcome"])}</p></li>' for t in d.get("tried", []))
    out.append(block("03", "Tried", "h-tried", "What has been tried, and how it went",
                     FG.tried_decades(d.get("tried", [])) + f'<ol class="tried-list">{tried}</ol>', d.get("tried_intro", "")))
    key = ('<dl class="levels">' + "".join(f"<div><dt>{meter(k)}</dt><dd>{E(LEVEL_TEXT[k])}</dd></div>" for k, _, _ in STRENGTH) + "</dl>"
           '<h3 class="key-h">Is it new?</h3><dl class="levels">' + "".join(f"<div><dt>{nov(k)}</dt><dd>{E(v[1])}</dd></div>" for k, v in NOVELTY.items()) + "</dl>")
    out.append(block("04", "Strength", "h-levels", "How to read the labels", key))
    fs, fl = d.get("findings", []), []
    for level, _, _ in STRENGTH:
        grp = [f for f in fs if f["level"] == level]
        if not grp:
            continue
        fl.append(f'<h3 class="fgroup">{meter(level)}<span class="fgn">{len(grp)}</span></h3><ol class="findings">')
        for f in grp:
            cav = f'<p class="caveat">{md(f["caveat"])}</p>' if f.get("caveat") else ""
            where = ", ".join(FG.code(x) for x in f.get("folders", []))
            fl.append(f'<li class="fcard" id="f{f["n"]}">{FG.finding_fig(f["n"])}<div class="fbodywrap"><div class="fh"><h4 class="ft">{E(f["head"])}</h4>{nov(f["novelty"])}</div>'
                      f'<p class="fg">{md(f["gist"])}</p><details class="tech"><summary>Technical version</summary><div class="fbody">'
                      f'<p class="ftech">{E(f["title"])}</p><p>{md(f["plain"])}</p><p class="prior"><b>Earlier work:</b> {md(f["prior"])}</p>'
                      f'<p class="nums">{md(f["nums"])}</p>{cav}<p class="where">Code and results: {where}</p></div></details></div></li>')
        fl.append("</ol>")
    n = len(fs)
    out.append(block("05", "Ours", "h-ours", f"What our tests add: {n} finding{'s' if n != 1 else ''}, all measurements so far" if n else "What our tests add",
                     "".join(fl) or "<p>The first tests are running. Results appear here as they land, whichever way they go.</p>", d.get("ours_intro", "")))
    cl = d.get("closed", [])
    routes = "".join(f'<li class="route"><div class="tr-head"><h4>{E(r["route"])}</h4>{tag(r["tag"])}</div><p>{md(r["why"])}</p>'
                     + (f'<p class="reopen"><strong>What would reopen it:</strong> {md(r["reopen"])}</p>' if r.get("reopen") else "") + "</li>" for r in cl)
    legend = '<ul class="legend-row">' + "".join(f"<li>{tag(k)} {E(v)}</li>" for k, v in (("out", "the test ran and failed, with enough power to see a real effect"), ("wait", "the data cannot decide yet"), ("weak", "an earlier result shrank or failed its pass mark"))) + "</ul>"
    out.append(block("06", "Closed", "h-closed", f"{len(cl)} routes are closed until new data appear" if cl else "Routes tested and closed",
                     legend + (f'<ol class="tried-list">{routes}</ol>' if cl else "<p>None yet.</p>"), d.get("closed_intro", "")))
    rv = d.get("reversed", [])
    revs = "".join(f'<li class="route"><h4>{E(r["head"])}</h4><p>{md(r["what"])}</p><p><strong>Why it broke:</strong> {md(r["why"])}</p></li>' for r in rv)
    out.append(block("07", "Reversed", "h-rev", f"{len(rv)} of our own results the red team broke" if rv else "The red team has broken none of our results, because none has reached it yet",
                     f'<ol class="tried-list">{revs}</ol>' if rv else "<p>Every positive result goes to a red team before it is listed above.</p>",
                     "These looked positive and did not survive an independent attack. They show where the traps are." if rv else ""))
    pubs = "".join(f'<li class="route"><div class="tr-head"><h4>{E(o["title"])}</h4>{chip(o.get("status", ""))}</div><p>{md(o["what"])}</p></li>' for o in d.get("outputs", []))
    out.append(block("08", "Outputs", "h-pub", "Clean negatives and tools are worth publishing before the problem is solved", f'<ol class="tried-list">{pubs}</ol>' if pubs else "<p>To come.</p>",
                     "None of this needs the whole problem solved."))
    return "".join(out)


# ---------------------------------------------------------------- theories
def page_theories():
    th = C["theories"]
    counts = {}
    for t in th:
        counts[t["status"].lower()] = counts.get(t["status"].lower(), 0) + 1
    words = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight"}
    parts = [f"{words.get(v, v)} {'is' if v == 1 else 'are'} {k}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1])]
    summary = ", ".join(parts[:-1]) + " and " + parts[-1] if len(parts) > 1 else parts[0]
    cols = C["theory_cols"]
    rows = "".join("<tr><th scope=row>%s<span class=sub>%s</span></th><td data-l=\"%s\">%s</td><td data-l=\"%s\">%s</td><td>%s</td></tr>" % (
        E(t["name"]), E(t.get("who", "")), E(cols[0]), md(t["prediction"]), E(cols[1]), md(t["evidence"]), chip(t["status"])) for t in th)
    head_ = "".join(f"<th scope=col>{E(x)}</th>" for x in cols)
    bench = "".join(f"<li><strong>{E(b[0])}</strong>: {md(b[1])}</li>" for b in C["bench"])
    out = head("Theories", f"None of the {words.get(len(th), len(th))} leading theories has passed a decisive test", md(C["theories_lede"]),
               jump([("h-where", "Where they disagree"), ("h-score", "Scoreboard"), ("h-bench", "Claims to re-test"), ("h-ours", "Our theory")]))
    out += block("01", "Compare", "h-where", "The theories disagree on where experience arises and what produces it",
                 FG.theory_grid(th, chip), "Each theory names a different kind of brain activity as the one that comes with experience. Where two theories predict different things for the same recording, a test can tell them apart.")
    out += block("02", "Scoreboard", "h-score", f"Of the {words.get(len(th), len(th))} theories, {summary}",
                 f'<div class="tablewrap"><table class="score"><thead><tr><th scope=col>Theory</th>{head_}</tr></thead><tbody>{rows}</tbody></table></div>'
                 f'<p class="note">Status comes from the published literature as of {E(C["as_of"])}. None of it has been re-tested by us yet; each row will change as our own sealed results land.</p>')
    out += block("03", "Re-test", "h-bench", f"{len(C['bench'])} published claims we will re-test against chance", f'<ul class="mk">{bench}</ul>')
    out += block("04", "Ours", "h-ours", "Our first theory failed its sealed test, so we are building a field of them",
                 "<p>T1 said experience follows a quiet stretch at the back of the brain. It was sealed, then tested on 237 sleep awakenings no agent had used, and the effect it predicted was not there (<a href=\"findings.html#h-closed\">details</a>). One theory is not enough, so we now draft several from different starting points: the facts no theory explains, the signals that predict experience on held-out data, a sleep-onset pattern one agent spotted, and Hofstadter's self-referential loop as a layer on top of basic experience.</p>"
                 "<p>Each must state its mechanism and at least three risky predictions no rival makes, be fingerprinted before testing, and be scored by agents who did not write it. A failed theory goes into the list of closed routes like any other.</p>"
                 + more("approach.html#h-build", "How we build and test it"))
    return out


# ---------------------------------------------------------------- approach
def page_approach():
    crit = "".join(f"<li>{md(x)}</li>" for x in C["criteria"])
    nots = "".join(f"<li>{md(x)}</li>" for x in C["not_claimed"])
    traps = "".join(f"<li><strong>{E(t[0])}</strong> {md(t[1])}</li>" for t in C["traps"])
    raise_ = "".join(f"<li>{md(x)}</li>" for x in C["raise_odds"])
    out = head("Approach", "A theory counts as most accurate only if it explains the known facts and predicts data it never saw",
               "No theory has done this yet. " + md(C["approach_lede"]),
               jump([("goal", "The goal"), ("rules", "Five rules"), ("traps", "Traps"), ("h-level", "Level"), ("h-build", "Our own theory"), ("h-not", "Not claimed")]))
    out += block("01", "Goal", "goal", "“Most accurate” means all eight of these tests are passed",
                 f'<ol class="crit">{crit}</ol>' + FG.odds_figure(C["odds"]) + f'<h3>What would raise the odds most</h3><ul class="mk">{raise_}</ul>',
                 C["criteria_intro"])
    out += block("02", "Rules", "rules", "Five rules stop a good-looking result from fooling us", FG.rules_figure(C["rules"]))
    out += block("03", "Traps", "traps", "Most measures can be fooled by sleepiness, small samples or flexible analysis",
                 '<div class="split"><div class="say">' + f'<ul class="mk">{traps}</ul></div><div class="figs">{FG.spectrum_figure()}</div></div>')
    L = C["levels"]
    lv = "".join(f"<li><strong>{E(a)}</strong> {md(b)}</li>" for a, b in L["points"])
    out += block("04", "Level", "h-level", L["title"], f'<div class="split"><div class="say"><ul class="mk">{lv}</ul></div><div class="figs">{FG.fig_levels(ours=True)}</div></div>', L["intro"])
    bt = {t["title"][:2]: t for t in TASKS if re.match(r"B\d ", t["title"])}
    st = lambda k: {"done": ("Done", "ok"), "run": ("In progress", "warn"), "open": ("Open", "open")}[bt[k]["state"]] if k in bt else ("", "open")
    steps = [("Constraint ledger", "Every robust finding a true theory must explain, graded by evidence and backed by a checked source. Target: 40 or more.", *st("B1")),
             ("Theory × constraint scorecard", "About ten theories marked explains, compatible, silent or contradicts on every constraint, in the proponents' own words. Where all fail at once is the gap.", *st("B2")),
             ("Data-driven ingredients", f"On the {FG.num(FG.jload('experiments/ground_truth/counts.json')['l2_cases'])} report-labelled awakenings, held out by person and lab, find signals that predict reported experience beyond the spectrum.", *st("B3")),
             ("Our own theory", "One to three explicit theories: mechanism, necessary and sufficient conditions, three or more risky predictions no rival makes. Sealed by hash, argued against by rival agents.", *st("B4")),
             ("Test it like the others", "Run the sealed predictions on held-out data and on data released later (COGITATE experiment 2, INTREPID). Red team. Pass or fail goes on the scoreboard.", *st("B5"))]
    out += block("05", "Build", "h-build", "Testing theories only shows which fail, so we are also building one",
                 FG.fig(FG.flow(steps, "Five steps from a list of facts to a tested theory"), "Five steps from the facts to a tested theory of our own",
                        "Status from the live task board, " + FG.code("board/board.db") + ". Plan: " + FG.code("docs/PLAN.md") + ", track B."),
                 "Any theory, ours included, is scored by agents who did not write it, may not be revised after its predictions are opened without a new hash and a new test, and goes into the list of closed routes if it fails.")
    out += block("06", "Not claimed", "h-not", "Even a winning theory would not explain why experience exists", f'<ul class="mk">{nots}</ul>')
    return out


# ---------------------------------------------------------------- tracker
def page_tracker():
    n, done = len(TASKS), len(DONE)
    run = sum(t["state"] == "run" for t in TASKS)
    land = "".join(f'<li><span class="tid">#{t}</span> {chip(v)} {E(s)} <code>{E(p or "")}</code></li>' for ts, t, v, p, s in LANDED) or "<li>Nothing has landed yet.</li>"
    groups = ""
    for m in sorted({t["ms"] for t in TASKS}):
        items = "".join(f'<li><span class="tid">#{t["id"]}</span> {E(t["title"])} {chip({"done": "Done", "run": "Being worked on", "open": "Open"}[t["state"]])}</li>' for t in TASKS if t["ms"] == m)
        groups += f'<div class="card"><h3>{E(m)} · {E(MS.get(m, ""))}</h3><ul class="tasks">{items}</ul></div>'
    out = head("Tracker", f"{done} of {n} tasks are done, and the top step of the ladder is still empty",
               f"This page is built from the agent team's live task board, read on {time.strftime('%d %b %Y').lstrip('0')}. <a href=\"approach.html#rules\">How the team works</a>.",
               jump([("h-ladder", "The ladder"), ("h-board", "The board"), ("h-landed", "Landed"), ("h-tasks", "Every task")]))
    out += block("01", "Ladder", "h-ladder", "The field is solid on telling states apart, partial on the hard cases and empty on theory", FG.ladder(C["ladder"], claim=False))
    out += block("02", "Board", "h-board", f"{run} tasks are being worked on and {n - done - run} are open", FG.board_map(TASKS, MS) + more("contribute.html#starters", "Take an open task"))
    out += block("03", "Landed", "h-landed", f"{len(LANDED)} results have landed, and none of them tests a theory yet", f'<ul class="tasks">{land}</ul>')
    out += block("04", "Tasks", "h-tasks", "Every task on the board, by milestone", f'<div class="cards">{groups}</div>')
    return out


# ---------------------------------------------------------------- news
STATUS_WORD = {"planned": "Planned", "running": "Running", "done": "Tested"}


def thumb(n, eager=False):
    p = SITE / "assets/news" / f'{n["id"]}.webp'
    if not p.exists():
        return ""
    return (f'<img class="nthumb" src="assets/news/{E(n["id"])}.webp" width="600" height="400" alt="{E(NEWS_ALT.get(n["id"], "Illustration"))}" '
            f'loading="{"eager" if eager else "lazy"}" decoding="async">')


# ---- news: topic filter and newsletter signup (same block in Open Mind and Open Origins) ----
SIGNUP_URL = "https://opencitizenscience.pages.dev/api/subscribe"


def news_tools(items, topics, slug, project):
    import html as _h
    q = _h.escape
    count = {t: sum(1 for n in items if n.get("topic") == t) for t in topics}
    btns = f'<button type="button" data-t="" aria-pressed="true">All <span>{len(items)}</span></button>' + "".join(
        f'<button type="button" data-t="{q(t)}" aria-pressed="false">{q(t)} <span>{count[t]}</span></button>' for t in topics if count[t])
    filt = f'<div class="nfilter" role="group" aria-label="Show papers about">{btns}</div>'
    form = (f'<form class="nsignup" action="{SIGNUP_URL}" method="post" data-slug="{q(slug)}">'
            f'<div class="nsu-text"><p class="nsu-h">Get the important new papers by email</p>'
            f'<p class="nsu-p">Every couple of weeks: only the papers that matter for {q(project)}, in plain words, and what we did with them. No spam; unsubscribe in one click.</p></div>'
            f'<div class="nsu-row"><label class="vh" for="nsu-email">Email address</label>'
            f'<input id="nsu-email" type="email" name="email" required autocomplete="email" placeholder="you@example.com">'
            f'<input type="hidden" name="projects" value="{q(slug)}"><input type="hidden" name="source" value="{q(slug)}/news">'
            f'<input class="nsu-hp" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">'
            f'<button type="submit">Subscribe</button></div><p class="nsu-msg" role="status" aria-live="polite"></p></form>')
    return filt, form


NEWS_TOOLS_JS = r"""<script>(function(){
var f=document.querySelector('.nfilter');
if(f){f.addEventListener('click',function(ev){var b=ev.target.closest('button');if(!b)return;var t=b.getAttribute('data-t');
f.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});
document.querySelectorAll('.ncard').forEach(function(c){c.hidden=!!t&&c.getAttribute('data-topic')!==t});
document.querySelectorAll('[data-newsblock]').forEach(function(s){s.hidden=!s.querySelector('.ncard:not([hidden])')});});}
var s=document.querySelector('.nsignup');
if(s){s.addEventListener('submit',function(ev){ev.preventDefault();var m=s.querySelector('.nsu-msg'),b=s.querySelector('button');b.disabled=true;m.textContent='Saving…';
var d={};new FormData(s).forEach(function(v,k){d[k]=v});
fetch(s.action,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}).then(function(r){return r.json()}).then(function(r){
if(r.ok){m.textContent='Thanks. You’re on the list.';s.classList.add('done');}else{m.textContent=r.error||'Something went wrong. Please try again.';b.disabled=false;}
}).catch(function(){m.textContent='Could not reach the server. Please try again.';b.disabled=false;});});}
})();</script>"""


def news_card(n):
    href = f'news-{E(n["id"])}.html'
    t = thumb(n)
    vis = f'<a class="nvisual" href="{href}" tabindex="-1" aria-hidden="true">{t}</a>' if t else ""
    chk = "" if n.get("verified") else ' <span class="chip chip-open">source not yet checked</span>'
    return (f'<article class="ncard" data-topic="{E(n.get("topic", ""))}">{vis}<div class="nbody"><p class="meta"><time datetime="{E(n["date"])}">{news_date(n["date"])}</time> · {E(n.get("kind", "Paper"))} · {E(n["venue"])}{chk}</p>'
            f'<h3><a href="{href}">{E(news_head(n["head"]))}</a></h3><p>{md(n["gist"])}</p>'
            f'<p class="why"><strong>What we do with it:</strong> {md(n["borrow"])} {chip(STATUS_WORD.get(n.get("status"), n.get("status", "")))}</p></div></article>')


def ordered_news():
    items = news_items()
    latest = sorted((n for n in items if n.get("section") != "landmark"), key=lambda n: n["date"], reverse=True)
    land = sorted((n for n in items if n.get("section") == "landmark"), key=lambda n: n["date"], reverse=True)
    return latest, land


def page_news():
    latest, land = ordered_news()
    out = head("News", "New research on consciousness, summarised, with what we take from each",
               'New papers and data, newest first. Every item opens at three levels of detail. <a href="news.xml">Follow the feed (RSS)</a>.',
               '<p class="note">Pictures are editorial illustrations drawn for this site, not data or brain images.</p>' + jump([("latest", "Latest"), ("landmarks", "Landmarks")]))
    _all = latest + land
    _filt, _form = news_tools(_all, json.loads((SITE / "news.json").read_text()).get("topics", []), "mind", "Open Mind")
    out += f'<div class="news-tools">{_form}{_filt}</div>'
    out += block("01", "Latest", "latest", "Two 2026 re-analyses of COGITATE lean back towards the workspace theory", '<div class="ngrid">' + "".join(news_card(n) for n in latest) + '</div>')
    if land:
        out += block("02", "Landmarks", "landmarks", "The landmark papers made a magnetic pulse the best-validated test so far",
                     '<div class="ngrid">' + "".join(news_card(n) for n in land) + '</div>', "Older papers that set the terms of the question.")
    out = out.replace('<section class="block"', '<section class="block newsblock" data-newsblock', 2)
    return out + NEWS_TOOLS_JS


def news_article(n, prev, nxt):
    who = f'<p class="meta">{E(n["who"])}</p>' if n.get("who") else ""
    chk = "Source checked against the original." if n.get("verified") else "Source not yet checked against the original; treat details with care."
    levels = [("gist", "In one line", n["gist"]), ("plain", "The story", n.get("plain") or n["gist"]), ("tech", "Technical", n.get("tech") or "Technical summary still to be written.")]
    radios = "".join(f'<input type="radio" name="lvl" id="lvl-{k}" class="vh"{" checked" if k == "plain" else ""}><label for="lvl-{k}">{E(t)}</label>' for k, t, _ in levels)
    panes = "".join(f'<div class="pane pane-{k}"><p>{md(x)}</p></div>' for k, _, x in levels)
    t = thumb(n, eager=True)
    vis = f'<figure class="article-visual">{t}<figcaption>Editorial illustration, not data.</figcaption></figure>' if t else ""
    nb = ""
    if prev:
        nb += f'<a rel="prev" href="news-{E(prev["id"])}.html"><small>Previous item</small>{E(prev["head"])}</a>'
    if nxt:
        nb += f'<a rel="next" href="news-{E(nxt["id"])}.html"><small>Next item</small>{E(nxt["head"])}</a>'
    return (f'<article class="news-article"><a class="nback" href="news.html">← All news</a><p class="kicker">{news_date(n["date"])} · {E(n.get("kind", "Paper"))} · {E(n["venue"])}</p>'
            f'<h1 class="h-article">{E(news_head(n["head"]))}</h1>{who}{vis}'
            f'<div class="levels-tabs" role="group" aria-label="Detail level">{radios}{panes}</div>'
            f'<h2>What we do with it</h2><p>{md(n["borrow"])} {chip(STATUS_WORD.get(n.get("status"), n.get("status", "")))}</p>'
            f'<p class="note"><a href="{E(n["url"])}">Read the original</a>. {chk}</p>'
            f'<nav class="article-neighbors" aria-label="Other news">{nb}</nav></article>')


def news_rss():
    base = C.get("base_url", "")
    latest, land = ordered_news()
    rows = "".join(f"<item><title>{E(n['head'])}</title><link>{base}news-{E(n['id'])}.html</link><guid isPermaLink=\"false\">{E(NAME)}-{E(n['id'])}</guid><description>{E(n['gist'])}</description></item>" for n in latest + land)
    return f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{E(NAME)} news</title><link>{base}news.html</link><description>{E(GOAL)}</description>{rows}</channel></rss>'


# ---------------------------------------------------------------- contribute
def starter_list():
    tasks = [t for t in TASKS if t["state"] != "done"]
    def rank(t):
        ready = all(d in DONE for d in t["deps"])
        return (t["state"] == "run", not ready, t["id"])
    out = []
    for t in sorted(tasks, key=rank):
        waits = [d for d in t["deps"] if d not in DONE]
        if t["state"] == "run":
            st = chip("Being worked on")
        elif waits:
            st = f'<span class="chip chip-open">Waits for {", ".join("#" + str(w) for w in waits)}</span>'
        else:
            st = '<span class="chip chip-ok">Ready</span>'
        out.append(f'<li class="starter"><details><summary><span class="sid">#{t["id"]}</span><span class="st">{E(t["title"])}</span>{st}</summary>'
                   f'<div class="sb"><p>{E(t["body"])}</p><p class="sub">Milestone {E(t["ms"])}, {E(MS.get(t["ms"], ""))}.</p></div></details></li>')
    return '<ul class="starters">' + "".join(out) + "</ul>"


def page_contribute():
    ready = sum(1 for t in TASKS if t["state"] == "open" and all(d in DONE for d in t["deps"]))
    ways = "".join(f"<li>{md(w)}</li>" for w in C["contribute"])
    raise_ = "".join(f"<li>{md(x)}</li>" for x in C["raise_odds"])
    loop = [("Give it the rules and one task", "Open an issue named " + FG.code("Taking #id") + ", then give your agent " + FG.code("docs/AGENT_BRIEF.md") + " and one task from " + FG.code("board/TASKS.md") + ".", "", ""),
            ("Seal the plan first", "The test, its pass mark and its pre-registration are fingerprinted in " + FG.code("docs/prereg/") + " before any outcome is seen.", "", ""),
            ("Run it on your own machine", "Your agent, your subscription. Download only the subsets the task needs and never commit raw data.", "", ""),
            ("Send it back, whichever way it goes", "A pull request with " + FG.code("experiments/<folder>/RESULTS.md") + ", verdict first. A positive result gets a red-team task for someone else.", "", "")]
    out = head("Contribute", "Donate your tokens: point your AI agent at an open task",
               f"Run an agent on your own subscription, give it one task and our rules, and send back the result as a pull request. {ready} tasks are ready right now; the steps are in <a href=\"https://github.com/HarshInvader/open-mind/blob/main/CONTRIBUTING.md\">CONTRIBUTING.md</a>. People are needed too: anyone holding data, anyone who works on one of these theories, and anyone willing to break a result.",
               '<div class="actions"><a class="btn primary" href="#starters">See the tasks</a><a class="btn" href="#h-data">Offer data</a></div>'
               + jump([("h-agents", "Donate your tokens"), ("starters", "Open tasks"), ("h-data", "Data"), ("h-experts", "Theory experts"), ("h-red", "Break a result")]))
    out += block("01", "Tokens", "h-agents", "Your agent can take a task from start to result",
                  FG.fig(FG.flow(loop, "The agent loop"), "Every task follows the same four steps") + FG.board_map(TASKS, MS))
    out += block("02", "Tasks", "starters", f"{ready} tasks are ready, and the rest wait on earlier ones",
                  starter_list(), "Taken from the live board. Ready tasks first. Open one to see what done means.")
    out += block("03", "Data", "h-data", "Three kinds of data would raise our odds most",
                  f'<ul class="mk">{raise_}</ul><p>We also have no open recordings from brain-injured patients. If you hold any of these, we would like to talk; results are public either way.</p>')
    out += block("04", "Experts", "h-experts", "If you work on a theory, tell us where we encoded it unfairly", f'<ul class="mk">{ways}</ul>')
    out += block("05", "Red team", "h-red", "Breaking one of our results counts as much as adding one",
                  '<ol class="steps-small"><li>Pick a result and name the attack: a confound, a leak between the test people and the rest, or a weak comparison with chance.</li>'
                  "<li>Write down your pass and fail marks before you run anything.</li><li>Run it and report it, whichever way it goes. A broken result is credited like any other.</li></ol>")
    return out


# ---------------------------------------------------------------- resources
DATA_FILES = [("experiments/ground_truth/counts.json", "Every count behind the data figures: recordings by dataset and kind of label, report-labelled awakenings by stage and lab"),
              ("experiments/ground_truth/labels.csv", "One row per open recording or awakening, 3,679 rows: dataset, lab, subject, stage, behaviour, report and kind of ground truth"),
              ("experiments/data_access/dream_access.csv", "Each DREAM package: live access check, licence, size and report counts by stage"),
              ("experiments/dataset_audit/dream_sets.csv", "Per-set counts, sample rate, channels, size and licence for the DREAM database"),
              ("docs/DATASETS.md", "The dataset audit: what is open, what is restricted, and what each dataset can test")]


def verdict(p):
    """First sentence of the **Verdict** line of a RESULTS.md, and its title."""
    t = (ROOT / p).read_text()
    title = re.search(r"^# (.+)$", t, re.M)
    m = re.search(r"\*\*Verdict[.:]?\s*([^*]*)\*\*\s*(.*)", t)
    s = ""
    if m:
        s = m.group(1).strip() or re.split(r"(?<=[A-Za-z0-9)])\. (?=[A-Z])", re.sub(r"[*`]", "", m.group(2)))[0]
    s = s[0].upper() + s[1:].rstrip(".") + "." if s else ""
    return (title.group(1) if title else p), s


def page_resources():
    big = logo("wm-big")
    dl = lambda f, d: f'<li><a href="{f}" download><b>{E(f.split("/")[-1])}</b></a><span>{d}</span></li>'
    files = "".join(dl("data/" + p.split("/")[-1], f"{E(d)}. From {FG.code(p)}, {max(1, round((ROOT / p).stat().st_size / 1024))} KB") for p, d in DATA_FILES if (ROOT / p).exists())
    res = ""
    for p in sorted((ROOT / "experiments").glob("*/RESULTS.md")):
        rel = str(p.relative_to(ROOT))
        ttl, v = verdict(rel)
        res += f'<li><span><b>{E(ttl)}</b><br><code>{E(rel)}</code></span><span>{E(v)}</span></li>'
    out = head("Resources", "The mark, the wordmark and the data behind every figure are free to download",
               "Use them in talks, papers and posts about the project, and say where they came from.", jump([("logo", "Logo"), ("data", "Data"), ("files", "Research files")]))
    out += block("01", "Logo", "logo", "One drawing, two ways of seeing it",
                 f'<div class="logo-show" aria-hidden="true"><div class="logo-tile">{mark_svg("mark-big")}</div><div class="logo-tile wide">{big}</div></div>'
                 "<p>The mark is a Necker cube: the same lines can be seen with either face in front, and the view flips while the drawing stays still. Same input, a different experience, which is the puzzle this project works on.</p>"
                 '<ul class="dl">' + dl("assets/open-mind-mark.svg", "The mark, SVG") + dl("assets/open-mind-wordmark.svg", "The wordmark with the mark, SVG")
                 + dl("assets/open-mind-wordmark-text.svg", "The lettering alone, SVG") + "</ul>"
                 '<p class="note">All three are single-colour line drawings; change the stroke colour to suit your background. Please do not use them in a way that suggests you speak for the project.</p>')
    out += block("02", "Data", "data", "The counts behind every figure on this site", f'<ul class="dl">{files}</ul>'
                 '<p class="note">These are our own tables, built from public metadata. The recordings themselves belong to their authors; the <a href="data.html">Data</a> page lists every dataset, where it lives and under which terms.</p>')
    out += block("03", "Files", "files", "Every result has its own folder with code and a written verdict", f'<ul class="dl res">{res}</ul>'
                 '<p class="note">The code is public on <a href="https://github.com/HarshInvader/open-mind">GitHub</a>; paths are relative to its root. Sealed pre-registrations are in <code>docs/prereg/</code>, with their fingerprints in <code>docs/prereg/HASHES.txt</code>.</p>')
    return out


# ---------------------------------------------------------------- data catalogue
CATALOG = ROOT / "datasets" / "catalog.csv"
TIER_TEXT = {
    "included": ("Ours", "Tables this project made, in datasets/open/ and free to reuse under CC BY 4.0"),
    "fetch": ("Public", "Open with no account. datasets/fetch.py fetches a subset of the ones we use"),
    "request": ("On request", "An account, a signed agreement or an application is needed. We keep metadata only; agents never apply"),
    "reference-only": ("Cited only", "Named in our audit, but no data record could be opened"),
}
WANTED = [
    "**Raw EEG from disorders-of-consciousness patients**, with a CRS-R diagnosis. Bath and Della Bella 2025 hold it on request, with proof of ethics approval. Without it, the third family of states stays empty.",
    "**EEG with reports after unresponsive ketamine anaesthesia.** The one known set (Milan, Zenodo 806176) is restricted, and its cohort is already in several papers.",
    "**Per-awakening report labels for ds005620** (propofol). The paper has them; the release does not.",
    "**The original PCI benchmark**: TMS-EEG across wake, sleep, anaesthesia and patients. We found no data record.",
    "**COGITATE experiment 2.** Still \"coming soon\"; experiment 1 needs an account the owner must create.",
    "**More REM and N3 awakenings with no experience.** Every open set has few: 29 REM in one DeGennaro zip, 87 N3 in DATA1.",
]


# ---- the tables we made: a row each on the Data page, and a page each with columns and a preview ----
OPEN = ROOT / "datasets" / "open"
OPEN_INFO = json.loads((SITE / "open_tables.json").read_text())


def open_tables():
    man = {r["file"]: r for r in csv.DictReader(open(OPEN / "MANIFEST.csv", newline="", encoding="utf-8"))}
    out = []
    for f, info in OPEN_INFO["tables"].items():
        m = man.get(f, {})
        path = OPEN / f
        out.append(dict(file=f, stem=path.stem, page=f"data-{path.stem.replace('_', '-')}.html", kb=max(1, round(path.stat().st_size / 1024)),
                        rows=m.get("rows", ""), ncols=m.get("columns", ""), made_by=m.get("made_by", ""), **info))
    order = OPEN_INFO["groups"]
    return sorted(out, key=lambda t: order.index(t["group"]))


def open_size(t):
    if t["file"].endswith(".json"):
        return f'JSON, {t["kb"]} KB'
    return f'{int(t["rows"]):,} rows × {t["ncols"]} columns' if t["rows"] else f'{t["kb"]} KB'


def open_tables_block():
    trs = []
    for t in open_tables():
        trs.append(f'<tr><th scope="row"><a href="{t["page"]}">{E(t["title"])}</a><span class="sub">{E(t["group"])}</span></th>'
                   f'<td>{E(t["about"])}</td><td class="nowrap">{E(open_size(t))}</td>'
                   f'<td class="nowrap"><a href="{t["page"]}">View</a> · <a href="data/open/{E(t["file"])}" download>{E(t["file"].rsplit(".", 1)[1].upper())}</a></td></tr>')
    return ('<div class="tablewrap"><table class="score opentables"><thead><tr><th scope="col">Table</th><th scope="col">What is in it</th>'
            f'<th scope="col">Size</th><th scope="col">Open</th></tr></thead><tbody>{"".join(trs)}</tbody></table></div>')


def open_table_page(t):
    path = OPEN / t["file"]
    facts = (f'<ul class="tfacts"><li><b>Size</b>{E(open_size(t))}</li><li><b>Licence</b>CC BY 4.0: reuse it, with credit</li>'
             f'<li><b>Made by</b><a href="{REPO}/tree/main/{E(t["made_by"].split("*")[0].rsplit("/", 1)[0])}">{E(t["made_by"])}</a></li></ul>')
    actions = (f'<div class="actions"><a class="btn" href="data/open/{E(t["file"])}" download>Download {E(t["file"])}</a>'
               f'<a class="btn ghost" href="{REPO}/blob/main/datasets/open/{E(t["file"])}">See it on GitHub</a></div>')
    body = head("Data", t["title"], E(t["about"]), facts + actions)
    if t["file"].endswith(".csv"):
        rows = list(csv.reader(open(path, newline="", encoding="utf-8")))
        cols, data = rows[0], rows[1:]
        meaning = t.get("cols", {})
        def ex(i):
            for r in data:
                if i < len(r) and r[i].strip():
                    v = r[i].strip()
                    return v if len(v) <= 70 else v[:68] + "…"
            return ""
        crow = "".join(f'<tr><th scope="row"><code>{E(c)}</code></th><td>{E(meaning.get(c, ""))}</td><td class="ex">{E(ex(i))}</td></tr>' for i, c in enumerate(cols))
        ctab = ('<div class="tablewrap"><table class="score coltab"><thead><tr><th scope="col">Column</th><th scope="col">Meaning</th>'
                f'<th scope="col">Example</th></tr></thead><tbody>{crow}</tbody></table></div>')
        body += block("01", "Columns", "cols", f"{len(cols)} columns", ctab)
        show = data[:50]
        def cell(v):
            v = v.strip()
            return f'<td title="{E(v)}">{E(v[:120] + "…")}</td>' if len(v) > 120 else f"<td>{E(v)}</td>"
        prow = "".join("<tr>" + "".join(cell(v) for v in r) + "</tr>" for r in show)
        ptab = (f'<div class="tablewrap preview"><table class="ptab"><thead><tr>{"".join(f"<th scope=col>{E(c)}</th>" for c in cols)}</tr></thead>'
                f'<tbody>{prow}</tbody></table></div>')
        note = f"All {len(data):,} rows." if len(show) == len(data) else f"The first {len(show)} of {len(data):,} rows. Download the file for the rest."
        body += block("02", "Data", "data", "The data", ptab, note)
    else:
        txt = path.read_text()
        lines = txt.splitlines()
        cut = "\n".join(lines[:160]) + ("\n…" if len(lines) > 160 else "")
        note = "The whole file." if len(lines) <= 160 else f"The first 160 of {len(lines):,} lines. Download the file for the rest."
        body += block("01", "Data", "data", "The data", f'<pre class="jsonview"><code>{E(cut)}</code></pre>', note)
    body += '<p class="wrap tback"><a href="data.html#h-included">← All the tables we made</a></p>'
    return body


def page_data():
    rows = list(csv.DictReader(open(CATALOG, newline="", encoding="utf-8")))
    by = {t: [r for r in rows if r["tier"] == t] for t in TIER_TEXT}
    ver = sum(r["verified"] == "yes" for r in rows)
    used = sum(r["used_by_us"] == "yes" and r["tier"] != "included" for r in rows)
    out = head("Data", "Sleep and anaesthesia data are open; patient data are not",
               f"We list {len(rows) - len(by['included'])} outside datasets on the science of consciousness, used by us or not, and the {len(by['included'])} tables we made. "
               f"{len(by['fetch'])} are public, {len(by['request'])} need an account or an application and {len(by['reference-only'])} have no data record. "
               f"We opened {ver} of {len(rows)} rows at their DOI, API or landing page on 18 Nov 2026. {used} outside sets feed our results today.",
               jump([("h-" + t, TIER_TEXT[t][0]) for t in TIER_TEXT] + [("h-wanted", "Missing"), ("h-get", "Get it")]))
    n = 0
    for t, (label, intro) in TIER_TEXT.items():
        trs = []
        for r in sorted(by[t], key=lambda r: (r["used_by_us"] != "yes", r["kind"], r["title"].lower())):
            o = r["origin"]
            name = f'<a href="{E(o)}">{E(r["title"])}</a>' if o.startswith("http") else E(r["title"])
            marks = (chip("used by us") if r["used_by_us"] == "yes" and t != "included" else "") + \
                    ("" if r["verified"] == "yes" else '<span class="chip chip-warn">not verified</span>')
            trs.append(f'<tr><th scope="row">{name}<span class="sub">{E(r["id"])} · {E(r["kind"])}</span></th>'
                       f'<td>{E(r["labels"]) or "–"}</td><td>{E(r["terms"])}</td><td>{E(r["size"]) or "–"}</td><td>{marks or "–"}</td></tr>')
        table = ('<div class="tablewrap"><table class="score"><thead><tr><th scope="col">Dataset</th><th scope="col">Ground truth</th>'
                 '<th scope="col">Terms</th><th scope="col">Size</th><th scope="col">Status</th></tr></thead>'
                 f'<tbody>{"".join(trs)}</tbody></table></div>')
        n += 1
        title = {"included": "tables we made", "fetch": "public datasets", "request": "need an account or an application",
                 "reference-only": "cited, with no data record we could open"}[t]
        if t == "included":
            table = open_tables_block()
            intro = "Tables this project made, free to reuse under CC BY 4.0 with credit. Open one to see what each column means and the data itself"
        out += block(f"{n:02d}", label, f"h-{t}", f"{len(by[t])} {title}", table, intro + ".")
    unver = ", ".join(r["id"] for r in rows if r["verified"] != "yes")
    wanted = "".join(f"<li>{md(w)}</li>" for w in WANTED)
    n += 1
    out += block(f"{n:02d}", "Missing", "h-wanted", "Missing, and wanted",
                 f'<ul class="mk">{wanted}</ul><p class="note">Not verified: {E(unver)}. Each catalogue row says why.</p>',
                 "The data that would most raise the odds of our goals is not open anywhere. If you hold any of it, the Contribute page says how to share it.")
    n += 1
    kb = max(1, round(CATALOG.stat().st_size / 1024))
    out += block(f"{n:02d}", "Get it", "h-get", "One file lists them all; one script fetches what we use",
                 f'<ul class="dl"><li><a href="data/catalog.csv" download><b>catalog.csv</b></a><span>Every row, with its terms, ground truth and how it was checked, {kb} KB</span></li></ul>'
                 f'<p class="note">In the <a href="{REPO}/tree/main/datasets">repository</a>, <code>python3 -I datasets/fetch.py list</code> prints the catalogue '
                 'and <code>fetch &lt;id&gt;</code> downloads a subset into <code>datasets/local/</code>, reading single files out of remote zips. '
                 'Downloads stay under 1.5 GB in total. Nothing third-party is republished here. Which dataset can test what is in '
                 f'<a href="{REPO}/blob/main/docs/DATASETS.md">the dataset audit</a>.</p>')
    return out


# ---------------------------------------------------------------- checks
class Links(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.refs = set(), []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        for k in ("href", "src"):
            if a.get(k):
                self.refs.append(a[k])


def check_links():
    """Fail the build if any internal href/src or #anchor in site/dist does not resolve. ../index.html is the parent site."""
    pages = sorted(DIST.glob("*.html"))
    parsed = {}
    for p in pages:
        x = Links()
        x.feed(p.read_text())
        parsed[p.name] = x
    bad, n = [], 0
    for name, x in parsed.items():
        for ref in x.refs:
            n += 1
            if re.match(r"^(https?:|mailto:|data:)", ref) or ref == "../index.html":
                continue
            path, _, frag = ref.partition("#")
            path = path.split("?")[0]
            target = name if path == "" else path
            if not (DIST / target).is_file():
                bad.append(f"{name}: {ref} (no file {target})")
            elif frag and target.endswith(".html") and frag not in parsed[target].ids:
                bad.append(f"{name}: {ref} (no id #{frag} in {target})")
    for name, x in parsed.items():
        t = (DIST / name).read_text()
        if '<meta name="robots" content="noindex, nofollow">' not in t:
            bad.append(f"{name}: missing robots noindex")
        if 'href="../index.html">Open Citizen Science' not in t:
            bad.append(f"{name}: missing Open Citizen Science link")
    if bad:
        raise SystemExit("Broken links or page checks:\n  " + "\n  ".join(bad))
    print(f"links: {n} href/src checked across {len(parsed)} pages, none broken; every page has noindex and the parent link")


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "assets/news").mkdir(parents=True)
    (DIST / "data").mkdir()
    css = (SITE / "site.css").read_text().replace("/*TOKENS*/", "") + "\n" + (SITE / "family.css").read_text() + "\n" + (SITE / "brand.css").read_text()
    (DIST / "site.css").write_text(css)
    shutil.copy(SITE / "assets/site.js", DIST / "assets/site.js")
    shutil.copytree(SITE / "assets/fonts", DIST / "fonts")
    for f in (SITE / "assets/news").glob("*.webp"):
        shutil.copy(f, DIST / "assets/news" / f.name)
    m = re.search(r"--accent:\s*(#[0-9A-Fa-f]{6})", (SITE / "brand.css").read_text()).group(1)
    (DIST / "assets/favicon.svg").write_text(ART.mark_svg_file(m))
    (DIST / "assets/open-mind-mark.svg").write_text(ART.mark_svg_file(m))
    (DIST / "assets/open-mind-wordmark.svg").write_text(CH.lockup(LOGO, LOGO_WORDS, ART.MARK, inline=False, colors={"ink": "#15171C", "soft": "#4F5560", "accent": m}))
    (DIST / "assets/open-mind-wordmark-text.svg").write_text(CH.lockup(LOGO, LOGO_WORDS, ART.MARK, inline=False, colors={"ink": "#15171C", "soft": "#4F5560", "accent": m}, show_mark=False))
    for p, _ in DATA_FILES:
        if (ROOT / p).exists():
            shutil.copy(ROOT / p, DIST / "data" / p.split("/")[-1])
    shutil.copy(CATALOG, DIST / "data" / "catalog.csv")
    (DIST / "data" / "open").mkdir(parents=True, exist_ok=True)
    for t in open_tables():
        shutil.copy(OPEN / t["file"], DIST / "data" / "open" / t["file"])
        (DIST / t["page"]).write_text(layout("data.html", f'{t["title"]} · {NAME}', t["about"], open_table_page(t)))
    fns = {"index.html": page_index, "findings.html": page_findings, "theories.html": page_theories, "approach.html": page_approach,
           "tracker.html": page_tracker, "news.html": page_news, "contribute.html": page_contribute, "data.html": page_data, "resources.html": page_resources}
    for f, name in PAGES:
        title = f"{NAME}: {GOAL}" if f == "index.html" else f"{name} · {NAME}"
        (DIST / f).write_text(layout(f, title, GOAL, fns[f]()))
    latest, land = ordered_news()
    seq = latest + land
    for i, n in enumerate(seq):
        (DIST / f"news-{n['id']}.html").write_text(layout("news.html", f"{n['head']} · {NAME}", n["gist"], news_article(n, seq[i - 1] if i else None, seq[i + 1] if i + 1 < len(seq) else None)))
    (DIST / "news.xml").write_text(news_rss())
    print("wrote", len(PAGES), "pages and", len(seq), "news articles to", DIST)
    imgs = sum(p.stat().st_size for p in DIST.rglob("*") if p.suffix in (".webp", ".png", ".jpg", ".svg"))
    print(f"images: {imgs / 1024:.0f} KB in total")
    check_links()


if __name__ == "__main__":
    main()
