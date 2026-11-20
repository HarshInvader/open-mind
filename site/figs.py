"""Open Mind explanatory figures. Read by site/build.py (stdlib only).

Every figure makes one point. Figures that show numbers read them from the repo files named in each docstring,
so the drawing and the number come from the same source. Figures without data are labelled "Illustration".
All colours come from CSS classes (site.css, "Figures"), so every figure follows the light and dark themes.
"""
import csv, html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E = html.escape


def jload(p):
    return json.loads((ROOT / p).read_text())


def T(x, y, s, c="t", a="start"):
    return f'<text x="{x}" y="{y}" class="{c}" text-anchor="{a}">{E(str(s))}</text>'


def svg(vb, body, label, cls="fsvg"):
    return f'<svg class="{cls}" viewBox="{vb}" role="img" aria-label="{E(label)}">{body}</svg>'


def fig(body, claim="", src="", cls="fig"):
    c = f'<p class="claim">{E(claim)}</p>' if claim else ""
    s = f'<figcaption>{src}</figcaption>' if src else ""
    return f'<figure class="{cls}">{c}{body}{s}</figure>'


def code(p):
    return f"<code>{E(p)}</code>"


def num(n):
    return f"{n:,}"


# ---------------------------------------------------------------- small drawn parts
def viewer(x, y):
    """A person seen from the front: head and shoulders, centred on x, head centre at y."""
    return (f'<circle cx="{x}" cy="{y}" r="8" class="s-ink"/>'
            f'<path d="M{x-14} {y+22} Q{x} {y+6} {x+14} {y+22}" class="s-ink"/>')


BRAIN = ("M14 44 C10 27 24 12 45 10 C63 6 84 8 98 17 C110 25 114 39 108 51 C104 58 96 61 88 61 "
         "L86 69 C84 73 78 73 76 69 L74 63 C60 65 44 65 30 61 C20 58 16 52 14 44 Z")


def mini_brain(kind):
    """A schematic side view, front on the left. One drawing per theory: where it puts experience."""
    b = f'<path d="{BRAIN}" class="br"/>'
    lab = T(16, 84, "front", "t-xs") + T(108, 84, "back", "t-xs", "end")
    front, back, top, mid = (34, 30), (90, 34), (64, 20), (62, 44)
    dot = lambda p, r=5, c="f-acc": f'<circle cx="{p[0]}" cy="{p[1]}" r="{r}" class="{c}"/>'
    if kind == "iit":      # a dense, integrated posterior zone
        nodes = [(84, 26), (98, 32), (92, 46), (80, 40), (100, 44)]
        inner = f'<circle cx="90" cy="36" r="17" class="zone"/>' + "".join(
            f'<path d="M{a[0]} {a[1]}L{c[0]} {c[1]}" class="s-acc thin"/>' for i, a in enumerate(nodes) for c in nodes[i + 1:]) + "".join(dot(n, 2.6) for n in nodes)
    elif kind == "gnw":    # ignition: the front lights up and broadcasts to far areas
        far = [(64, 18), (92, 30), (86, 50), (52, 52)]
        inner = "".join(f'<path d="M34 30L{p[0]} {p[1]}" class="s-acc"/>' for p in far) + "".join(dot(p, 3, "f-acc") for p in far) + dot(front, 7)
    elif kind == "rpt":    # local feedback loop inside sensory cortex at the back
        inner = (dot(back, 3.2) + dot((76, 46), 3.2) + '<path d="M90 34 C98 46 88 54 78 48" class="s-acc arr"/>'
                 '<path d="M76 46 C70 36 80 28 88 32" class="s-acc arr"/>')
    elif kind == "hot":    # the front re-represents a state at the back
        inner = dot(back, 4, "f-soft") + dot(front, 6) + '<path d="M42 28 C56 18 72 20 84 30" class="s-acc arr"/>' + T(62, 16, "about", "t-xs", "middle")
    elif kind == "pp":     # predictions down, errors up
        inner = ('<path d="M40 24 C58 16 74 20 86 30" class="s-acc arr"/>' + '<path d="M86 44 C70 54 54 52 40 38" class="s-ink arr dash"/>'
                 + T(62, 14, "guess", "t-xs", "middle") + T(62, 62, "error", "t-xs", "middle"))
    elif kind == "ast":    # a simplified model of where attention is
        inner = ('<circle cx="88" cy="36" r="10" class="s-ink dash"/>' + dot((88, 36), 3)
                 + '<rect x="24" y="22" width="26" height="18" rx="3" class="f-soft s-acc"/>' + '<path d="M52 31 L76 34" class="s-acc arr"/>'
                 + T(37, 52, "model", "t-xs", "middle"))
    elif kind == "cx":     # the whole brain's signal: rich and varied when conscious
        pts = [(28, 40), (40, 24), (56, 18), (72, 16), (88, 22), (100, 36), (92, 50), (74, 54), (56, 54), (40, 50), (60, 36), (78, 36)]
        inner = "".join(f'<path d="M{a[0]} {a[1]}L{c[0]} {c[1]}" class="s-acc thin"/>' for i, a in enumerate(pts) for c in pts[i + 1:] if abs(a[0] - c[0]) + abs(a[1] - c[1]) < 34) + "".join(dot(p, 2.2) for p in pts)
    else:                  # our own theory: not written yet
        return f'<path d="{BRAIN}" class="br dash"/>' + T(61, 42, "?", "t-q", "middle") + lab
    return b + inner + lab


# ---------------------------------------------------------------- the problem (home, findings)
def fig_seen_missed():
    body = ('<rect x="10" y="58" width="60" height="52" rx="5" class="card"/>'
            '<circle cx="40" cy="84" r="13" class="s-ink"/><circle cx="35" cy="81" r="1.6" class="f-ink"/><circle cx="45" cy="81" r="1.6" class="f-ink"/>'
            '<path d="M35 89 Q40 93 45 89" class="s-ink"/>'
            + T(40, 128, "the same picture,", "t-s", "middle") + T(40, 141, "flashed briefly", "t-s", "middle")
            + '<path d="M74 84 C92 84 94 40 110 40" class="s-mute"/><path d="M74 84 C92 84 94 124 110 124" class="s-mute"/>'
            + viewer(124, 34) + T(146, 38, "Seen", "t-b acc") + T(146, 52, "says “yes”", "t-s")
            + viewer(124, 118) + T(146, 122, "Missed", "t-b") + T(146, 136, "says “no”", "t-s")
            + '<path d="M208 34 H214 V136 H208" class="s-mute"/><path d="M214 85 H232" class="s-acc arr"/>'
            + '<rect x="236" y="62" width="78" height="46" rx="6" class="f-soft s-acc"/>'
            + T(275, 81, "what differs", "t-s", "middle") + T(275, 96, "in the brain?", "t-s", "middle")
            + T(275, 126, "a candidate", "t-s", "middle") + T(275, 139, "correlate", "t-s", "middle"))
    return fig(svg("0 0 320 150", body, "Illustration: the same briefly flashed picture is sometimes seen and sometimes missed. "
                   "Whatever differs in the brain between the two cases is a candidate correlate of experience."),
               "Same input, different experience: the difference is the clue", "Illustration. The contrast behind most of the field since Crick and Koch, 1990. A difference is a clue, not an explanation: seen and missed trials can also differ in how strong the signal was.")


def fig_two_questions():
    body = (T(6, 20, "Level", "t-b") + T(48, 20, "is anyone there at all?", "t-s")
            + '<path d="M20 49.5 L300 44 L300 56 L20 50.5 Z" class="f-soft"/><path d="M20 50 H300" class="s-acc"/>'
            + '<circle cx="20" cy="50" r="5" class="card"/><circle cx="300" cy="50" r="5" class="f-acc"/>'
            + T(20, 72, "deep sleep", "t-s") + T(300, 72, "awake", "t-s", "end")
            + '<path d="M6 92 H314" class="s-line"/>'
            + T(6, 114, "Content", "t-b") + T(64, 114, "conscious of what?", "t-s")
            + '<circle cx="60" cy="144" r="14" class="s-ink"/><circle cx="55" cy="140" r="1.6" class="f-ink"/><circle cx="65" cy="140" r="1.6" class="f-ink"/><path d="M54 149 Q60 154 66 149" class="s-ink"/>'
            + '<path d="M146 138 h6 l9 -8 v28 l-9 -8 h-6 z" class="s-ink"/><path d="M167 137 q5 7 0 14" class="s-ink"/><path d="M172 132 q9 12 0 24" class="s-ink"/>'
            + '<path d="M262 130 A14 14 0 1 0 266 157 A11 11 0 1 1 262 130 Z" class="s-ink"/>'
            + T(60, 176, "a face", "t-s", "middle") + T(162, 176, "a sound", "t-s", "middle") + T(262, 176, "a dream", "t-s", "middle"))
    return fig(svg("0 0 320 182", body, "Illustration: two separate questions. Level asks whether someone is conscious at all, from deep sleep to awake. "
                   "Content asks what they are conscious of, such as a face, a sound or a dream."),
               "Two questions: whether you are conscious, and of what", "Illustration.")


def fig_echo():
    """Findings 01: Massimini 2005, as summarised in site/findings.json (known, third item)."""
    nodes = [(30, 52), (52, 30), (78, 26), (104, 34), (114, 58), (88, 74), (56, 72)]
    def panel(ox, spread):
        p = f'<g transform="translate({ox} 0)"><path d="M12 54 C8 26 40 10 74 12 C112 12 132 34 128 60 C124 82 92 92 62 88 C30 86 14 74 12 54 Z" class="br"/>'
        lit = range(len(nodes)) if spread else (0, 1)
        for k in lit:
            if k:
                p += f'<path d="M30 52 L{nodes[k][0]} {nodes[k][1]}" class="s-acc"/>'
        for k, (x, y) in enumerate(nodes):
            p += f'<circle cx="{x}" cy="{y}" r="{5 if k == 0 else 3.6}" class="{"f-acc" if k in lit else "card"}"/>'
        p += '<path d="M24 34 l6 8 l-5 1 l6 8" class="s-glow"/>'
        return p + "</g>"
    body = (panel(0, True) + panel(160, False)
            + T(70, 112, "Awake", "t-b", "middle") + T(70, 126, "the echo spreads", "t-s", "middle")
            + T(230, 112, "Deep sleep", "t-b", "middle") + T(230, 126, "it stays local", "t-s", "middle"))
    return fig(svg("0 0 300 132", body, "Illustration: a magnetic pulse at one spot. Awake, the brain's response spreads to many connected areas. "
                   "In deep sleep it stays near the spot and dies out."),
               "Awake, a tap on the brain echoes widely", "Illustration after Massimini and colleagues, 2005. The pulse is the zigzag.")


def fig_covert():
    """Findings 01: Bodien et al. 2024, numbers as given in site/findings.json (known, fourth item)."""
    n, k = 241, 60
    w = 300 * k / n
    body = (T(4, 16, f"{n} patients who showed no response to commands", "t-s")
            + f'<rect x="4" y="26" width="300" height="22" rx="4" class="card"/><rect x="4" y="26" width="{w:.1f}" height="22" rx="4" class="f-acc"/>'
            + T(4, 70, f"{k} of them ({round(100 * k / n)}%) did a mental task on fMRI or EEG", "t-s acc"))
    return fig(svg("0 0 310 80", body, f"Bar chart: of {n} patients with no response to commands, {k} performed a mental task on fMRI or EEG."),
               "One in four unresponsive patients was following instructions", "Data: Bodien and colleagues, 2024, 353 patients at six centres.")


def fig_report():
    trace = "M8 46 " + " ".join(f"C{x+6} {30 if i % 2 else 62} {x+12} {30 if i % 2 else 62} {x+18} 46" for i, x in enumerate(range(8, 170, 18)))
    body = (f'<path d="{trace}" class="s-ink"/>' + T(8, 92, "asleep, so no answer", "t-s") + T(8, 106, "from behaviour", "t-s")
            + '<path d="M184 14 V100" class="s-acc dash"/>' + T(184, 118, "woken", "t-s acc", "middle")
            + '<path d="M200 14 h126 a6 6 0 0 1 6 6 v18 a6 6 0 0 1 -6 6 h-114 l-8 8 v-8 h-4 a6 6 0 0 1 -6 -6 v-18 a6 6 0 0 1 6 -6 z" class="f-soft s-acc"/>'
            + T(265, 34, "“something was there”", "t-s", "middle")
            + '<path d="M200 64 h126 a6 6 0 0 1 6 6 v18 a6 6 0 0 1 -6 6 h-114 l-8 8 v-8 h-4 a6 6 0 0 1 -6 -6 v-18 a6 6 0 0 1 6 -6 z" class="card"/>'
            + T(265, 84, "“nothing”", "t-s", "middle"))
    return fig(svg("0 0 340 124", body, "Illustration: a sleeper cannot answer, so they are woken and asked whether anything was going through their mind. "
                   "The answer, experience or nothing, is the ground truth we use."),
               "The best evidence for sleep is a report given on waking", "Illustration.")


# ---------------------------------------------------------------- ladder
def ladder(levels, claim=True):
    kind = {"done": "done", "solid": "done", "partial": "part", "contested": "part"}
    rungs = "".join(f'<li class="rung r{i+1} {kind.get(s.lower(), "open")}"><b>{E(l)}</b><span class="nm">{E(n)}</span><span class="st">{E(s)}</span></li>'
                    for i, (l, n, d, s) in enumerate(levels))
    lab = "Five kinds of claim, weakest first. " + " ".join(f"{l} {n}: {s}." for l, n, d, s in levels)
    cap = '<p class="claim">The top step, one theory beating its rivals, is empty</p>' if claim else ""
    return (f'<figure class="ladder-fig">{cap}<ol class="ladder" aria-label="{E(lab)}">{rungs}</ol>'
            '<div class="key" aria-hidden="true"><span><i class="k done"></i>Done or solid</span><span><i class="k part"></i>Partial or contested</span><span><i class="k open"></i>Empty</span></div>'
            '<figcaption>Where the published field stands, from <a href="approach.html#goal">our own grading</a>. Each step needs the ones below it.</figcaption></figure>')


# ---------------------------------------------------------------- pipeline (home) and rule drawings (approach)
ICONS = {
    "seal": '<rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10 V7 a4 4 0 0 1 8 0 V10"/>',
    "hold": '<circle cx="7" cy="8" r="2.5"/><circle cx="17" cy="8" r="2.5"/><path d="M3 18 q4 -6 8 0 M13 18 q4 -6 8 0 M12 3 V21"/>',
    "plant": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="0.8"/>',
    "red": '<path d="M12 3 L19 6 V11 C19 16 16 19 12 21 C8 19 5 16 5 11 V6 Z"/><path d="M9 12 L11 14 L15 10"/>',
    "pub": '<path d="M6 3 H14 L18 7 V21 H6 Z"/><path d="M14 3 V7 H18 M9 12 H15 M9 16 H15"/>',
}
STEPS = (("seal", "Seal it", "Measure, threshold and pass mark hashed before any outcome is seen"),
         ("hold", "Hold people out", "Split by person; the same lab counts as a near-copy"),
         ("plant", "Plant an answer", "Recover an answer we put in on purpose, and reject fake signals"),
         ("red", "Red team", "Someone who did not build it tries to break it"),
         ("pub", "Publish either way", "Failures go out with the effect the test could have caught"))


def pipeline():
    """The five rules in site/content.json ("rules"), one step each."""
    items = "".join(f'<li><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[k]}</svg><b>{E(t)}</b><span>{E(d)}</span></li>' for k, t, d in STEPS)
    return (f'<figure class="pipe-fig"><p class="claim">Every claim takes the same five steps</p>'
            f'<ol class="pipe" aria-label="The path every result takes: seal, hold people out, plant an answer, red team, publish">{items}</ol></figure>')


def rule_pictures():
    """Approach: one drawing per rule, in the same order as content.json "rules"."""
    lines = lambda x, y, n=3: "".join(f'<path d="M{x} {y + i * 7} H{x + 22 - (i % 2) * 7}" class="s-mute"/>' for i in range(n))
    person = lambda x, y, c="s-ink": f'<circle cx="{x}" cy="{y}" r="4" class="{c}"/><path d="M{x-7} {y+13} q7 -9 14 0" class="{c}"/>'
    pics = [
        '<rect x="10" y="10" width="40" height="50" rx="4" class="card"/>' + lines(17, 20, 4)
        + '<rect x="62" y="30" width="22" height="16" rx="3" class="f-soft s-acc"/><path d="M66 30 v-5 a7 7 0 0 1 14 0 v5" class="s-acc"/>'
        + T(96, 42, "sha256", "t-s mono"),
        "".join(person(16 + i * 20, 22) for i in range(4)) + '<path d="M92 8 V58" class="s-acc dash"/>' + "".join(person(108 + i * 20, 22, "s-acc") for i in range(2))
        + T(46, 62, "build", "t-s", "middle") + T(118, 62, "test", "t-s acc", "middle"),
        '<path d="M8 30 C16 20 22 40 30 30 S44 22 50 30" class="s-ink"/><path d="M50 30 C56 30 58 8 64 8 S72 30 78 30" class="s-acc"/>'
        + T(64, 52, "planted", "t-s acc", "middle") + '<path d="M96 30 l3 -6 l3 9 l3 -12 l3 15 l3 -9 l3 6 l3 -4 l3 7 l3 -3 l3 2" class="s-mute"/>'
        + T(120, 52, "noise", "t-s", "middle"),
        '<rect x="10" y="14" width="56" height="40" rx="4" class="card"/>' + lines(17, 24)
        + '<path d="M102 10 L120 16 V28 C120 39 112 46 102 50 C92 46 84 39 84 28 V16 Z" class="f-soft s-acc"/><path d="M95 29 L100 34 L110 24" class="s-acc"/>'
        + '<path d="M70 32 H80" class="s-mute arr"/>',
        '<rect x="12" y="10" width="40" height="50" rx="4" class="card"/>' + lines(19, 20) + '<path d="M22 46 l5 5 l10 -10" class="s-acc"/>'
        + '<rect x="72" y="10" width="40" height="50" rx="4" class="card"/>' + lines(79, 20) + '<path d="M84 41 l10 10 M94 41 l-10 10" class="s-ink"/>'
        + T(62, 70, "both go out", "t-s", "middle"),
    ]
    return pics


def rules_figure(rules):
    pics = rule_pictures()
    items = "".join(f'<li><svg viewBox="0 0 150 74" aria-hidden="true">{p}</svg><b>{E(r[0])}</b><span>{E(r[1])}</span></li>' for p, r in zip(pics, rules))
    return f'<ol class="how" aria-label="Our five rules of evidence">{items}</ol>'


# ---------------------------------------------------------------- the data (home)
def data_matrix():
    """Open data by family and by kind of ground truth.
    Counts: experiments/ground_truth/counts.json (by_dataset_truth, l2_cases).
    Gaps: docs/DATASETS.md ("Not qualifying"), experiments/data_access/RESULTS.md (ketamine)."""
    c = jload("experiments/ground_truth/counts.json")
    bt = c["by_dataset_truth"]
    edf = bt.get("sleep-edfx|behaviour", 0)
    anaes = sum(v for k, v in bt.items() if k.endswith("|behaviour") and not k.startswith("sleep"))
    l2 = c["l2_cases"]
    cell = lambda n, s, hi=False: f'<div class="cell{" hi" if hi else ""}" role="cell"><b>{E(n)}</b><span>{E(s)}</span></div>'
    gap = lambda s: f'<div class="cell gap" role="cell"><b>Gap</b><span>{E(s)}</span></div>'
    rows = [("Sleep", cell(num(edf), "nights, Sleep-EDF"), cell(num(l2), "awakenings, DREAM", True)),
            ("Anaesthesia", cell(num(anaes), "recordings in 3 sets"), gap("no report per recording")),
            ("Brain injury", gap("none open"), gap("none open")),
            ("Ketamine", cell("1", "set, below anaesthetic dose"), gap("one restricted set, Milan cohort"))]
    body = ('<div class="dmx" role="table" aria-label="Open datasets by family and by kind of label">'
            '<div class="hrow" role="row"><span role="columnheader"></span><span role="columnheader">Labels from behaviour or sleep scoring<em>tests awake versus not</em></span>'
            '<span role="columnheader">Reports given on waking<em>tests where behaviour misleads</em></span></div>'
            + "".join(f'<div class="drow" role="row"><span class="fam" role="rowheader">{E(f)}</span>{a}{b}</div>' for f, a, b in rows) + "</div>")
    src = ("Data: " + code("experiments/ground_truth/counts.json") + ", " + code("docs/DATASETS.md") + ", " + code("experiments/data_access/RESULTS.md")
           + ". Ketamine: Farnes and colleagues 2020 is open but subanaesthetic, so people stayed responsive.")
    return fig(body, f"Sleep has {num(l2)} reported awakenings; brain injury has no open data at all", src, "fig dmx-fig")


# ---------------------------------------------------------------- findings (one small figure each)
def finding_fig(n):
    """Each figure reads the same files the finding cites."""
    if n == 1:   # docs/DATASETS.md, "Qualifying datasets": 4 sleep, 3 anaesthesia, 0 disorders of consciousness
        cols = (("Sleep", 4, 40), ("Anaesthesia", 3, 120), ("Brain injury", 0, 200))
        b = ""
        for name, k, cx in cols:
            for i in range(k):
                b += f'<rect x="{cx-12}" y="{72 - i * 22}" width="24" height="18" rx="3" class="f-soft s-acc"/>'
            if not k:
                b += f'<rect x="{cx-26}" y="38" width="52" height="52" rx="4" class="card dash"/>' + T(cx, 61, "none", "t-s", "middle") + T(cx, 75, "open", "t-s", "middle")
            b += T(cx, 108, name, "t-s", "middle") + T(cx, 121, str(k), "t-s t-b", "middle")
        return svg("0 0 240 122", b, "Open datasets with usable labels by family: sleep 4, anaesthesia 3, brain injury none.", "ffig")
    if n == 2:   # experiments/research_sweep/RESULTS.md: Sarasso 2015, Colombo 2019, Maschke 2024 share one cohort
        papers = (("Sarasso 2015", "PCI"), ("Colombo 2019", "spectral slope"), ("Maschke 2024", "criticality"))
        b = ""
        for i, (a, m) in enumerate(papers):
            y = 8 + i * 38
            b += f'<rect x="4" y="{y}" width="96" height="32" rx="4" class="card"/>' + T(10, y + 14, a, "t-s t-b") + T(10, y + 27, m, "t-xs")
            b += f'<path d="M100 {y + 16} C140 {y + 16} 150 60 170 60" class="s-mute"/>'
        b += '<circle cx="198" cy="60" r="28" class="f-soft s-acc"/>' + "".join(f'<circle cx="{198 + dx}" cy="{60 + dy}" r="3" class="f-acc"/>' for dx, dy in ((-10, -8), (0, -12), (10, -8), (-12, 6), (0, 4), (12, 6), (-4, 16), (6, 16)))
        b += T(198, 104, "one group of", "t-xs", "middle") + T(198, 116, "volunteers", "t-xs", "middle")
        return svg("0 0 240 122", b, "Three papers, Sarasso 2015, Colombo 2019 and Maschke 2024, all draw on one group of volunteers.", "ffig")
    if n == 3:   # experiments/rules/dry_run.json
        d = jload("experiments/rules/dry_run.json")
        a1, a2 = d["epoch_split"]["auc"], d["subject_split"]["auc"]
        x0, W = 74, 132
        b = (T(4, 26, "slices mixed", "t-s") + f'<rect x="{x0}" y="14" width="{W * a1:.1f}" height="18" rx="3" class="f-acc"/>' + T(x0 + W * a1 + 4, 27, f"{a1:.2f}", "t-s t-b")
             + T(4, 62, "split by", "t-s") + T(4, 75, "person", "t-s") + f'<rect x="{x0}" y="56" width="{W * a2:.1f}" height="18" rx="3" class="f-mute"/>' + T(x0 + W * a2 + 4, 69, f"{a2:.2f}", "t-s t-b")
             + f'<path d="M{x0 + W / 2} 6 V88" class="s-ink dash"/>' + T(x0 + W / 2, 102, "0.5 = chance", "t-xs", "middle")
             + f'<path d="M{x0} 88 H{x0 + W}" class="s-line"/>' + T(x0, 116, "AUC 0", "t-xs") + T(x0 + W, 116, "1", "t-xs", "middle"))
        return svg("0 0 240 122", b, f"On fake data with no real effect, mixing time slices of the same people gave AUC {a1:.2f}; splitting by person gave {a2:.2f}, near chance.", "ffig")
    if n == 4:   # experiments/ground_truth/counts.json, l2_by_stage_report
        c = jload("experiments/ground_truth/counts.json")["l2_by_stage_report"]
        st = ("N1", "N2", "N3", "REM")
        mx = max(c[f"{s}|experience"] + c[f"{s}|no_experience"] for s in st)
        x0, W, b = 36, 140, ""
        for i, s in enumerate(st):
            y = 6 + i * 22
            e_, n_ = c[f"{s}|experience"], c[f"{s}|no_experience"]
            we, wn = W * e_ / mx, W * n_ / mx
            b += T(4, y + 12, s, "t-s t-b") + f'<rect x="{x0}" y="{y}" width="{we:.1f}" height="15" class="f-acc"/><rect x="{x0 + we:.1f}" y="{y}" width="{wn:.1f}" height="15" class="f-mute"/>'
            b += T(x0 + we + wn + 4, y + 12, f"{e_} / {n_}", "t-xs")
        b += '<rect x="4" y="102" width="10" height="10" class="f-acc"/>' + T(18, 111, "experience", "t-xs") + '<rect x="90" y="102" width="10" height="10" class="f-mute"/>' + T(104, 111, "no experience", "t-xs")
        return svg("0 0 240 122", b, "Report-labelled awakenings by sleep stage, experience versus no experience: " + ", ".join(f"{s} {c[s + '|experience']} versus {c[s + '|no_experience']}" for s in st) + ".", "ffig")
    if n == 5:   # experiments/data_access/dream_access.csv
        rows = list(csv.DictReader((ROOT / "experiments/data_access/dream_access.csv").open()))
        b = ""
        k = 0
        for i, r in enumerate(rows):
            x, y = 8 + (i % 10) * 23, 16 + (i // 10) * 26
            op = r["access_live"].strip().lower().startswith("open")
            k += op
            b += f'<rect x="{x}" y="{y}" width="19" height="20" rx="3" class="{"f-acc" if op else "card dash"}"/>'
        b += T(8, 90, f"{k} open to download", "t-s acc t-b") + T(8, 106, f"{len(rows) - k} by request", "t-s")
        return svg("0 0 240 122", b, f"{k} of {len(rows)} DREAM packages can be downloaded without asking; {len(rows) - k} needs a request.", "ffig")
    return ""


def tried_decades(tried):
    """Findings 03: every approach in site/findings.json "tried", placed by the decade it started, shaped by its status tag."""
    decs = {}
    for t in tried:
        m = re.search(r"(19|20)(\d)\d", t.get("when", ""))
        if m:
            decs.setdefault(int(m.group(0)[:3] + "0"), []).append(t["status"])
    order = sorted(decs)
    b = ""
    for i, d in enumerate(order):
        y = 18 + i * 24
        b += T(4, y + 4, f"{d}s", "t-s t-b")
        for j, s in enumerate(sorted(decs[d], key=lambda s: {"part": 0, "weak": 1, "open": 2}.get(s, 3))):
            x = 62 + j * 18
            if s == "part":
                b += f'<circle cx="{x}" cy="{y}" r="6" class="f-acc"/>'
            elif s == "weak":
                b += f'<circle cx="{x}" cy="{y}" r="6" class="card"/><path d="M{x} {y-6} A6 6 0 0 0 {x} {y+6} Z" class="f-ink"/>'
            else:
                b += f'<circle cx="{x}" cy="{y}" r="6" class="card s-acc"/>'
    y = 18 + len(order) * 24 + 6
    b += (f'<circle cx="10" cy="{y}" r="5" class="f-acc"/>' + T(20, y + 4, "works in part", "t-xs")
          + f'<circle cx="104" cy="{y}" r="5" class="card"/><path d="M104 {y-5} A5 5 0 0 0 104 {y+5} Z" class="f-ink"/>' + T(114, y + 4, "weakened", "t-xs")
          + f'<circle cx="180" cy="{y}" r="5" class="card s-acc"/>' + T(190, y + 4, "still open", "t-xs"))
    n = {k: sum(t["status"] == k for t in tried) for k in ("part", "weak", "open")}
    lab = f"{len(tried)} approaches by the decade they began: {n['part']} work in part, {n['weak']} weakened, {n['open']} still open. None has settled the question."
    return fig(svg(f"0 0 260 {y + 12}", b, lab), "None of these approaches has settled the question",
               f"Data: the {len(tried)} approaches listed below, placed by the decade each began.", "fig narrow")


# ---------------------------------------------------------------- theories
THEORY_ART = {"Integrated information (IIT 4.0)": ("iit", "a tightly integrated zone at the back"),
              "Global neuronal workspace": ("gnw", "a sudden broadcast from the front"),
              "Recurrent processing": ("rpt", "local feedback in sensory areas"),
              "Higher-order theories": ("hot", "the front representing a state as its own"),
              "Predictive processing / active inference": ("pp", "the brain's best guess at its input"),
              "Attention schema": ("ast", "the brain's model of its own attention"),
              "Complexity and criticality measures": ("cx", "a rich, varied signal across the whole brain")}


def theory_grid(theories, status_chip):
    cards = ""
    for t in theories:
        k, where = THEORY_ART.get(t["name"], ("ours", ""))
        cards += (f'<li class="thy"><svg viewBox="0 0 120 90" aria-hidden="true">{mini_brain(k)}</svg>'
                  f'<b>{E(t["name"])}</b><span>{E(where)}</span>{status_chip(t["status"])}</li>')
    cards += ('<li class="thy ours"><svg viewBox="0 0 120 90" aria-hidden="true">' + mini_brain("ours") + '</svg>'
              '<b>Our own theory</b><span>joins once it is written and sealed</span><span class="chip chip-open">Not sealed</span></li>')
    lab = "Schematic side views of the brain, front on the left, one per theory: " + "; ".join(f"{t['name']}: {THEORY_ART.get(t['name'], ('', ''))[1]}" for t in theories) + "; our own theory: not yet written."
    return (f'<figure class="fig thy-fig"><p class="claim">Each theory puts experience somewhere different</p><ul class="thys" aria-label="{E(lab)}">{cards}</ul>'
            '<figcaption>Illustration: schematic, not anatomy. Front of the head on the left. Status is from the published record, as in the table below.</figcaption></figure>')


# ---------------------------------------------------------------- approach
def odds_figure(odds):
    """site/content.json "odds": the lead's estimates, drawn as ranges on 0-100%."""
    rows = ""
    for label, v in odds:
        m = re.match(r"(\d+)-(\d+)%", v)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
        elif v.startswith("under"):
            a, b = 0, int(re.search(r"\d+", v).group(0))
        else:
            a = b = None
        bar = (f'<span class="track"><span class="rng" style="left:{a}%;width:{max(b - a, 1.5)}%"></span></span>' if a is not None
               else '<span class="track none"></span>')
        rows += f'<li><span class="ol">{E(label)}</span>{bar}<span class="ov">{E(v)}</span></li>'
    return fig(f'<ol class="oddbars" aria-label="Our odds for each outcome">{rows}</ol>'
               '<div class="axis" aria-hidden="true"><span>0%</span><span>50%</span><span>100%</span></div>',
               "Our odds fall as the claim grows", "The project lead's estimates, November 2026. The hard problem is not attempted, so it has no bar.")


def spectrum_figure():
    """experiments/research_sweep/RESULTS.md: Maschke et al. 2025, Cerebral Cortex, 303 patients:
    LZC vs the 1-40 Hz exponent, r(197) = 0.86 shuffle-normalised, 0.24 phase-normalised."""
    rows = (("As usually computed", 0.86, "hi"), ("Spectrum controlled", 0.24, ""))
    b = "".join(f'<div class="hb"><span class="bl">{E(l)}</span><span class="track"><span class="fill {c}" style="width:{100 * v:.0f}%"></span></span><span class="bv">r = {v:.2f}</span></div>' for l, v, c in rows)
    return fig(f'<div class="hbars" role="img" aria-label="Correlation between Lempel-Ziv complexity and the slope of the EEG spectrum: 0.86 as usually computed, 0.24 once the spectrum is controlled.">{b}'
               '<div class="axis" aria-hidden="true"><span>0</span><span>0.5</span><span>1</span></div></div>',
               "Most of a popular complexity score was the spectrum's slope",
               "Data: Maschke and colleagues 2025, 303 patients, as checked in " + code("experiments/research_sweep/RESULTS.md") + ". Once the spectrum was controlled, the score's diagnostic value vanished.")


def flow(steps, label):
    """steps: (title, text, status word, status class)."""
    li = "".join(f'<li class="step"><span class="dot" aria-hidden="true">{i}</span><div><div class="sh">{E(t)}{f" <span class=\"chip chip-{c}\">{E(s)}</span>" if s else ""}</div><p>{d}</p></div></li>'
                 for i, (t, d, s, c) in enumerate(steps, 1))
    return f'<ol class="flow" aria-label="{E(label)}">{li}</ol>'


# ---------------------------------------------------------------- board
def board_map(tasks, milestones):
    """Tracker, contribute, home: every task on board/board.db as one tile, grouped by milestone, by status."""
    groups = {}
    for t in tasks:
        groups.setdefault(t["ms"], []).append(t)
    rows = ""
    for m in sorted(groups):
        tiles = "".join(f'<i class="bt-{t["state"]}" title="#{t["id"]} {E(t["title"])}"></i>' for t in groups[m])
        rows += f'<div class="bm-row"><span class="bm-lab"><b>{E(m)}</b> {E(milestones.get(m, ""))}</span><span class="bm-tiles">{tiles}</span></div>'
    n = {k: sum(t["state"] == k for t in tasks) for k in ("done", "run", "open")}
    lab = f"{len(tasks)} tasks on the board: {n['done']} done, {n['run']} being worked on, {n['open']} open."
    key = (f'<div class="key"><span><i class="k done"></i>Done {n["done"]}</span><span><i class="k part"></i>Being worked on {n["run"]}</span>'
           f'<span><i class="k open"></i>Open {n["open"]}</span></div>')
    return fig(f'<div class="bmap" role="img" aria-label="{E(lab)}">{rows}</div>{key}',
               f"{n['done']} of {len(tasks)} tasks done, {n['open']} open to take", "Data: the live task board, " + code("board/board.db") + ", one tile per task.")


def fig_levels(ours=False):
    """Findings 01 (known, third item) and Approach 04: the ladder of scales, with where each approach looks.
    Placements are the theories' own stated scales; EEG's scale is physics (summed activity of many neurons)."""
    rungs = ["Whole-brain activity", "Brain areas", "Local circuits", "Single neurons", "Synapses", "Molecules"]
    tags = {0: ("EEG, PCI" + (", our tests" if ours else ""), True), 1: ("Workspace theory", False),
            2: ("Recurrent processing theory", False), 5: ("Where anaesthetics act", False)}
    top, gap = 22, 30
    body = '<path d="M30 %d V%d" class="s-line"/>' % (top, top + gap * 5)
    for i, r in enumerate(rungs):
        y = top + i * gap
        acc = tags.get(i, ("", False))[1]
        body += f'<circle cx="30" cy="{y}" r="{5.5 if acc else 4.5}" class="{"f-acc" if acc else "card"}"/>' + T(44, y + 4, r, "t-b" if acc else "t")
        if i in tags:
            body += f'<path d="M188 {y} H196" class="s-mute"/>' + T(200, y + 4, tags[i][0], "t-s acc" if acc else "t-s")
    # integrated information theory: it looks for the level itself (where integrated information peaks)
    body += (f'<path d="M12 {top} V{top + gap * 5}" class="s-acc arr2"/>' + f'<path d="M8 {top + 6} L12 {top} L16 {top + 6}" class="s-acc"/>'
             + f'<path d="M8 {top + gap * 5 - 6} L12 {top + gap * 5} L16 {top + gap * 5 - 6}" class="s-acc"/>'
             + T(12, top + gap * 5 + 30, "Double arrow: integrated information theory.", "t-s acc")
             + T(12, top + gap * 5 + 44, "Experience sits at whichever level carries the", "t-s")
             + T(12, top + gap * 5 + 58, "most integrated information, so it must be found.", "t-s"))
    src = ("Illustration. Placements follow each theory's own account; the level search is from Hoel, Albantakis, Marshall and Tononi, 2016.")
    return fig(svg("0 0 360 236", body, "Illustration: a ladder of scales from molecules to whole-brain activity. EEG and PCI measure whole-brain activity, "
                   "workspace theory works with brain areas, recurrent processing theory with local circuits, and anaesthetics act on molecules. "
                   "Integrated information theory says the right level must be found."),
               "Each theory, and each measure, looks at its own level", src)
