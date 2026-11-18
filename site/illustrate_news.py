#!/usr/bin/env python3
"""News thumbnails for Open Mind: one original drawing per item in site/news.json.

The series looks like a page of sleep-lab chart paper: a faint green grid, a short recording trace along the foot,
pen-ink lines, night indigo for the subject and dawn amber for one detail. No text, no photographs, no brain scans,
nothing copied from a paper's figures. Drawings are editorial illustrations, not data.

Run: .venv/bin/python -I site/illustrate_news.py   (Pillow only)
Writes site/assets/news/<id>.webp (600x400, drawn at 3x) and site/assets/news/alt.json.
"""
import json, math, random
from pathlib import Path
from PIL import Image, ImageDraw

SITE = Path(__file__).resolve().parent
OUT = SITE / "assets" / "news"
PAPER, GRID, GRIDB = "#F3F4EF", "#E4EADD", "#D0DAC7"
INK, MUTE, CARD = "#23262C", "#9AA394", "#FBFCF8"
IND, IND_SOFT, AMB, AMB_SOFT = "#4B3A9C", "#DDD8F1", "#B06A12", "#F1DFC2"
S = 3

BRAIN = [(14, 44), (10, 27), (24, 12), (45, 10), (63, 6), (84, 8), (98, 17), (110, 25), (114, 39), (108, 51), (104, 58), (96, 61),
         (88, 61), (86, 69), (80, 73), (76, 69), (74, 63), (60, 65), (44, 65), (30, 61), (20, 58)]


def smooth(pts, n=12):
    """Closed Catmull-Rom curve through pts."""
    out = []
    for i in range(len(pts)):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % len(pts)], pts[(i + 2) % len(pts)]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    return out


class Art:
    def __init__(self, seed=1):
        self.im = Image.new("RGB", (600 * S, 400 * S), PAPER)
        self.d = ImageDraw.Draw(self.im)
        self.rng = random.Random(seed)
        for x in range(0, 601, 20):
            self.line([(x, 0), (x, 400)], GRIDB if x % 100 == 0 else GRID, 1 if x % 100 else 1.3)
        for y in range(0, 401, 20):
            self.line([(0, y), (600, y)], GRIDB if y % 100 == 0 else GRID, 1 if y % 100 else 1.3)
        # the series signature: a short recording trace along the foot of the page
        r = random.Random(5)
        self.line([(40 + i * 2, 364 + 4 * math.sin(i * 0.9) + r.uniform(-2, 2)) for i in range(70)], MUTE, 1.3)

    def P(self, pts):
        return [(round(x * S), round(y * S)) for x, y in pts]

    def line(self, pts, c=INK, w=2.4):
        self.d.line(self.P(pts), fill=c, width=max(1, round(w * S)), joint="curve")

    def poly(self, pts, fill=None, outline=INK, w=2.4):
        if fill:
            self.d.polygon(self.P(pts), fill=fill)
        if outline:
            self.line(list(pts) + [pts[0], pts[1]], outline, w)

    def rect(self, x, y, w, h, fill=CARD, r=10, outline=INK, lw=2.4):
        self.d.rounded_rectangle((x * S, y * S, (x + w) * S, (y + h) * S), radius=r * S, fill=fill,
                                 outline=outline, width=round(lw * S) if outline else 0)

    def circle(self, x, y, r, fill=None, outline=INK, w=2.4):
        self.d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=fill, outline=outline, width=round(w * S) if outline else 0)

    def dashed(self, pts, c=INK, w=2, on=8, off=7):
        segs = []
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            L = math.hypot(x2 - x1, y2 - y1)
            n = max(1, int(L))
            segs += [(x1 + (x2 - x1) * i / n, y1 + (y2 - y1) * i / n) for i in range(n)]
        for i in range(0, len(segs) - 1, on + off):
            self.line(segs[i:i + on], c, w)

    def arrow(self, x1, y1, x2, y2, c=INK, w=2.4, head=12):
        self.line([(x1, y1), (x2, y2)], c, w)
        a = math.atan2(y2 - y1, x2 - x1)
        self.line([(x2 - head * math.cos(a - 0.5), y2 - head * math.sin(a - 0.5)), (x2, y2),
                   (x2 - head * math.cos(a + 0.5), y2 - head * math.sin(a + 0.5))], c, w)

    def curve(self, p, c=INK, w=2.4):
        pts = []
        for i in range(81):
            t = i / 80
            u = 1 - t
            pts.append(tuple(u ** 3 * p[0][j] + 3 * u * u * t * p[1][j] + 3 * u * t * t * p[2][j] + t ** 3 * p[3][j] for j in (0, 1)))
        self.line(pts, c, w)

    def brain(self, x, y, s=1.0, fill=CARD, outline=INK, dashed=False):
        """Schematic side view, front on the left; (x, y) is the top-left of a 120x76 box at scale s."""
        pts = [(x + px * s, y + py * s) for px, py in smooth(BRAIN, 8)]
        self.poly(pts, fill, None if dashed else outline)
        if dashed:
            self.dashed(pts + [pts[0]], outline, 2.2)
        return lambda px, py: (x + px * s, y + py * s)

    def trace(self, x, y, w, fn, c=INK, lw=2.2):
        self.line([(x + i, y - fn(i)) for i in range(0, int(w) + 1)], c, lw)

    def person(self, x, y, s=1.0, c=INK, fill=None):
        self.circle(x, y, 11 * s, fill, c)
        self.curve([(x - 20 * s, y + 38 * s), (x - 18 * s, y + 16 * s), (x + 18 * s, y + 16 * s), (x + 20 * s, y + 38 * s)], c)

    def bubble(self, x, y, w, h, fill=CARD, c=INK, tail="left"):
        self.rect(x, y, w, h, fill, 16, c)
        tx = x + 26 if tail == "left" else x + w - 26
        self.poly([(tx - 9, y + h - 1), (tx - 18 if tail == "left" else tx + 18, y + h + 18), (tx + 9, y + h - 1)], fill, None)
        self.line([(tx - 9, y + h), (tx - 18 if tail == "left" else tx + 18, y + h + 18), (tx + 9, y + h)], c)

    def lines(self, x, y, w, n=3, c=MUTE, gap=14):
        for i in range(n):
            self.line([(x, y + i * gap), (x + w - (i % 2) * w * 0.3, y + i * gap)], c, 2)

    def save(self, path):
        self.im.resize((600, 400), Image.Resampling.LANCZOS).save(path, "WEBP", quality=80, method=6)


def wave(amp, per, ph=0.0):
    return lambda i: amp * math.sin(2 * math.pi * i / per + ph)


def noisy(amp, seed):
    r = random.Random(seed)
    parts = [(r.uniform(5, 30), r.uniform(0, 6.3), r.uniform(0.4, 1)) for _ in range(6)]
    tot = sum(p[2] for p in parts)
    return lambda i: amp * sum(a * math.sin(2 * math.pi * i / p + ph) for p, ph, a in parts) / tot


# ------------------------------------------------------------------ one drawing per news item
def draw(key, a):
    if key == "adversarial-testing-of-global-neuronal-workspace":   # two theories, two predictions, tested head to head
        f = a.brain(46, 100, 2.0)
        a.circle(*f(34, 30), 14, IND, None)
        for p in ((64, 18), (92, 30), (86, 50)):
            a.line([f(34, 30), f(*p)], IND, 2.6); a.circle(*f(*p), 6, IND, None)
        g = a.brain(326, 100, 2.0)
        a.circle(*g(90, 36), 28, IND_SOFT, IND)
        for p in ((84, 26), (98, 32), (92, 46), (80, 40)):
            a.circle(*g(*p), 5, IND, None)
        a.line([(300, 80), (300, 300)], INK, 2.4)
        a.circle(300, 190, 15, AMB, None)
    elif key == "intrepid-an-adversarial-collaboration-of-iit-neu":  # a plan agreed in advance, boxes still empty
        a.rect(200, 70, 200, 250, CARD, 12)
        a.rect(255, 56, 90, 30, AMB_SOFT, 8, INK)
        for i in range(4):
            y = 120 + i * 48
            a.rect(228, y, 26, 26, CARD, 5)
            a.lines(270, y + 13, 104, 1, MUTE)
        a.circle(110, 150, 34, IND_SOFT, IND)
        a.arrow(450, 140, 520, 140, IND); a.arrow(520, 230, 450, 230, IND)
        a.curve([(110, 190), (110, 260), (150, 290), (196, 290)], MUTE, 2)
    elif key == "bandara-dcm-reanalysis-cogitate-meg":   # the frontal flare at onset and again at offset
        a.rect(150, 70, 300, 40, IND_SOFT, 8, IND)
        a.line([(150, 62), (150, 300)], INK, 2); a.line([(450, 62), (450, 300)], INK, 2)
        a.trace(60, 240, 480, lambda i: 70 * math.exp(-((i - 108) / 16) ** 2) + 70 * math.exp(-((i - 408) / 16) ** 2) + 4 * math.sin(i / 5), IND, 3)
        a.circle(450, 166, 12, AMB, None)
    elif key == "bryant-whyte-connectivity-ncc-cogitate":   # many ways to measure connectivity, a few agree
        r = random.Random(4)
        for i in range(8):
            for j in range(5):
                x, y = 92 + i * 54, 70 + j * 50
                hi = (i, j) in ((1, 1), (5, 3), (6, 1))
                a.rect(x, y, 40, 40, IND if hi else CARD, 6, IND if hi else MUTE, 2)
                for k in range(3):
                    if not hi:
                        a.line([(x + 8 + r.uniform(0, 20), y + 10 + k * 10), (x + 14 + r.uniform(0, 18), y + 10 + k * 10)], MUTE, 1.6)
        a.circle(372, 238, 9, AMB, None)
    elif key == "dream-eeg-mentation-database":   # twenty studies pooled into one
        r = random.Random(9)
        for i in range(10):
            y = 60 + i * 26
            a.trace(60, y, 170, noisy(7, i), MUTE if i % 3 else INK, 1.8)
            a.curve([(234, y), (290, y), (300, 200), (340, 200)], MUTE, 1.4)
        a.rect(340, 120, 190, 160, IND_SOFT, 18, IND)
        for k in range(3):
            a.line([(360, 165 + k * 34), (510, 165 + k * 34)], IND, 2)
        a.bubble(420, 50, 92, 52, CARD, INK, "left")
        a.circle(466, 76, 8, AMB, None)
    elif key == "repeated-awakening-propofol-dreaming-ds005620":   # sedation lowered complexity; dream and no-dream looked alike
        a.trace(50, 210, 230, lambda i: (26 - i * 0.09) * math.sin(i / 2.6) * (1 if i < 80 else 0.55) + noisy(6, 3)(i), INK, 2.2)
        a.line([(300, 70), (300, 320)], MUTE, 2)
        a.bubble(340, 70, 180, 70, IND_SOFT, IND)
        a.circle(372, 105, 9, AMB, None)
        a.lines(394, 98, 100, 2, IND, 16)
        a.bubble(340, 190, 180, 70, CARD, INK)
        a.line([(410, 290), (450, 290)], INK, 3); a.line([(410, 302), (450, 302)], INK, 3)
    elif key == "maschke-etiology-alpha-complexity-exponent":   # the complexity score traced the spectral slope
        a.line([(110, 70), (110, 320), (510, 320)], INK, 2.4)
        a.line([(130, 100), (490, 290)], IND, 6)
        a.line([(130, 108), (490, 286)], AMB, 2.4)
        for i, (x, y) in enumerate(((180, 120), (260, 175), (340, 210), (420, 250))):
            a.circle(x, y, 8, CARD, INK)
    elif key == "newman-criticality-pci-doc":   # stood in for the index in some patients, not all
        for i in range(10):
            x, y = 90 + (i % 5) * 100, 120 + (i // 5) * 120
            ok = i in (0, 1, 2, 6)
            a.person(x, y, 1.15, IND if ok else MUTE, IND_SOFT if ok else None)
        a.line([(60, 258), (540, 258)], MUTE, 1.6)
        a.circle(290, 92, 7, AMB, None)
    elif key == "luppi-integration-anaesthesia-mammals":   # four species, integration breaks under anaesthesia
        for i, r in enumerate((62, 46, 34, 24)):
            cx = 110 + i * 125 if i else 110
            cx = (110, 250, 360, 450)[i]
            a.circle(cx, 190, r, IND_SOFT, IND)
            pts = [(cx + r * 0.55 * math.cos(t), 190 + r * 0.55 * math.sin(t)) for t in (0.3, 2.2, 4.1)]
            for k in range(3):
                p, q = pts[k], pts[(k + 1) % 3]
                mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
                a.line([p, (mid[0] - (q[0] - p[0]) * 0.1, mid[1] - (q[1] - p[1]) * 0.1)], IND, 2)
            for p in pts:
                a.circle(*p, 3.5, IND, None)
        a.arrow(500, 120, 540, 120, AMB, 3)
    elif key == "butlin-indicators-consciousness-ai":   # check the machine's workings against a list, not its words
        a.rect(90, 110, 170, 170, CARD, 14)
        a.rect(130, 150, 90, 90, IND_SOFT, 8, IND)
        for k in range(4):
            for side in (0, 1):
                x = 120 + k * 35 if True else 0
                a.line([(112 + k * 42, 110), (112 + k * 42, 92)], INK, 2) if side == 0 else a.line([(112 + k * 42, 280), (112 + k * 42, 298)], INK, 2)
        a.rect(340, 80, 180, 240, CARD, 12)
        for i in range(5):
            y = 112 + i * 42
            a.rect(360, y - 12, 24, 24, CARD, 5)
            if i in (0, 2):
                a.line([(365, y), (371, y + 6), (380, y - 6)], IND, 3)
            a.lines(398, y, 100, 1)
        a.bubble(200, 40, 70, 40, CARD, MUTE, "left")
        a.dashed([(196, 38), (276, 84)], AMB, 2.6)
    elif key == "psilocybin-midazolam-eeg-complexity":   # complexity still rose as the effects came on
        a.trace(60, 200, 480, lambda i: (6 + i * 0.07) * (math.sin(i / 3.1) + 0.7 * math.sin(i / 1.7 + 1) * (i / 480) + 0.5 * noisy(1, 2)(i) * (i / 300)), INK, 2.2)
        a.line([(60, 300), (540, 300)], MUTE, 1.6)
        a.curve([(60, 300), (260, 296), (420, 260), (540, 150)], IND, 4)
        a.circle(540, 150, 9, AMB, None)
    elif key == "resting-eeg-dynamics-predict-the-perturbational":   # resting signal predicts the pulse-based index
        a.trace(60, 200, 190, noisy(18, 11), INK, 2.2)
        a.arrow(270, 200, 340, 200, IND, 3)
        a.line([(380, 300), (520, 300)], INK, 2)
        for i, h in enumerate((150, 92, 196)):
            a.rect(390 + i * 44, 300 - h, 30, h, IND_SOFT, 4, IND)
            a.line([(386 + i * 44, 300 - h - 6), (424 + i * 44, 300 - h - 6)], AMB, 2.6)
    elif key == "integrated-information-estimates-rise-under-prop":   # the proxy went up while the index went down
        a.rect(110, 90, 160, 210, CARD, 14)
        a.arrow(190, 270, 190, 120, IND, 5, 22)
        a.rect(330, 90, 160, 210, CARD, 14)
        a.arrow(410, 120, 410, 270, INK, 5, 22)
        a.circle(300, 195, 10, AMB, None)
    elif key == "the-integrated-information-theory-of-consciousne":   # an open letter, and a question over the theory
        a.rect(150, 70, 230, 270, CARD, 8)
        a.lines(180, 112, 170, 8, MUTE, 22)
        for i in range(6):
            a.line([(186 + i * 26, 300), (200 + i * 26, 292)], INK, 2)
        a.circle(420, 150, 64, IND_SOFT, IND)
        a.curve([(396, 134), (396, 104), (446, 104), (444, 136)], IND, 7)
        a.line([(444, 136), (420, 156), (420, 172)], IND, 7)
        a.circle(420, 196, 6, AMB, None)
    elif key == "iit-4-0":   # a small system's cause-effect structure
        nodes = ((200, 120), (400, 120), (300, 290))
        for i, p in enumerate(nodes):
            for j, q in enumerate(nodes):
                if i != j:
                    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
                    nx, ny = (q[1] - p[1]) * 0.06, -(q[0] - p[0]) * 0.06
                    a.curve([p, (mx + nx, my + ny), (mx + nx, my + ny), q], IND, 2.4)
        for p in nodes:
            a.circle(*p, 34, IND_SOFT, IND, 3)
        a.circle(300, 178, 9, AMB, None)
    elif key == "siclari-neural-correlates-of-dreaming":   # less slow activity at the back before a dream report
        f = a.brain(50, 110, 2.4)
        a.circle(*f(90, 34), 30, AMB_SOFT, AMB)
        a.trace(*f(78, 34), 26, wave(3, 6), INK, 1.8)
        a.trace(*f(18, 38), 44, wave(10, 22), INK, 2.4)
        a.bubble(380, 60, 160, 84, IND_SOFT, IND)
        a.circle(416, 100, 10, IND, None); a.lines(440, 94, 80, 2, IND, 16)
    elif key == "casarotto-pci-stratification":   # one cutoff; some 'vegetative' patients land above it
        r = random.Random(21)
        a.dashed([(60, 190), (540, 190)], AMB, 3)
        for i in range(22):
            a.circle(80 + i * 21, r.uniform(90, 170), 7, IND, None)
        for i in range(16):
            x = 90 + i * 28
            up = i in (3, 9, 13)
            a.circle(x, r.uniform(120, 175) if up else r.uniform(210, 300), 7, CARD, INK, 2.4)
    elif key == "casali-pci-2013":   # a magnetic pulse, and the echo it leaves
        f = a.brain(140, 90, 2.6)
        a.circle(*f(34, 30), 9, AMB, None)
        x, y = f(34, 30)
        for k, rr in enumerate((40, 72, 104, 136)):
            a.d.arc(((x - rr) * S, (y - rr) * S, (x + rr) * S, (y + rr) * S), -40, 70, fill=IND, width=round((3.2 - k * 0.5) * S))
        a.line([(x - 50, y - 70), (x - 34, y - 40), (x - 48, y - 36), (x - 30, y - 10)], AMB, 3)
    elif key == "sarasso-ketamine-pci":   # still, unresponsive, yet a wake-like echo and a vivid dream
        a.person(150, 200, 1.6, INK, CARD)
        a.line([(140, 196), (150, 199), (160, 196)], INK, 2)
        x, y = 150, 192
        for k, rr in enumerate((60, 90, 120)):
            a.d.arc(((x - rr) * S, (y - rr) * S, (x + rr) * S, (y + rr) * S), -60, 60, fill=IND, width=round((3 - k * 0.5) * S))
        a.bubble(330, 70, 210, 120, IND_SOFT, IND)
        a.circle(390, 128, 22, AMB_SOFT, AMB)
        a.poly([(430, 160), (466, 104), (500, 160)], CARD, IND)
    elif key == "schartner-psychedelic-signal-diversity":   # signal diversity above the waking line
        a.line([(80, 310), (520, 310)], INK, 2)
        a.dashed([(80, 190), (520, 190)], INK, 2)
        for i, h in enumerate((120, 166, 172, 178)):
            a.rect(110 + i * 105, 310 - h, 60, h, IND if i else IND_SOFT, 6, IND)
        a.circle(460, 112, 8, AMB, None)


ALT = {
    "adversarial-testing-of-global-neuronal-workspace": "Two schematic brains side by side: one lit at the front with lines spreading out, one lit at the back, divided by a line.",
    "intrepid-an-adversarial-collaboration-of-iit-neu": "A clipboard with empty tick boxes between a round token and two opposed arrows: a plan agreed before any results.",
    "bandara-dcm-reanalysis-cogitate-meg": "A trace with two equal peaks, one where a picture appears and one where it disappears.",
    "bryant-whyte-connectivity-ncc-cogitate": "A grid of forty small panels, three of them filled in.",
    "dream-eeg-mentation-database": "Ten recording traces flowing into one database, with a speech bubble above.",
    "repeated-awakening-propofol-dreaming-ds005620": "A trace that quietens, then two speech bubbles, one with content and one empty, joined by an equals sign.",
    "maschke-etiology-alpha-complexity-exponent": "Two lines, one thick and one thin, lying almost exactly on top of each other on a chart.",
    "newman-criticality-pci-doc": "Ten figures of people, four of them filled in and six left pale.",
    "luppi-integration-anaesthesia-mammals": "Four circles of shrinking size, each holding a small network whose links are broken.",
    "butlin-indicators-consciousness-ai": "A chip beside a checklist with two boxes ticked, and a crossed-out speech bubble.",
    "psilocybin-midazolam-eeg-complexity": "A trace that grows more varied from left to right, under a rising curve.",
    "resting-eeg-dynamics-predict-the-perturbational": "A resting trace with an arrow to three bars, each matched by a short line at its top.",
    "integrated-information-estimates-rise-under-prop": "Two panels: an arrow pointing up and an arrow pointing down.",
    "the-integrated-information-theory-of-consciousne": "A long signed letter beside a large question mark.",
    "iit-4-0": "Three circles, each linked to the other two by arrows in both directions.",
    "siclari-neural-correlates-of-dreaming": "A schematic brain with small fast waves at the back and slow waves at the front, beside a speech bubble.",
    "casarotto-pci-stratification": "Dots above and below a dashed cutoff line, with three hollow dots above it.",
    "casali-pci-2013": "A schematic brain with a pulse at the front and echoes rippling across it.",
    "sarasso-ketamine-pci": "A still figure with echoes spreading from the head, and a dream bubble holding a sun and a mountain.",
    "schartner-psychedelic-signal-diversity": "Four bars, the last three rising above a dashed line.",
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    items = json.loads((SITE / "news.json").read_text())["items"]
    alts = {}
    for k, it in enumerate(items):
        a = Art(seed=k)
        draw(it["id"], a)
        a.save(OUT / f'{it["id"]}.webp')
        alts[it["id"]] = "Illustration: " + ALT.get(it["id"], "an abstract drawing on chart paper.")
    (OUT / "alt.json").write_text(json.dumps(alts, indent=1))
    tot = sum(p.stat().st_size for p in OUT.glob("*.webp"))
    print(f"wrote {len(items)} thumbnails, {tot // 1024} KB")


if __name__ == "__main__":
    main()
