"""Open Mind brand art. Read by site/build.py (stdlib only, same output on every build).

The look is a sleep-lab recording: pale chart paper with a faint grid, a night indigo for links, and a dawn amber used
only in motifs. The mark is a Necker cube: one drawing, two ways of seeing it. Same input, a different experience,
which is the puzzle the project works on. The hero is a night's recording drawn from textbook wave shapes.
"""
import math, random

NAME_MARK = "a Necker cube"
MARK = ('<path d="M5 12h14v14H5z"/><path d="M13 6h14v14H13z"/>'
        '<path d="M5 12l8-6M19 12l8-6M19 26l8-6M5 26l8-6"/>')

W, SEG = 560, 140  # four stages of 140 px each
STAGES = [("Awake", "wake"), ("Light sleep", "n2"), ("Deep sleep", "n3"), ("Dreaming sleep", "rem")]


def _noise(rng, n=6, lo=3.0, hi=14.0):
    """A smooth random wiggle: a sum of a few sines with random periods (px) and phases."""
    parts = [(rng.uniform(lo, hi), rng.uniform(0, 6.283), rng.uniform(0.4, 1.0)) for _ in range(n)]
    tot = sum(a for _, _, a in parts)
    return lambda x: sum(a * math.sin(6.283 * x / p + ph) for p, ph, a in parts) / tot


def _eeg(stage, x, rng_f):
    """Brain-wave trace for one stage at local position x (0-140), in px of deflection."""
    n = rng_f(x)
    if stage == "wake":   # small, fast waves
        return 3.2 * math.sin(6.283 * x / 4.2) * (0.6 + 0.4 * math.sin(x / 9)) + 1.6 * n
    if stage == "n2":     # slower waves, one sleep spindle and one K-complex
        v = 4.5 * n + 2.2 * math.sin(6.283 * x / 11)
        if 22 < x < 54:
            v += 6 * math.sin(math.pi * (x - 22) / 32) * math.sin(6.283 * x / 3.4)
        if 88 < x < 116:
            t = (x - 88) / 28
            v += -26 * math.exp(-((t - 0.35) / 0.13) ** 2) + 13 * math.exp(-((t - 0.7) / 0.17) ** 2)
        return v
    if stage == "n3":     # large, slow waves
        return 19 * math.sin(6.283 * x / 37 + 0.6) * (0.75 + 0.25 * math.sin(x / 23)) + 3 * n
    # dreaming: small mixed waves like waking, with saw-tooth runs
    v = 2.8 * math.sin(6.283 * x / 6.5) + 2.2 * n
    if 30 < x < 70 or 98 < x < 124:
        v += 5 * (((x / 10) % 1) - 0.5) * 2
    return v


def _eyes(stage, x, rng):
    if stage == "wake":   # two blinks
        return sum(-14 * math.exp(-((x - c) / 3) ** 2) for c in (38, 104))
    if stage == "n2":     # slow rolling
        return 6 * math.sin(6.283 * x / 140)
    if stage == "n3":
        return 0.6 * math.sin(x / 7)
    # dreaming: rapid eye movements, sharp jumps that settle back
    v = 0.0
    for c, a in ((20, 13), (44, -11), (58, 12), (86, -13), (112, 11), (126, -9)):
        if x >= c:
            v += a * math.exp(-(x - c) / 6)
    return v


def _path(fn, y0, scale=1.0):
    pts = [f"{x},{y0 - fn(x) * scale:.1f}" for x in range(0, W + 1)]
    return "M" + " L".join(pts)


def hero():
    rng = random.Random(7)
    fs = {s: _noise(random.Random(i * 13 + 1)) for i, (_, s) in enumerate(STAGES)}

    def trace(kind):
        def f(x):
            i = min(int(x // SEG), 3)
            s = STAGES[i][1]
            v = _eeg(s, x - i * SEG, fs[s]) if kind == "eeg" else _eyes(s, x - i * SEG, rng)
            # blend 8 px either side of each stage boundary so the line has no jumps
            b = (i + 1) * SEG
            if i < 3 and x > b - 8:
                s2 = STAGES[i + 1][1]
                w = (x - (b - 8)) / 16
                v2 = _eeg(s2, x - b, fs[s2]) if kind == "eeg" else _eyes(s2, x - b, rng)
                v = v * (1 - w) + v2 * w
            if i > 0 and x < i * SEG + 8:
                s0 = STAGES[i - 1][1]
                w = (i * SEG + 8 - x) / 16
                v0 = _eeg(s0, x - (i - 1) * SEG, fs[s0]) if kind == "eeg" else _eyes(s0, x - (i - 1) * SEG, rng)
                v = v * (1 - w) + v0 * w
            return v
        return f

    grid = "".join(f'<path d="M{x} 40V214" class="g{"" if x % 70 else " gb"}"/>' for x in range(0, W + 1, 14))
    grid += "".join(f'<path d="M0 {y}H{W}" class="g{"" if (y - 40) % 58 else " gb"}"/>' for y in range(40, 215, 29))
    labels = "".join(f'<text x="{i * SEG + 6}" y="28" class="st">{n}</text>' for i, (n, _) in enumerate(STAGES))
    seps = "".join(f'<path d="M{i * SEG} 16V286" class="sep"/>' for i in range(1, 4))
    hyp = "M0 240H140V264H280V278H420V252H560"
    return f'''<figure class="hero-art"><svg viewBox="-34 0 {W + 40} 300" role="img" aria-label="Illustration of a night's sleep recording: brain waves and eye movements in four stages, awake, light sleep, deep sleep and dreaming sleep, with a sleep-stage chart underneath">
<rect x="420" y="36" width="140" height="250" class="rem"/>
{grid}{seps}{labels}
<text x="-6" y="92" class="ch">brain</text><text x="-6" y="172" class="ch">eyes</text><text x="-6" y="262" class="ch">stage</text>
<path d="{_path(trace("eeg"), 92)}" class="tr"/>
<path d="{_path(trace("eye"), 168)}" class="tr"/>
<path d="{hyp}" class="hyp"/><path d="M420 252H560" class="hyp-rem"/>
</svg>
<figcaption>Illustration drawn from textbook wave shapes. Dreaming sleep (shaded) looks almost like waking on the recording, and people woken from it usually report experiences. Deep sleep looks very different, yet people woken from it sometimes report experiences too. Telling these cases apart is the test.</figcaption></figure>'''


# Wordmark: "OPEN MIND" in single strokes on a 40-unit cap height, drawn here so it needs no font.
# Each letter is (width, path) in its own box; the lockup puts the Necker cube first.
LETTERS = {
    "O": (30, "M15 0C6.7 0 2 9 2 20S6.7 40 15 40 28 31 28 20 23.3 0 15 0Z"),
    "P": (24, "M2 40V0H13C19 0 22 4.5 22 10.5S19 21 13 21H2"),
    "E": (22, "M21 0H2V40H21M2 20H18"),
    "N": (28, "M2 40V0L26 40V0"),
    "M": (34, "M2 40V0L17 26L32 0V40"),
    "I": (4, "M2 0V40"),
    "D": (28, "M2 0H11C21 0 26 9 26 20S21 40 11 40H2Z"),
    " ": (14, ""),
}


def wordmark(with_mark=True, gap=9):
    """Return (svg_inner, width, height) for the lockup, in a 40-high letter space."""
    parts, x = [], 0
    if with_mark:
        parts.append(f'<g transform="translate(-6 -6) scale(1.6)" stroke-width="2.4">{MARK}</g>')
        x = 52
    for ch in "OPEN MIND":
        w, d = LETTERS[ch]
        if d:
            parts.append(f'<path transform="translate({x} 0)" d="{d}"/>')
        x += w + gap
    return "".join(parts), x - gap, 40


def wordmark_svg(color="#4B3A9C", with_mark=True):
    inner, w, h = wordmark(with_mark)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-4 -4 {w + 8} {h + 8}" width="{(w + 8) * 2}" height="{(h + 8) * 2}" '
            f'role="img" aria-label="Open Mind" fill="none" stroke="{color}" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round">'
            f'<title>Open Mind</title>{inner}</svg>\n')


def mark_svg_file(color="#4B3A9C"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="256" height="256" role="img" aria-label="Open Mind mark, a Necker cube" '
            f'fill="none" stroke="{color}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><title>Open Mind</title>{MARK}</svg>\n')
