#!/usr/bin/env python3
"""News thumbnails for Open Mind: one original drawing per item in site/news.json.

The series looks like a page of sleep-lab chart paper: a faint green grid, a short recording trace along the foot,
pen-ink lines, night indigo for the subject and dawn amber for one detail. No text, no photographs, no brain scans,
nothing copied from a paper's figures. Drawings are editorial illustrations, not data.

Run: .venv/bin/python -I site/illustrate_news.py   (Pillow only)
Writes site/assets/news/<id>.webp (600x400, drawn at 3x) and site/assets/news/alt.json,
plus one drawing per library topic in site/assets/library/<topic>.webp and site/assets/library/alt.json.
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

    elif key == "rochas-n2-dreaming-hdeeg":   # light sleep: fast activity at the back before a thought-like dream
        f = a.brain(40, 120, 2.3)
        for k, (px, py) in enumerate(((86, 24), (98, 34), (92, 48))):
            x, y = f(px, py)
            a.trace(x - 18, y, 36, wave(4, 6, k), IND, 2.2)
        x, y = f(30, 36)
        a.trace(x - 22, y, 44, wave(7, 30), MUTE, 2)
        a.bubble(360, 70, 180, 110, CARD, INK, "left")
        a.lines(384, 104, 130, 3, IND, 18)
        a.circle(520, 92, 7, AMB, None)
        a.curve([(70, 320), (200, 300), (360, 300), (530, 320)], MUTE, 2)
    elif key == "selte-nrem-experience-hdeeg":   # hundreds of awakenings, about half with a dream
        r = random.Random(12)
        for i in range(16):
            for j in range(3):
                x, y = 70 + i * 18, 90 + j * 34
                a.circle(x, y, 6, IND if r.random() < 0.5 else CARD, IND if True else INK, 1.8)
        a.line([(360, 300), (360, 80), (540, 80)], MUTE, 0)
        a.line([(360, 80), (360, 300), (540, 300)], INK, 2.4)
        a.dashed([(360, 300), (540, 120)], MUTE, 2)
        a.curve([(360, 300), (372, 190), (430, 140), (540, 120)], IND, 4)
        a.circle(404, 160, 8, AMB, None)
        a.trace(70, 250, 260, noisy(14, 21), INK, 2)
    elif key == "stoliker-psilocybin-context-ds006110":   # four settings, and a path that follows them
        boxes = ((80, 80), (330, 80), (80, 230), (330, 230))
        for (x, y) in boxes:
            a.rect(x, y, 190, 100, CARD, 12, MUTE, 2)
        a.circle(175, 130, 20, None, INK)                                    # rest
        a.poly([(400, 160), (425, 108), (450, 160)], None, INK)              # meditation
        a.circle(160, 300, 9, INK, None); a.line([(168, 300), (168, 252), (194, 246), (194, 262)], INK, 2.4)  # music
        a.circle(194, 290, 9, INK, None)
        a.rect(385, 255, 80, 50, None, 4, INK); a.poly([(415, 268), (415, 292), (436, 280)], INK, None)        # film
        a.curve([(250, 130), (310, 60), (300, 220), (360, 210)], IND, 3.4)
        a.curve([(360, 210), (420, 200), (250, 330), (240, 270)], IND, 3.4)
        a.circle(240, 270, 8, AMB, None)
    elif key == "berjaga-buisan-fdt-nonequilibrium":   # a signal with a direction in time, and a scale out of balance
        a.trace(60, 150, 300, lambda i: 30 * ((i % 50) / 50) - 15, INK, 2.6)
        a.arrow(60, 210, 360, 210, IND, 3)
        a.line([(450, 300), (450, 150)], INK, 3)
        a.line([(380, 130), (520, 170)], INK, 3)
        a.circle(450, 150, 6, INK, None)
        a.line([(380, 130), (366, 190), (394, 190), (380, 130)], INK, 1.8)
        a.line([(520, 170), (506, 230), (534, 230), (520, 170)], INK, 1.8)
        a.rect(364, 190, 32, 8, IND, 3, None)
        a.rect(498, 230, 44, 12, IND, 3, None)
        a.circle(520, 214, 8, AMB, None)
        a.line([(420, 300), (480, 300)], INK, 3)
    elif key == "congyu-neural-field-doc":   # a loop between thalamus and cortex, and a model that copies the signal
        f = a.brain(40, 110, 2.3)
        cx, cy = f(62, 42)
        a.circle(cx, cy, 16, IND_SOFT, IND)
        a.curve([(cx - 10, cy - 14), (cx - 60, cy - 80), (cx + 40, cy - 110), (cx + 14, cy - 18)], IND, 2.6)
        a.arrow(cx + 26, cy - 50, cx + 16, cy - 20, IND, 2.6, 10)
        a.trace(360, 160, 180, noisy(18, 7), INK, 2.4)
        a.trace(360, 160, 180, lambda i: noisy(18, 7)(i) * 0.92 + 2, AMB, 1.6)
        a.trace(360, 260, 180, noisy(14, 8), INK, 2.4)
        a.trace(360, 260, 180, lambda i: noisy(14, 8)(i) * 0.9 - 2, AMB, 1.6)
    elif key == "onoda-local-phi-nrem":   # a tightly joined four-part knot loosens in sleep; the spike rows thin out too
        for cx, awake in ((170, True), (430, False)):
            pts = [(cx - 52, 130), (cx + 52, 130), (cx + 52, 226), (cx - 52, 226)]
            col = IND if awake else MUTE
            for i, p in enumerate(pts):
                for q in pts[i + 1:]:
                    if awake:
                        a.line([p, q], IND, 2.6)
            if not awake:
                a.dashed([pts[0], pts[1]], MUTE, 1.8)
                a.line([pts[2], pts[3]], MUTE, 2)
            for p in pts:
                a.rect(p[0] - 15, p[1] - 15, 30, 30, IND if awake else CARD, 6, col, 2.2)
            r = random.Random(11 if awake else 12)
            for row in range(3):
                y = 266 + row * 18
                for _ in range(22 if awake else 8):
                    x = cx - 90 + r.uniform(0, 180)
                    a.line([(x, y - 6), (x, y + 6)], INK if awake else MUTE, 1.8)
        a.arrow(272, 178, 328, 178, INK, 2.2)
        a.circle(482, 226, 6, AMB, None)
    elif key == "zhou-alpha-coherence-doc-recovery":   # loose, out-of-step nodes at the back, then a linked network
        f = a.brain(50, 120, 1.8, dashed=True)
        pts = [(84, 26), (100, 36), (94, 52), (76, 44)]
        for p in pts:
            a.circle(*f(*p), 6, CARD, MUTE, 2)
        a.dashed([f(*pts[0]), f(*pts[2])], MUTE, 1.6)
        a.arrow(272, 190, 318, 190, INK, 2.2)
        g = a.brain(340, 120, 1.8)
        for i, p in enumerate(pts):
            for q in pts[i + 1:]:
                a.line([g(*p), g(*q)], IND, 2.2)
        for p in pts:
            a.circle(*g(*p), 7, IND, None)
        a.trace(400, 80, 150, wave(9, 25), IND, 2.2)
        a.circle(*g(100, 36), 4, AMB, None)
    elif key == "nunez-waveform-morphology":   # the same rhythm, symmetric and lopsided
        a.trace(70, 140, 460, wave(40, 115), INK, 2.6)
        def saw(i):
            t = (i % 115) / 115
            return 40 * (math.sin(math.pi * t / 0.3) if t < 0.3 else -math.sin(math.pi * (t - 0.3) / 0.7))
        a.trace(70, 280, 460, saw, IND, 3)
        a.circle(105, 240, 8, AMB, None)
        a.line([(70, 210), (530, 210)], MUTE, 1.4)
    elif key == "gaglioti-structural-complexity":   # orderly, in-between and random wiring; the middle one stands out
        for k, (cx, kind) in enumerate(((120, "ring"), (300, "small"), (480, "rand"))):
            r = random.Random(30 + k)
            pts = [(cx + 72 * math.cos(2 * math.pi * i / 12), 190 + 72 * math.sin(2 * math.pi * i / 12)) for i in range(12)]
            col = IND if kind == "small" else INK
            if kind != "rand":
                for i in range(12):
                    a.line([pts[i], pts[(i + 1) % 12]], col, 2)
            chords = {"ring": [], "small": [(0, 5), (3, 9)], "rand": [(r.randrange(12), r.randrange(12)) for _ in range(14)]}[kind]
            for i, j in chords:
                if i != j:
                    a.line([pts[i], pts[j]], col, 2)
            for p in pts:
                a.circle(*p, 6, IND_SOFT if kind == "small" else CARD, col, 2)
        a.circle(300, 92, 9, AMB, None)
    elif key == "hesse-tsao-rapid-alternation":   # one steady view, but inside a fast flip between two images
        a.circle(140, 120, 34, IND_SOFT, IND)
        a.poly([(426, 150), (460, 86), (494, 150)], CARD, INK)
        for i in range(18):
            x = 70 + i * 26
            seen = i % 2 == 0
            a.rect(x, 230, 22, 46, IND if seen else CARD, 4, IND if seen else MUTE, 1.8)
        a.line([(70, 300), (540, 300)], INK, 2)
        a.circle(176, 98, 7, AMB, None)
    elif key == "owen-goodale-grand-theories":   # a big dashed outline overhead; small solid steps on the ground
        a.dashed([(150 + 120 * math.cos(t / 40 * 2 * math.pi), 130 + 70 * math.sin(t / 40 * 2 * math.pi)) for t in range(41)], MUTE, 2.4)
        for i in range(5):
            a.rect(170 + i * 50, 300 - (i + 1) * 30, 50, (i + 1) * 30, CARD, 2, INK, 2.2)
        a.person(450, 196, 1.3, IND, IND_SOFT)
        a.line([(80, 300), (540, 300)], INK, 2)
        a.circle(395, 128, 8, AMB, None)
    elif key == "overgaard-theory-method-dependencies":   # experiments clustered in separate corners
        r = random.Random(14)
        for (cx, cy, col, fill) in ((150, 130, IND, IND), (440, 120, INK, CARD), (300, 280, IND, IND_SOFT)):
            for _ in range(22):
                a.circle(cx + r.gauss(0, 30), cy + r.gauss(0, 22), 5, fill, col, 1.6)
        a.dashed([(300, 60), (300, 210)], MUTE, 1.8)
        a.dashed([(80, 210), (520, 210)], MUTE, 1.8)
        a.circle(520, 70, 8, AMB, None)
    elif key == "gurnee-jacobian-lens-workspace":   # a stack of layers; the middle band broadcasts outward
        for i in range(9):
            y = 60 + i * 30
            mid = 3 <= i <= 5
            a.rect(110, y, 190, 20, IND if mid else CARD, 5, IND if mid else MUTE, 2)
        for k, y in enumerate((90, 160, 230, 300)):
            a.arrow(310, 180, 430, y, IND, 2.4)
            a.rect(440, y - 18, 70, 36, CARD, 8, INK, 2)
        a.circle(205, 180, 7, AMB, None)


ALT = {
    "onoda-local-phi-nrem": "Four filled squares all joined by lines above dense rows of spike ticks, an arrow, then the same four squares pale and barely joined above sparse ticks.",
    "zhou-alpha-coherence-doc-recovery": "Two schematic brains: on the left, four pale dots at the back barely linked; on the right, the same four dots filled and all joined, under a small even wave.",
    "rochas-n2-dreaming-hdeeg": "A schematic brain with small fast waves at the back and a slow wave at the front, beside a thought bubble holding lines of text-like strokes.",
    "selte-nrem-experience-hdeeg": "Rows of dots, about half filled in, beside a curve that rises well above a dashed diagonal.",
    "stoliker-psilocybin-context-ds006110": "Four panels showing rest, meditation, music and a film, with one looping path running through them.",
    "berjaga-buisan-fdt-nonequilibrium": "A sawtooth trace with an arrow pointing forward in time, and a balance tipped to one side.",
    "congyu-neural-field-doc": "A schematic brain with a loop from a small inner circle to the cortex, beside pairs of traces that almost overlap.",
    "nunez-waveform-morphology": "Two waves with the same rhythm: one smooth and even, one rising fast and falling slowly.",
    "gaglioti-structural-complexity": "Three rings of nodes: neatly linked, linked with two shortcuts, and randomly linked; the middle one is highlighted.",
    "hesse-tsao-rapid-alternation": "A circle and a triangle above a row of blocks that alternate between filled and empty.",
    "owen-goodale-grand-theories": "A large dashed outline floating above a small staircase of solid blocks and a standing figure.",
    "overgaard-theory-method-dependencies": "Three separate clusters of dots, each in its own corner of the page.",
    "gurnee-jacobian-lens-workspace": "A stack of nine layers with the middle three filled, sending arrows out to four boxes.",
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


# ------------------------------------------------------------------ one drawing per library topic
TOPICS = {
    "Theories tested": "A balance with a circle on one pan and a triangle on the other.",
    "Measuring consciousness": "A dial with its needle part-way round, above a recording trace.",
    "Sleep and dreams": "A crescent moon over a sleeping figure, with a small dream bubble.",
    "Drugs and anaesthesia": "A drip bag on a stand with a line running down to a quietening trace.",
    "AI": "A chip with pins on every side and a small network drawn inside.",
}


def topic_slug(t):
    return "".join(ch if ch.isalnum() else "-" for ch in t.lower()).strip("-").replace("--", "-")


def draw_topic(t, a):
    if t == "Theories tested":
        a.line([(300, 90), (300, 300)], INK, 3); a.line([(240, 300), (360, 300)], INK, 3)
        a.line([(160, 110), (440, 110)], INK, 3); a.circle(300, 100, 8, INK, None)
        for x in (160, 440):
            a.line([(x, 110), (x - 40, 190)], INK, 1.8); a.line([(x, 110), (x + 40, 190)], INK, 1.8)
            a.curve([(x - 50, 190), (x - 30, 214), (x + 30, 214), (x + 50, 190)], INK, 2.4)
        a.circle(160, 170, 18, IND_SOFT, IND)
        a.poly([(420, 186), (440, 150), (460, 186)], IND, None)
        a.circle(300, 100, 5, AMB, None)
    elif t == "Measuring consciousness":
        a.curve([(170, 230), (170, 90), (430, 90), (430, 230)], INK, 3)
        for k in range(9):
            ang = math.pi + k * math.pi / 8
            a.line([(300 + 118 * math.cos(ang), 230 + 118 * math.sin(ang)), (300 + 102 * math.cos(ang), 230 + 102 * math.sin(ang))], MUTE, 2)
        ang = math.pi + 0.62 * math.pi
        a.line([(300, 230), (300 + 96 * math.cos(ang), 230 + 96 * math.sin(ang))], IND, 4)
        a.circle(300, 230, 10, AMB, None)
        a.trace(100, 300, 400, noisy(16, 3), INK, 2.2)
    elif t == "Sleep and dreams":
        a.circle(470, 90, 40, AMB_SOFT, AMB)
        a.circle(492, 76, 36, PAPER, None)
        a.rect(90, 250, 420, 30, CARD, 10, INK)
        a.circle(150, 228, 22, IND_SOFT, IND)
        a.curve([(172, 236), (260, 210), (400, 214), (490, 248)], IND, 3)
        a.bubble(220, 90, 150, 80, CARD, INK, "left")
        a.circle(260, 130, 8, IND, None); a.lines(282, 122, 70, 2, MUTE, 16)
    elif t == "Drugs and anaesthesia":
        a.line([(170, 60), (170, 320)], INK, 3); a.line([(130, 320), (210, 320)], INK, 3)
        a.line([(170, 70), (230, 70)], INK, 3)
        a.rect(200, 80, 60, 90, IND_SOFT, 12, IND)
        a.rect(210, 120, 40, 40, IND, 8, None)
        a.curve([(230, 170), (230, 240), (300, 260), (330, 230)], INK, 2.2)
        a.circle(230, 186, 5, AMB, None)
        a.trace(330, 230, 200, lambda i: (22 - i * 0.09) * math.sin(i / 3.2), INK, 2.2)
    elif t == "AI":
        a.rect(200, 100, 200, 200, CARD, 16, INK)
        for k in range(5):
            o = 236 + k * 32          # pin positions along the top and bottom edges
            a.line([(o, 100), (o, 80)], INK, 2.4); a.line([(o, 300), (o, 320)], INK, 2.4)
            o = 136 + k * 32          # and along the left and right edges
            a.line([(200, o), (180, o)], INK, 2.4); a.line([(400, o), (420, o)], INK, 2.4)
        nodes = [(250, 150), (350, 150), (250, 250), (350, 250), (300, 200)]
        for i, p in enumerate(nodes):
            for q in nodes[i + 1:]:
                a.line([p, q], IND, 1.8)
        for p in nodes:
            a.circle(*p, 9, IND_SOFT, IND)
        a.circle(300, 200, 6, AMB, None)


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
    lib = SITE / "assets" / "library"
    lib.mkdir(parents=True, exist_ok=True)
    talt = {}
    for k, t in enumerate(TOPICS):
        a = Art(seed=100 + k)
        draw_topic(t, a)
        a.save(lib / f"{topic_slug(t)}.webp")
        talt[topic_slug(t)] = "Illustration: " + TOPICS[t]
    (lib / "alt.json").write_text(json.dumps(talt, indent=1))
    print(f"wrote {len(TOPICS)} topic drawings")


if __name__ == "__main__":
    main()
