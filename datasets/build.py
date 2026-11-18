"""Build datasets/open/ (this project's own tables) and check datasets/catalog.csv.

    python3 -I datasets/build.py

Rules:
- open/ holds only tables this project made, copied from experiments/ (CC BY 4.0). Nothing third-party in bulk: the DREAM
  index tables (Datasets.csv, Data records.csv) stay out, and so does anything with an email address or a local path.
  `datasets/fetch.py fetch dream_index` gets the DREAM index on your machine.
- catalog.csv is written by hand. It lists every open or requestable dataset relevant to the project, used or not.
  This script checks its columns and values, refuses emails and local paths, and checks that every open/ file has an
  `included` row and the other way round.
"""
import csv, json, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "datasets"
OPEN = HERE / "open"
COLS = "id,title,kind,tier,origin,terms,size,n,labels,serves_tasks,used_by_us,verified,notes".split(",")
TIERS = ("included", "fetch", "request", "reference-only")
BAD = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|/Users/|/home/")

# (source, published name, description)
OPEN_TABLES = [
    ("experiments/ground_truth/labels.csv", "ground_truth_labels.csv", "One row per open recording or awakening: dataset, lab, subject, stage, behaviour, report and kind of ground truth"),
    ("experiments/ground_truth/counts.json", "ground_truth_counts.json", "Counts behind the data figures: recordings by dataset and label kind, report-labelled awakenings by stage and lab"),
    ("experiments/data_access/dream_access.csv", "dream_access.csv", "Each DREAM package: live access check, licence, size and experience / no-experience counts by stage"),
    ("experiments/dataset_audit/dream_sets.csv", "dream_sets.csv", "Per DREAM set: awakenings, subjects, report counts, sample rate, channels, size and licence"),
    ("experiments/*/ledger_rows.csv", "bench_ledger.csv", "One row per test from every experiment, with an `experiment` column"),
    ("experiments/lz_slope/results.json", "lz_slope_results.json", "LZ complexity vs aperiodic slope across Sleep-EDF, ds005620 and Chennu: AUCs and CIs"),
    ("experiments/t1_dream/features.csv", "t1_dream_features.csv", "Tononi serial awakenings: per-awakening delta, sigma, beta power and exponent before waking, with report label"),
    ("experiments/t1_dream/subject_counts_realised.csv", "t1_dream_subject_counts.csv", "Tononi set: experience / no experience / without recall per subject, as analysed"),
    ("experiments/theory_tests/scoreboard.csv", "theory_tests_scoreboard.csv", "Pre-registered theory predictions on DREAM and Chennu data: statistic, CI, verdict, prereg hash"),
    ("experiments/theory_tests/results.json", "theory_tests_results.json", "Full results of the theory tests"),
    ("experiments/theory_scorecard/scorecard.csv", "theory_scorecard.csv", "Each theory x constraint: mark, points and reason"),
    ("experiments/theory_scorecard/totals.csv", "theory_scorecard_totals.csv", "Totals per theory: explains, compatible, silent, strained, contradicts"),
    ("experiments/theory_scorecard/gaps.csv", "theory_scorecard_gaps.csv", "Constraints no theory explains"),
    ("experiments/constraint_ledger/ledger.csv", "constraint_ledger.csv", "The constraints any theory must meet, with evidence grade and sources"),
    ("experiments/our_theory/coverage.csv", "our_theory_coverage.csv", "Our candidate theory against each constraint, two drafts"),
    ("experiments/blind_scoring/marks.csv", "blind_scoring_marks.csv", "Blind re-marks of theory x constraint cells"),
]


def rows_of(f):
    return list(csv.DictReader(f))


def copy_table(src, name):
    """Copy one table into open/. Returns (rows, columns)."""
    out = OPEN / name
    if "*" in src:  # concatenate ledgers
        rows, cols = [], ["experiment"]
        for p in sorted(ROOT.glob(src)):
            for r in rows_of(open(p, newline="", encoding="utf-8")):
                r = {"experiment": p.parent.name, **r}
                cols += [c for c in r if c not in cols]
                rows.append(r)
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
        return len(rows), len(cols)
    p = ROOT / src
    shutil.copy2(p, out)
    if p.suffix == ".csv":
        rows = rows_of(open(p, newline="", encoding="utf-8"))
        return len(rows), len(rows[0]) if rows else 0
    j = json.load(open(p, encoding="utf-8"))
    return (len(j) if isinstance(j, list) else ""), (len(j) if isinstance(j, dict) else "")


def build_open():
    if OPEN.exists():
        shutil.rmtree(OPEN)
    OPEN.mkdir(parents=True)
    man = []
    for src, name, desc in OPEN_TABLES:
        if "*" not in src and not (ROOT / src).exists():
            print("missing", src); continue
        n, cols = copy_table(src, name)
        if BAD.search((OPEN / name).read_text(encoding="utf-8")):
            sys.exit(f"{name}: contains an email address or a local path; fix the source before publishing")
        man.append(dict(file=name, rows=n, columns=cols, description=desc, made_by=src))
    with open(OPEN / "MANIFEST.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(man[0].keys())); w.writeheader(); w.writerows(man)
    return man


def check_catalog(man):
    p = HERE / "catalog.csv"
    rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
    head = next(csv.reader(open(p, newline="", encoding="utf-8")))
    errs = []
    if head != COLS:
        errs.append(f"columns are {head}, want {COLS}")
    ids = [r["id"] for r in rows]
    errs += [f"duplicate id {i}" for i in sorted({i for i in ids if ids.count(i) > 1})]
    for r in rows:
        if r["tier"] not in TIERS:
            errs.append(f"{r['id']}: tier {r['tier']!r}")
        if r["used_by_us"] not in ("yes", "no") or r["verified"] not in ("yes", "no"):
            errs.append(f"{r['id']}: used_by_us/verified must be yes or no")
        if not r["origin"] and r["verified"] == "yes":
            errs.append(f"{r['id']}: verified rows need an origin")
        if r["verified"] == "yes" and r["tier"] != "included" and "checked 20" not in r["notes"] and "read 20" not in r["notes"] \
                and "opened 20" not in r["notes"] and "(2026-11-18)" not in r["notes"]:
            errs.append(f"{r['id']}: verified rows say how they were checked")
        if any(BAD.search(v or "") for v in r.values()):
            errs.append(f"{r['id']}: email address or local path")
    included = {r["origin"].split("/")[-1] for r in rows if r["tier"] == "included"}
    errs += [f"open/{m['file']} has no included row" for m in man if m["file"] not in included]
    errs += [f"included row for {f} has no file in open/" for f in included if not (OPEN / f).exists()]
    if errs:
        sys.exit("catalog.csv:\n  " + "\n  ".join(errs))
    by = {t: sum(r["tier"] == t for r in rows) for t in TIERS}
    ver = sum(r["verified"] == "yes" for r in rows)
    used = sum(r["used_by_us"] == "yes" for r in rows)
    print(f"catalog.csv: {len(rows)} rows; " + ", ".join(f"{v} {k}" for k, v in by.items()) + f"; {ver} verified, {len(rows) - ver} not; {used} used by us")


if __name__ == "__main__":
    man = build_open()
    print(f"open/: {len(man)} tables written, MANIFEST.csv updated")
    check_catalog(man)
