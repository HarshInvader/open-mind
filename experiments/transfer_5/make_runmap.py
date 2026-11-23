"""Label-free run map for the ds005620 report-calibration test (task #5b). Run before any report labels arrive.

extract_ds.py appended sed2 epochs in run order (run-1, run-2, run-3, skipping runs absent from the release), after
two awake epochs (indices 0, 1). This rebuilds which sed2 run each clean epoch came from, from the public S3 key
list (metadata only), and records the frozen Sleep-EDF exponent and baseline calls for each clean run.
Writes ds005620_runmap.json.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse as A  # noqa: E402  (this folder's analyse.py, imported before the path change)
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("ne_extract", os.path.join(HERE, "..", "nonequilibrium", "extract.py"))
NE = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(NE)


def main():
    keys = NE.ds_list()
    cut = A.fit(A.load("sedf_wn"))
    rows = [json.loads(l) for l in open(os.path.join(HERE, "ds005620_feats.jsonl"))]
    out = {"cutoff_exponent": cut["exponent"], "runs": [], "available_sed2": {}}
    subs = sorted({r["subject"] for r in rows})
    for sub in subs:
        runs = [r for r in (1, 2, 3) if f"ds005620/{sub}/eeg/{sub}_task-sed2_acq-rest_run-{r}_eeg.eeg" in keys]
        out["available_sed2"][sub] = runs
    sed = [r for r in rows if r["stage"] == "sed2"]
    ws_e = A.wake_side(sed, cut, "exponent")
    ws_b = A.wake_side(sed, cut, "baseline")
    for r, we, wb in zip(sed, ws_e, ws_b):
        runs = out["available_sed2"][r["subject"]]
        k = r["epoch"] - 2
        assert 0 <= k < len(runs), (r["subject"], r["epoch"], runs)
        out["runs"].append(dict(subject=r["subject"], run=runs[k], exponent=r["exponent"],
                                exponent_wake_side=bool(we), baseline_wake_side=bool(wb)))
    out["n_clean_runs"] = len(out["runs"])
    out["n_exponent_n3_side"] = int(sum(not x["exponent_wake_side"] for x in out["runs"]))
    json.dump(out, open(os.path.join(HERE, "ds005620_runmap.json"), "w"), indent=1)
    print(out["n_clean_runs"], "clean runs;", out["n_exponent_n3_side"], "exponent N3-side")


if __name__ == "__main__":
    main()
