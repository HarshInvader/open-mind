"""Secondary replication data: ds005620 (propofol), Sleep-EDF-identical derivations Fpz-Cz and Pz-Oz.

Per subject (sub-1037 excluded, as in participants.tsv):
  awake : two 30-s epochs from the eyes-closed awake run, 130-190 s;
  sed2  : the last 30 s of each available sed2 run (1-3; RASS -4, the minute before an awakening attempt).
Range-reads only those stretches (reader from experiments/nonequilibrium/extract.py), resamples 5 kHz -> 100 Hz
(MNE, anti-aliased), and writes measure rows to ds005620_feats.jsonl. Run only after the prereg is sealed.
Untrusted data: only parsed, never executed.
"""
import json
import os
import sys

import mne
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "nonequilibrium"))
import extract as NE  # noqa: E402  (ds_list, get, S3, FS_DS)
import measures as M  # noqa: E402


def read(key, size, start_s, win_s):
    NE.WIN_S = win_s
    x = NE.ds_read(key, size, start_s)
    hdr = NE.get(f"{NE.S3}/{key[len('ds005620/'):].replace('_eeg.eeg', '_eeg.vhdr')}").decode("utf-8", "replace")
    names = [l.split("=", 1)[1].split(",")[0] for l in hdr.splitlines()
             if l.startswith("Ch") and "=" in l and l.split("=")[0][2:].isdigit()]
    ix = {n: i for i, n in enumerate(names)}
    missing = [c for c in ("Fpz", "Cz", "Pz", "Oz") if c not in ix]
    if missing:
        raise RuntimeError(f"channels missing from {key}: {missing}")
    d = np.stack([x[ix["Fpz"]] - x[ix["Cz"]], x[ix["Pz"]] - x[ix["Oz"]]])
    return mne.filter.resample(d, up=100.0 / NE.FS_DS, verbose=False)


def main():
    keys = NE.ds_list()
    subs = sorted({k.split("/")[1] for k in keys} - {"sub-1037"})
    out = open(os.path.join(HERE, "ds005620_feats.jsonl"), "w")
    log = []
    for sub in subs:
        ec = f"ds005620/{sub}/eeg/{sub}_task-awake_acq-EC_eeg.eeg"
        sed = [k for k in (f"ds005620/{sub}/eeg/{sub}_task-sed2_acq-rest_run-{r}_eeg.eeg" for r in (1, 2, 3)) if k in keys]
        if ec not in keys or not sed:
            log.append({"sub": sub, "skip": "missing files"}); continue
        try:
            eps, st = [], []
            a = read(ec, keys[ec], 130.0, 60)
            eps += [a[:, :3000], a[:, 3000:6000]]; st += ["awake", "awake"]
            for k in sed:
                eps.append(read(k, keys[k], 1e9, 30)[:, :3000]); st.append("sed2")
            rows = M.epoch_rows(np.array(eps), np.array(st), sub, "ds005620")
            for r in rows:
                out.write(json.dumps(r) + "\n")
            out.flush()
            log.append({"sub": sub, "clean": {s: sum(r["stage"] == s for r in rows) for s in ("awake", "sed2")}})
        except Exception as e:  # unreadable files are skipped and listed; a channel problem stops the run
            if isinstance(e, RuntimeError) and "channels missing" in str(e):
                raise
            log.append({"sub": sub, "skip": repr(e)[:160]})
        print(json.dumps(log[-1]), flush=True)
    json.dump(log, open(os.path.join(HERE, "ds005620_log.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
