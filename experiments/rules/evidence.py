"""Open Mind rules-of-evidence toolkit (task #1).

Import from any experiment:

    import sys; sys.path.insert(0, "experiments/rules")
    from evidence import (seal, require_sealed, Recording, subject_folds,
                          check_split, LeakageError, ledger_rows_write,
                          perm_auc_within_subject)

Pieces
------
1. Sealing: `seal(paths)` appends sha256 + UTC time to docs/prereg/HASHES.txt
   (append only). `require_sealed(path)` raises unless the file's current hash
   was sealed, so an edited pre-registration is caught.
2. Splits: every recording carries subject, lab and dataset. `subject_folds`
   makes folds grouped by subject (never by epoch). In "transfer" mode the
   group is the lab, because same-lab data counts as a near-copy.
3. Leak check: `check_split(train, test, mode)` raises LeakageError if
   (a) a subject is on both sides, (b) the same signal appears on both sides
   under different IDs (content fingerprint), or (c) in transfer mode a lab is
   on both sides.
4. Ledger: fixed column list `LEDGER_COLUMNS`; `ledger_rows_write` validates.
5. Nulls: `perm_auc_within_subject` permutes state labels within subject.
"""
from __future__ import annotations

import csv
import datetime as _dt
import hashlib
import os
from dataclasses import dataclass, field
from typing import Iterable, Sequence

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HASHES = os.path.join(REPO, "docs", "prereg", "HASHES.txt")

# Columns follow the Open Indus ledger, with `distinct_text_unit` replaced by
# `distinct_subjects` and a `ground_truth` column (behaviour / delayed_report /
# none / synthetic) added per AGENT_BRIEF rule 6.
LEDGER_COLUMNS = [
    "id", "claim", "area", "file", "statistic", "p_value", "p_source", "ci",
    "n", "distinct_subjects", "split", "mode", "family", "family_size",
    "replicated_independently", "readme_claim", "ground_truth",
    "q_global", "q_area", "q_hier", "q_all", "note",
]
SPLITS = {"subject", "lab", "dataset", "none", "synthetic"}
MODES = {"confirmatory", "exploratory", "method_check"}
GROUND_TRUTH = {"behaviour", "delayed_report", "none", "synthetic"}


# ---------------------------------------------------------------- sealing
def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _rel(path: str) -> str:
    return os.path.relpath(os.path.abspath(path), REPO)


def seal(paths: Iterable[str], hashes_file: str = HASHES) -> list[str]:
    """Append `sha256  relpath  UTC-time` lines. Never rewrites the file."""
    now = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [f"{sha256_file(p)}  {_rel(p)}  {now}" for p in paths]
    with open(hashes_file, "a") as f:
        for ln in lines:
            f.write(ln + "\n")
    return lines


def sealed_entries(hashes_file: str = HASHES) -> list[tuple[str, str, str]]:
    out = []
    if not os.path.exists(hashes_file):
        return out
    for ln in open(hashes_file):
        parts = ln.split()
        if len(parts) >= 2 and len(parts[0]) == 64:
            out.append((parts[0], parts[1], parts[2] if len(parts) > 2 else ""))
    return out


class SealError(RuntimeError):
    pass


def require_sealed(path: str, hashes_file: str = HASHES) -> str:
    """Return the seal time if the file's CURRENT hash is sealed, else raise."""
    h, rel = sha256_file(path), _rel(path)
    hits = [t for (hh, p, t) in sealed_entries(hashes_file) if hh == h and p == rel]
    if not hits:
        known = [p for (_, p, _) in sealed_entries(hashes_file) if p == rel]
        why = "edited after sealing" if known else "never sealed"
        raise SealError(f"{rel}: {why} (sha256 {h[:12]}...)")
    return hits[0]


# ---------------------------------------------------------------- splits
class LeakageError(RuntimeError):
    pass


@dataclass
class Recording:
    """One recording (or one epoch; epochs share their recording's ids)."""
    rec_id: str
    subject: str
    lab: str
    dataset: str
    fingerprint: str = ""          # content hash; see `fingerprint()`
    meta: dict = field(default_factory=dict)


def fingerprint(x: np.ndarray, n: int = 4096, decimals: int = 3) -> str:
    """Content hash of a signal, robust to dtype and scaling.

    The signal is z-scored per channel and rounded, so a copy saved as float32
    vs float64, or rescaled (V vs uV), gets the same fingerprint. Use the
    whole recording (or its first `n` samples per channel).
    """
    a = np.atleast_2d(np.asarray(x, dtype=np.float64))[:, :n]
    a = (a - a.mean(1, keepdims=True)) / (a.std(1, keepdims=True) + 1e-12)
    return hashlib.sha256(np.round(a, decimals).tobytes()).hexdigest()[:16]


def _group_key(r: Recording, mode: str) -> str:
    if mode == "within":
        return f"{r.dataset}:{r.subject}"
    if mode == "transfer":
        return f"lab:{r.lab}"
    raise ValueError(mode)


def subject_folds(recs: Sequence[Recording], k: int = 5, mode: str = "within",
                  seed: int = 0) -> list[tuple[np.ndarray, np.ndarray]]:
    """Index folds grouped by subject (mode='within') or by lab ('transfer').

    Recordings with the same fingerprint are merged into one group too, so a
    subject re-uploaded under a new ID cannot straddle a fold.
    """
    keys = [_group_key(r, mode) for r in recs]
    # union-find: same group key or same fingerprint -> same group
    parent = list(range(len(recs)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    first: dict[str, int] = {}
    for i, r in enumerate(recs):
        for tag in (keys[i], ("fp:" + r.fingerprint) if r.fingerprint else None):
            if tag is None:
                continue
            if tag in first:
                parent[find(i)] = find(first[tag])
            else:
                first[tag] = i
    roots = np.array([find(i) for i in range(len(recs))])
    groups = np.unique(roots)
    rng = np.random.default_rng(seed)
    rng.shuffle(groups)
    k = min(k, len(groups))
    folds = []
    for j in range(k):
        test_groups = set(groups[j::k].tolist())
        test = np.array([i for i in range(len(recs)) if roots[i] in test_groups])
        train = np.array([i for i in range(len(recs)) if roots[i] not in test_groups])
        folds.append((train, test))
    return folds


def check_split(train: Sequence[Recording], test: Sequence[Recording],
                mode: str = "within") -> dict:
    """Raise LeakageError on any leak; return a summary dict if clean.

    within:   no subject (per dataset) on both sides; no shared fingerprint.
    transfer: additionally no lab on both sides (same lab = near-copy).
    """
    problems = []
    s_tr = {(r.dataset, r.subject) for r in train}
    s_te = {(r.dataset, r.subject) for r in test}
    both = s_tr & s_te
    if both:
        problems.append(f"{len(both)} subject(s) on both sides, e.g. {sorted(both)[:3]}")
    f_tr = {r.fingerprint: r for r in train if r.fingerprint}
    dup = [(f_tr[r.fingerprint].rec_id, r.rec_id) for r in test
           if r.fingerprint and r.fingerprint in f_tr]
    if dup:
        problems.append(f"{len(dup)} identical signal(s) under different ids, e.g. {dup[:3]}")
    if mode == "transfer":
        labs = {r.lab for r in train} & {r.lab for r in test}
        if labs:
            problems.append(f"lab(s) on both sides of a transfer split (near-copy): {sorted(labs)}")
    elif mode != "within":
        raise ValueError(mode)
    if problems:
        raise LeakageError("; ".join(problems))
    return {"n_train": len(train), "n_test": len(test),
            "train_subjects": len(s_tr), "test_subjects": len(s_te), "mode": mode}


# ---------------------------------------------------------------- ledger
def ledger_rows_write(path: str, rows: list[dict]) -> None:
    for r in rows:
        extra = set(r) - set(LEDGER_COLUMNS)
        if extra:
            raise ValueError(f"unknown ledger columns {extra}")
        for col in ("id", "claim", "area", "file", "statistic", "split", "mode"):
            if not str(r.get(col, "")).strip():
                raise ValueError(f"row {r.get('id')}: missing {col}")
        if r["split"] not in SPLITS:
            raise ValueError(f"row {r['id']}: split must be one of {SPLITS}")
        if r["mode"] not in MODES:
            raise ValueError(f"row {r['id']}: mode must be one of {MODES}")
        if r.get("ground_truth", "") not in GROUND_TRUTH:
            raise ValueError(f"row {r['id']}: ground_truth must be one of {GROUND_TRUTH}")
        if r["mode"] == "confirmatory" and r["split"] in ("none",):
            raise ValueError(f"row {r['id']}: confirmatory test needs a held-out split")
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in LEDGER_COLUMNS})


# ---------------------------------------------------------------- nulls
def auc(scores: np.ndarray, labels: np.ndarray) -> float:
    """Mann-Whitney AUC, labels in {0,1}; ties count half."""
    from scipy.stats import rankdata
    s, y = np.asarray(scores, float), np.asarray(labels, int)
    r = rankdata(s)
    n1, n0 = y.sum(), (1 - y).sum()
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def perm_auc_within_subject(scores, labels, groups, n_perm=2000, seed=0,
                            stat=None):
    """Two-sided-in-direction p for |AUC-0.5|, permuting labels within groups.

    `stat(scores, labels)` defaults to AUC. Returns (observed, p, null array).
    """
    stat = stat or auc
    rng = np.random.default_rng(seed)
    scores, labels, groups = map(np.asarray, (scores, labels, groups))
    obs = stat(scores, labels)
    idx = [np.flatnonzero(groups == g) for g in np.unique(groups)]
    null = np.empty(n_perm)
    for b in range(n_perm):
        y = labels.copy()
        for ii in idx:
            y[ii] = labels[rng.permutation(ii)]
        null[b] = stat(scores, y)
    p = (1 + np.sum(np.abs(null - 0.5) >= abs(obs - 0.5))) / (n_perm + 1)
    return obs, float(p), null


if __name__ == "__main__":
    # CLI: .venv/bin/python -I experiments/rules/evidence.py seal FILE [FILE...]
    #      .venv/bin/python -I experiments/rules/evidence.py check FILE
    import sys as _sys
    cmd, files = _sys.argv[1], _sys.argv[2:]
    if cmd == "seal":
        for ln in seal(files):
            print(ln)
    elif cmd == "check":
        for p in files:
            print(p, "sealed at", require_sealed(p))
    else:
        raise SystemExit("usage: evidence.py seal|check FILE...")
