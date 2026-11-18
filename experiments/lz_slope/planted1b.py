"""P1b (amendment 2 of the #4 prereg): plant a known spectral tilt into real wake epochs.

Streams the included subjects' clean W epochs again from PhysioNet S3 (range
requests), plants the tilt in memory, computes the measures, discards the raw data.
Nothing raw is written to disk. Output: planted1b.json
"""
import json, os, re, sys, urllib.request
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fetch as F                                   # reuse header parser + range getter
from features import preprocess, spectral_exponent, lz, FS
from analyse import load, CV

BETAS = (0, 0.25, 0.5, 1.0)


def tilt(x, beta):
    """Steepen the spectral exponent by `beta` (amplitude x f^(-beta/2)), RMS kept per channel."""
    n = x.shape[-1]
    X = np.fft.rfft(x, axis=-1)
    f = np.fft.rfftfreq(n, 1 / FS)
    g = np.ones_like(f); g[1:] = f[1:] ** (-beta / 2)
    y = np.fft.irfft(X * g[None, :], n=n, axis=-1)
    return y * (x.std(-1, keepdims=True) / (y.std(-1, keepdims=True) + 1e-12))


def main():
    df = load()
    w = df[df.stage == "W"][["rec", "subject", "epoch"]]
    recs_txt = urllib.request.urlopen(F.INDEX.replace("sleep-cassette/", "RECORDS"), timeout=60).read().decode()
    psg = {p[:6]: p for p in re.findall(r"(SC4\d{3}[A-Z]0)-PSG\.edf", recs_txt)}
    rows = []
    for rec, g in w.groupby("rec"):
        path = F.BASE + psg[rec] + "-PSG.edf"
        h = F.parse_header(F.get_range(path, 0, 4095))
        kk = int(round(h["rec_dur"] / 30)); spr = h["spr"]; rb = 2 * sum(spr)
        offs = np.concatenate([[0], np.cumsum(spr)])
        ii = [h["labels"].index("EEG Fpz-Cz"), h["labels"].index("EEG Pz-Oz")]
        for subj, e in zip(g.subject, g.epoch):
            st0 = h["hdr_bytes"] + (int(e) // kk) * rb; sub = int(e) % kk
            raw = np.frombuffer(F.get_range(path, st0, st0 + rb - 1), "<i2")
            chans = []
            for i in ii:
                n30 = spr[i] // kk
                dig = raw[offs[i] + sub * n30: offs[i] + (sub + 1) * n30].astype(float)
                gn = (h["pmax"][i] - h["pmin"][i]) / (h["dmax"][i] - h["dmin"][i])
                chans.append((dig - h["dmin"][i]) * gn + h["pmin"][i])
            x = preprocess(np.array(chans))
            r = {"subject": subj}
            for b in BETAS:
                y = tilt(x, b)
                r[f"slope_{b}"], r[f"lz_{b}"] = spectral_exponent(y), lz(y)
            rows.append(r)
        print(rec, len(g), flush=True)
    p = pd.DataFrame(rows)
    out = {"n_epochs": len(p), "n_subjects": int(p.subject.nunique())}
    for m in ("slope", "lz"):
        for b in BETAS:
            dd = pd.concat([pd.DataFrame({"subject": p.subject, "stage": "P", "f": p[f"{m}_{b}"]}),
                            pd.DataFrame({"subject": p.subject, "stage": "O", "f": p[f"{m}_0"]})], ignore_index=True)
            out[f"{m}_auc_beta{b}"] = CV(dd, "O", "P").auc(dd[["f"]].values)
        out[f"{m}_mean_shift_beta1"] = float((p[f"{m}_1.0"] - p[f"{m}_0"]).mean())
    v = [out[f"slope_auc_beta{b}"] for b in BETAS]
    out["PASS"] = bool(abs(v[0] - 0.5) < 0.05 and v[-1] > 0.8 and all(np.diff(v) > 0))
    json.dump(out, open(os.path.join(HERE, "planted1b.json"), "w"), indent=1)
    print(out)


if __name__ == "__main__":
    main()
