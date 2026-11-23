"""Task #5 (redesigned): per-measure frozen cutoffs, wake vs N3 on Sleep-EDF, applied unchanged to HMC.

Every measure takes one preprocessed 30-s epoch x of shape (2, 3000) at 100 Hz: a frontal-central and a
central/parietal-occipital bipolar derivation (Sleep-EDF Fpz-Cz, Pz-Oz; HMC F4-C4, C4-O2). Single-channel
measures are averaged over the two channels. All measures are scale-free, so no per-subject normalisation is
needed (and none is allowed: that would use the test subject's labels).
See docs/prereg/2026-11-23_transfer5_rem_placement.md.
"""
import os
import sys

import antropy as ant
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lz_slope"))
import features as F  # noqa: E402  (preprocess, phase_surrogate, lz, spectral_exponent, band_powers, perm_entropy, psd)

# Sign convention: +1 means "higher value = wake side". Fixed in advance from the literature, then checked
# against the Sleep-EDF fit direction (the fit picks the sign; a mismatch is reported, not hidden).
MEASURES = ["exponent", "lz", "perm_entropy", "spectral_entropy", "rel_delta", "rel_alpha", "rel_beta",
            "dfa", "wsmi"]
PRIOR_SIGN = {"exponent": +1, "lz": +1, "perm_entropy": +1, "spectral_entropy": +1, "rel_delta": -1,
              "rel_alpha": +1, "rel_beta": +1, "dfa": -1, "wsmi": +1}
BASELINE_FEATS = ["exponent", "bp_delta", "bp_theta", "bp_alpha", "bp_sigma", "bp_beta", "bp_lowgamma"]


def spectral_entropy(x):
    f, p = F.psd(x)
    m = (f >= 1) & (f <= 40)
    q = p[:, m] / p[:, m].sum(1, keepdims=True)
    return float(np.mean(-(q * np.log2(q + 1e-20)).sum(1) / np.log2(m.sum())))


def dfa(x):
    return float(np.mean([ant.detrended_fluctuation(np.ascontiguousarray(c, dtype=np.float64)) for c in np.atleast_2d(x)]))


def wsmi(x, kappa=3, tau=4):
    """Weighted symbolic mutual information between the two channels (King et al. 2013 form):
    ordinal patterns of length kappa at lag tau; identical and opposite patterns get zero weight."""
    import itertools
    pats = list(itertools.permutations(range(kappa)))
    idx = {p: i for i, p in enumerate(pats)}
    n = x.shape[-1] - (kappa - 1) * tau
    sym = []
    for c in x[:2]:
        emb = np.stack([c[i * tau: i * tau + n] for i in range(kappa)], 1)
        sym.append(np.array([idx[tuple(np.argsort(r))] for r in emb]))
    k = len(pats)
    joint = np.zeros((k, k))
    np.add.at(joint, (sym[0], sym[1]), 1)
    joint /= joint.sum()
    pa, pb = joint.sum(1), joint.sum(0)
    w = np.ones((k, k))
    for i, p in enumerate(pats):
        w[i, i] = 0
        w[i, idx[tuple(reversed(p))]] = 0
    nz = joint > 0
    return float(np.sum((w * joint)[nz] * np.log2(joint[nz] / np.outer(pa, pb)[nz])))


def all_measures(x):
    """x: preprocessed (2, n). Returns the 9 measures plus the baseline's band powers."""
    bp = F.band_powers(x)
    out = {"exponent": F.spectral_exponent(x), "lz": F.lz(x), "perm_entropy": F.perm_entropy(x),
           "spectral_entropy": spectral_entropy(x), "rel_delta": bp["bp_delta"], "rel_alpha": bp["bp_alpha"],
           "rel_beta": bp["bp_beta"], "dfa": dfa(x), "wsmi": wsmi(x)}
    out.update(bp)
    return out


def epoch_rows(eeg, stage, subject, dataset, rng=None, surrogate=False):
    """eeg: (n_epochs, 2, n) raw, in microvolts, 100 Hz. Returns feature rows for clean epochs
    (peak-to-peak <= 500 uV and SD >= 1 uV on both channels, the lz_slope rule).
    surrogate=True replaces each epoch with one multichannel phase-randomised copy (spectrum and
    cross-spectrum kept)."""
    rows = []
    for i in range(eeg.shape[0]):
        x = F.preprocess(eeg[i])
        if np.ptp(x, axis=-1).max() > 500 or x.std(-1).min() < 1:
            continue
        if surrogate:
            x = F.phase_surrogate(x, rng)
        r = all_measures(x)
        r.update(subject=str(subject), stage=str(stage[i]), dataset=dataset, epoch=i)
        rows.append(r)
    return rows
