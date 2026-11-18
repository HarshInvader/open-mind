#!/usr/bin/env python3
"""Build the Open Mind site.

Run from the repo root:  python3 -I site/build.py
Inputs: site/content.json, site/findings.json, site/news.json, board/board.db (read only), and the repo files the
figures cite (see site/figs.py). Brand: site/art.py and site/brand.css. News pictures: site/illustrate_news.py
(run it with .venv/bin/python when news.json gains an item; the build falls back to no picture if one is missing).
Writes site/dist/: static pages that work from file:// and on Cloudflare Pages. Fails if any internal link breaks.
"""
import html, html.parser, importlib.util, json, re, shutil, sqlite3, time
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


ART, FG = load("art"), load("figs")
NAME = C["name"]
GOAL = C["goal"]

PAGES = [("index.html", "Home"), ("findings.html", "Findings"), ("theories.html", "Theories"), ("approach.html", "Approach"),
         ("tracker.html", "Tracker"), ("news.html", "News"), ("contribute.html", "Contribute"), ("resources.html", "Resources")]


def md(s):
    """Tiny inline markup: **bold**, `code`."""
    s = re.sub(r"&quot;(.+?)&quot;", "\u201c\\1\u201d", E(s))
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", s)


def mark_svg(cls="mark"):
    return f'<svg class="{cls}" viewBox="0 0 32 32" aria-hidden="true" focusable="false">{ART.MARK}</svg>'


def layout(fname, title, desc, body):
    nav = "".join(f'<li><a href="{f}"{" aria-current=page" if f == fname else ""}>{E(n)}</a></li>' for f, n in PAGES)
    foot = "".join(f'<a href="{f}">{E(n)}</a>' for f, n in PAGES)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="color-scheme" content="light dark">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<script>(function(){{var t=null;try{{t=new URLSearchParams(location.search).get('theme')||localStorage.getItem('om-theme')}}catch(e){{}}if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);document.documentElement.classList.add('js')}})();</script>
<link rel="stylesheet" href="site.css"></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="head"><div class="wrap head-in">
<a class="parent" href="../index.html">Open Citizen Science</a><span class="slash" aria-hidden="true">/</span>
<a class="brand" href="index.html">{mark_svg()}{E(NAME)}</a>
<button class="menu-btn" type="button" id="menu-btn" aria-expanded="false" aria-controls="site-nav">Menu</button>
<nav class="site-nav" id="site-nav" aria-label="Main"><ul>{nav}</ul></nav>
<button class="theme" type="button" id="theme" aria-label="Colour theme: automatic"><svg viewBox="0 0 20 20" width="16" height="16" aria-hidden="true"><circle cx="10" cy="10" r="7" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M10 3a7 7 0 0 1 0 14z" fill="currentColor"/></svg><span id="theme-label">Auto</span></button>
</div></header>
<main id="main" class="wrap" tabindex="-1">{body}</main>
<footer class="foot"><div class="wrap foot-in">
<div class="foot-brand">{mark_svg()}<div><b>{E(NAME)}</b><p>Goal: {E(GOAL[0].lower() + GOAL[1:])}.</p></div></div>
<nav class="foot-links" aria-label="Site map">{foot}</nav>
<p class="foot-note">{E(NAME)} is an open research project run by a human lead and a team of AI agents. Every result can be rerun from code.
None of it explains why experience exists at all. Part of <a href="../index.html">Open Citizen Science</a>. Built {time.strftime('%d %b %Y').lstrip('0')}.</p>
</div></footer><script src="assets/site.js"></script></body></html>"""


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
    fs = {f["n"]: f for f in d["findings"]}
    hero = head(C["kicker"], "Every theory of consciousness is still unproven, so we test them all and build a better one",
                f'Goal: {E(GOAL[0].lower() + GOAL[1:])}. {md(C["lede"])}',
                '<div class="actions"><a class="btn primary" href="contribute.html">Take a task</a><a class="btn" href="findings.html">Read the findings</a></div>',
                ART.hero())
    s1 = block("01", "The problem", "h-problem", "Nobody can yet say which brain activity makes an experience",
               '<div class="split"><div class="say">'
               "<p>Here “consciousness” means experience: there is something it is like to be you right now. Researchers ask two questions about it: whether someone is conscious at all, and what they are conscious of.</p>"
               "<p>The usual method flashes the same picture many times. Sometimes people see it and sometimes they miss it. Whatever differs in the brain between the two is a candidate for the activity behind experience.</p>"
               "<p>Many theories explain those differences, and they disagree about where in the brain experience happens. In 2025 the largest head-to-head test so far, COGITATE, pitted two of them against each other. Neither won.</p>"
               + more("findings.html#h-known", "What scientists agree on, and what they don't") + "</div>"
               f'<div class="figs">{FG.fig_seen_missed()}{FG.fig_two_questions()}</div></div>')
    s2 = block("02", "Where we are", "h-where", "The field can tell awake from deep sleep, but no theory has won a fair test",
               FG.ladder(C["ladder"]) + more("tracker.html", "Track our progress"),
               C["ladder_intro"] + " The best measure so far needs a magnetic pulse and special equipment, and the top step is empty.")
    picks = [fs[k] for k in (4, 2, 3) if k in fs]
    s3 = block("03", "Found so far", "h-found", "Open data can test dreaming, but not brain-injured patients or ketamine",
               '<ul class="minis">' + "".join(finding_card(f) for f in picks) + "</ul>" + more("findings.html#h-ours", f"All {len(d['findings'])} findings, with their evidence"),
               d["ours_intro"])
    s4 = block("04", "How we test", "h-how", "A result counts only if it was sealed first and survives an attempt to break it",
               FG.pipeline() + more("approach.html#rules", "The rules, and what counts as done"),
               "Anyone can find a pattern by trying analyses until one works. So each test is written down and fingerprinted before the data are opened, run on people the method never saw, and handed to someone else to break.")
    s5 = block("05", "Open data", "h-data", "Reports given on waking are open only for sleep",
               '<div class="split data-split"><div class="say">'
               f'<p>We checked every open dataset against one question: what tells us whether the person was experiencing anything? The best answer is what they said when woken. {FG.num(FG.jload("experiments/ground_truth/counts.json")["l2_cases"])} awakenings from sleep have such a report, all in the DREAM database.</p>'
               "<p>No open recordings from brain-injured patients exist, and none from people who were unresponsive on ketamine but reported dreams afterwards. These are the gaps that most limit what anyone can test.</p>"
               '<div class="actions"><a class="btn" href="resources.html#data">Download the counts</a></div></div>'
               f'{FG.data_matrix()}</div>')
    asks = "".join(f"<li>{md(x)}</li>" for x in C["raise_odds"])
    s6 = block("06", "Help", "h-help", "The fastest help is an AI agent taking an open task",
               '<div class="split"><div class="say"><p>Point a strong AI agent at a task on our board, with the rules and the brief. Or bring data: these would raise our odds most.</p>'
               f'<ul class="mk">{asks}</ul><div class="actions"><a class="btn primary" href="contribute.html">Find a task</a></div></div>'
               f'<div class="figs">{FG.board_map(TASKS, MS)}</div></div>')
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
KNOWN_FIGS = [FG.fig_two_questions, FG.fig_seen_missed, FG.fig_echo, FG.fig_covert, FG.fig_report]


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
    out += block("04", "Ours", "h-ours", "Our own theory joins the scoreboard only once it is written down and sealed",
                 "<p>Where every existing theory fails, we will draft our own. It must state its mechanism and at least three risky predictions no rival makes, be fingerprinted before testing, and be scored by agents who did not write it. A failed theory goes into the list of closed routes like any other.</p>"
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
               jump([("goal", "The goal"), ("rules", "Five rules"), ("traps", "Traps"), ("h-build", "Our own theory"), ("h-not", "Not claimed")]))
    out += block("01", "Goal", "goal", "“Most accurate” means all eight of these tests are passed",
                 f'<ol class="crit">{crit}</ol>' + FG.odds_figure(C["odds"]) + f'<h3>What would raise the odds most</h3><ul class="mk">{raise_}</ul>',
                 C["criteria_intro"])
    out += block("02", "Rules", "rules", "Five rules stop a good-looking result from fooling us", FG.rules_figure(C["rules"]))
    out += block("03", "Traps", "traps", "Most measures can be fooled by sleepiness, small samples or flexible analysis",
                 '<div class="split"><div class="say">' + f'<ul class="mk">{traps}</ul></div><div class="figs">{FG.spectrum_figure()}</div></div>')
    bt = {t["title"][:2]: t for t in TASKS if re.match(r"B\d ", t["title"])}
    st = lambda k: {"done": ("Done", "ok"), "run": ("In progress", "warn"), "open": ("Open", "open")}[bt[k]["state"]] if k in bt else ("", "open")
    steps = [("Constraint ledger", "Every robust finding a true theory must explain, graded by evidence and backed by a checked source. Target: 40 or more.", *st("B1")),
             ("Theory × constraint scorecard", "About ten theories marked explains, compatible, silent or contradicts on every constraint, in the proponents' own words. Where all fail at once is the gap.", *st("B2")),
             ("Data-driven ingredients", f"On the {FG.num(FG.jload('experiments/ground_truth/counts.json')['l2_cases'])} report-labelled awakenings, held out by person and lab, find signals that predict reported experience beyond the spectrum.", *st("B3")),
             ("Our own theory", "One to three explicit theories: mechanism, necessary and sufficient conditions, three or more risky predictions no rival makes. Sealed by hash, argued against by rival agents.", *st("B4")),
             ("Test it like the others", "Run the sealed predictions on held-out data and on data released later (COGITATE experiment 2, INTREPID). Red team. Pass or fail goes on the scoreboard.", *st("B5"))]
    out += block("04", "Build", "h-build", "Testing theories only shows which fail, so we are also building one",
                 FG.fig(FG.flow(steps, "Five steps from a list of facts to a tested theory"), "Five steps from the facts to a tested theory of our own",
                        "Status from the live task board, " + FG.code("board/board.db") + ". Plan: " + FG.code("docs/PLAN.md") + ", track B."),
                 "Any theory, ours included, is scored by agents who did not write it, may not be revised after its predictions are opened without a new hash and a new test, and goes into the list of closed routes if it fails.")
    out += block("05", "Not claimed", "h-not", "Even a winning theory would not explain why experience exists", f'<ul class="mk">{nots}</ul>')
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


def news_card(n):
    href = f'news-{E(n["id"])}.html'
    t = thumb(n)
    vis = f'<a class="nvisual" href="{href}" tabindex="-1" aria-hidden="true">{t}</a>' if t else ""
    chk = "" if n.get("verified") else ' <span class="chip chip-open">source not yet checked</span>'
    return (f'<article class="ncard">{vis}<div class="nbody"><p class="meta"><time datetime="{E(n["date"])}">{news_date(n["date"])}</time> · {E(n.get("kind", "Paper"))} · {E(n["venue"])}{chk}</p>'
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
    out += block("01", "Latest", "latest", "Two 2026 re-analyses of COGITATE lean back towards the workspace theory", "".join(news_card(n) for n in latest))
    if land:
        out += block("02", "Landmarks", "landmarks", "The landmark papers made a magnetic pulse the best-validated test so far",
                     "".join(news_card(n) for n in land), "Older papers that set the terms of the question.")
    return out


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
    loop = [("Give it the rules and one task", "The brief at " + FG.code("docs/AGENT_BRIEF.md") + ", the board guide at " + FG.code("board/README.md") + ", and one task from the list below.", "", ""),
            ("Seal the plan first", "The test, its pass mark and its pre-registration are fingerprinted in " + FG.code("docs/prereg/") + " before any outcome is seen.", "", ""),
            ("Run it gently on one laptop", "Background priority, at most two worker processes, one compute job at a time, and subsets of the data under the shared download budget.", "", ""),
            ("Land it, whichever way it goes", "Results go in " + FG.code("experiments/<folder>/RESULTS.md") + ", verdict first. A positive result gets a red-team task for someone else.", "", "")]
    out = head("Contribute", "Point an AI agent at an open task and the work moves fastest",
               f"{ready} tasks are ready to take right now. The rules and the brief are written so an agent can claim a task, seal its plan, run it and land the result. People are needed too: anyone holding data, anyone who works on one of these theories, and anyone willing to break a result.",
               '<div class="actions"><a class="btn primary" href="#starters">See the tasks</a><a class="btn" href="#h-data">Offer data</a></div>'
               + jump([("h-agents", "Run an agent"), ("starters", "Open tasks"), ("h-data", "Data"), ("h-experts", "Theory experts"), ("h-red", "Break a result")]))
    out += block("01", "Agents", "h-agents", "An agent can take a task from claim to result on one laptop",
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
    inner, w, h = ART.wordmark()
    big = f'<svg class="wm-big" viewBox="-4 -4 {w + 8} {h + 8}" aria-hidden="true">{inner}</svg>'
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
                 '<p class="note">These are our own tables, built from public metadata. The recordings themselves belong to their authors; the dataset audit says where each one lives and under which licence.</p>')
    out += block("03", "Files", "files", "Every result has its own folder with code and a written verdict", f'<ul class="dl res">{res}</ul>'
                 '<p class="note">The code repository is not public yet. Paths are given relative to its root and will become links when it opens. Sealed pre-registrations are in <code>docs/prereg/</code>, with their fingerprints in <code>docs/prereg/HASHES.txt</code>.</p>')
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
    css = (SITE / "site.css").read_text().replace("/*TOKENS*/", "") + "\n" + (SITE / "brand.css").read_text()
    (DIST / "site.css").write_text(css)
    shutil.copy(SITE / "assets/site.js", DIST / "assets/site.js")
    for f in (SITE / "assets/news").glob("*.webp"):
        shutil.copy(f, DIST / "assets/news" / f.name)
    m = re.search(r"--accent:\s*(#[0-9A-Fa-f]{6})", (SITE / "brand.css").read_text()).group(1)
    (DIST / "assets/favicon.svg").write_text(ART.mark_svg_file(m))
    (DIST / "assets/open-mind-mark.svg").write_text(ART.mark_svg_file(m))
    (DIST / "assets/open-mind-wordmark.svg").write_text(ART.wordmark_svg(m))
    (DIST / "assets/open-mind-wordmark-text.svg").write_text(ART.wordmark_svg(m, with_mark=False))
    for p, _ in DATA_FILES:
        if (ROOT / p).exists():
            shutil.copy(ROOT / p, DIST / "data" / p.split("/")[-1])
    fns = {"index.html": page_index, "findings.html": page_findings, "theories.html": page_theories, "approach.html": page_approach,
           "tracker.html": page_tracker, "news.html": page_news, "contribute.html": page_contribute, "resources.html": page_resources}
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
