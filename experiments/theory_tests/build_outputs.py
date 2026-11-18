"""Write scoreboard.csv, results.json and ledger_rows.csv from dream_results.json and chennu_results.json."""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "experiments", "rules"))
from evidence import ledger_rows_write, sha256_file  # noqa: E402

PR = {k: os.path.join(REPO, "docs", "prereg", f"2026-11-18_theory_{k}.md")
      for k in ("iit_posterior_dream", "gnwt_frontal_dream", "entropic_propofol")}
H = {k: sha256_file(v) for k, v in PR.items()}
d = json.load(open(os.path.join(HERE, "dream_results.json")))
c = json.load(open(os.path.join(HERE, "chennu_results.json")))
pl = json.load(open(os.path.join(HERE, "planted_dream.json")))


def f(x, k=3):
    return f"{x:.{k}f}"


DREAM = "DREAM Zhang&Wamsley2019 + DeGennaro_YoungAdults, N2 awakenings"
n_d = f"{d['n']} awakenings ({d['n_exp']} exp / {d['n_noexp']} no-exp), {d['n_subjects']} subjects, 2 labs"
rows = [
    dict(theory="IIT 4.0", prediction="Lower posterior (P3 Pz P4 O1 O2) 1-4 Hz power before experience vs no experience in N2; larger than frontal; adds over 1-30 Hz exponent",
         dataset=DREAM, n=n_d,
         statistic=f"AUC {f(d['posterior']['auc'])} (perm p {f(d['posterior']['p_one_sided'])}); post-front dAUC {f(d['dAUC_post_minus_front']['value'])}; held-out dAUC over exponent {f(d['H3_posterior']['dAUC'])}",
         CI=f"AUC [{f(d['posterior']['ci95'][0])}, {f(d['posterior']['ci95'][1])}]; post-front [{f(d['dAUC_post_minus_front']['ci95'][0])}, {f(d['dAUC_post_minus_front']['ci95'][1])}]; held-out dAUC [{f(d['H3_posterior']['ci95'][0])}, {f(d['H3_posterior']['ci95'][1])}]",
         verdict=d["verdict_IIT"] + f" (detectable AUC about 0.66-0.70 at 80% power; planted a=0.75 gave power {pl['posterior_a0.75']['power_at_0.025']:.2f} at mean AUC {pl['posterior_a0.75']['mean_auc']:.2f})",
         prereg_hash=H["iit_posterior_dream"]),
    dict(theory="GNWT", prediction="Lower frontal (F3 Fz F4) 1-4 Hz power before experience vs no experience in N2; adds over 1-30 Hz exponent",
         dataset=DREAM, n=n_d,
         statistic=f"AUC {f(d['frontal']['auc'])} (perm p {f(d['frontal']['p_one_sided'])}, alpha 0.025); held-out dAUC over exponent {f(d['H3_frontal']['dAUC'])}",
         CI=f"AUC [{f(d['frontal']['ci95'][0])}, {f(d['frontal']['ci95'][1])}]; held-out dAUC [{f(d['H3_frontal']['ci95'][0])}, {f(d['H3_frontal']['ci95'][1])}]",
         verdict=d["verdict_GNWT"] + f" (detectable AUC about 0.66 at 87% power; planted frontal a=0.75 mean AUC {pl['frontal_a0.75']['mean_auc']:.2f})",
         prereg_hash=H["gnwt_frontal_dream"]),
    dict(theory="Entropic brain", prediction="Phase-normalised LZ (spectrum-matched) lower at moderate propofol than baseline, within subject",
         dataset="Chennu 2016 propofol (Cambridge), first 120 s of baseline and moderate", n=f"{c['subjects']} subjects",
         statistic=f"median paired pnLZ diff {c['pnlz']['median_diff']:.4f} (Wilcoxon p {f(c['pnlz']['wilcoxon_p_less'])}, d_z {c['pnlz']['d_z']:.2f}); raw LZ diff {c['lz']['median_diff']:.4f} (p {f(c['lz']['wilcoxon_p_less'])})",
         CI=f"pnLZ diff [{c['pnlz']['ci95'][0]:.4f}, {c['pnlz']['ci95'][1]:.4f}]; LZ diff [{c['lz']['ci95'][0]:.4f}, {c['lz']['ci95'][1]:.4f}]",
         verdict=("no verdict on the primary (pnLZ) test: uninformative, because pnLZ could not tell real baseline EEG from its own spectrum-matched surrogate (planted check P1, p "
                  + f"{c['planted']['P1_p']:.2f}" + "). Secondary H1, raw LZ lower under propofol: FAILED this test in the opposite direction, LZ rose "
                  + f"{c['lz']['median_diff']:.3f} (d_z {c['lz']['d_z']:.2f}, p {c['lz']['wilcoxon_p_greater']:.4f} two-sided-direction), and surrogate LZ rose as much ("
                  + f"{c['lz_surr']['median_diff']:.3f}), so the change is spectral. Detectable paired d_z about 0.58 at 80% power."),
         prereg_hash=H["entropic_propofol"]),
]
NOT = [
    ("Higher-order theories", "PFC activity tracks awareness/confidence when task performance is matched (Lau & Passingham-type relative blindsight)",
     "not testable on reachable data: no open sleep/sedation set has confidence or awareness ratings with matched performance. Needs: open EEG/MEG with trial-wise awareness + confidence at matched d' (or COGITATE with an account). The frontal dream test above is shared context only."),
    ("Recurrent processing (RPT)", "Phenomenal experience with local recurrent (feedback) activity in sensory cortex without report; loss of recurrence (not feedforward) removes experience",
     "not testable on reachable data: needs stimulus-evoked EEG/iEEG (masking or figure-ground, with a no-report condition) across states. Resting EEG cannot isolate stimulus-locked recurrence. Needs COGITATE iEEG (account) or an open visual masking/figure-ground set under sedation."),
    ("Predictive processing", "Mismatch/prediction-error responses (MMN, local-global) change with conscious state in a specified direction; top-down predictions lost first",
     "not testable on reachable data: no open auditory oddball or local-global EEG across sleep or sedation found (OpenNeuro ds005429 local-global is awake only). Needs an open local-global or roving-MMN set under propofol or sleep with delayed report."),
    ("Attention schema", "Awareness tracks the brain's model of its own attention; awareness and attention control dissociate when the schema is disrupted",
     "not testable on reachable data: needs an attention-cueing paradigm with trial-wise awareness reports (e.g. Webb/Graziano designs) with EEG; none in docs/DATASETS.md. Resting or sleep data have no attention manipulation."),
]
for th, pred, why in NOT:
    rows.append(dict(theory=th, prediction=pred, dataset="none reachable", n="", statistic="", CI="",
                     verdict=why, prereg_hash=""))
cols = ["theory", "prediction", "dataset", "n", "statistic", "CI", "verdict", "prereg_hash"]
with open(os.path.join(HERE, "scoreboard.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)

json.dump({"task": 16, "agent": "mind-3", "dream": d, "chennu": c, "planted_dream": pl,
           "exploratory_dream_split": json.load(open(os.path.join(HERE, "dream_exploratory_split.json"))),
           "prereg_sha256": H, "scoreboard": rows}, open(os.path.join(HERE, "results.json"), "w"), indent=1)

L = [
    dict(id="T16-IIT-H1", claim="posterior delta lower before N2 experience (IIT hot zone)", area="theory_tests",
         file="experiments/theory_tests/dream_results.json", statistic=f"AUC {f(d['posterior']['auc'])}",
         p_value=f(d["posterior"]["p_one_sided"], 4), p_source="permutation within dataset, 5000",
         ci=str(d["posterior"]["ci95"]), n=str(d["n"]), distinct_subjects=str(d["n_subjects"]), split="subject",
         mode="confirmatory", family="T16-dream", family_size="2", replicated_independently="no",
         readme_claim="no", ground_truth="delayed_report", note=d["verdict_IIT"]),
    dict(id="T16-IIT-H2", claim="posterior effect larger than frontal", area="theory_tests",
         file="experiments/theory_tests/dream_results.json", statistic=f"dAUC {f(d['dAUC_post_minus_front']['value'])}",
         p_value="", p_source="subject-cluster bootstrap CI", ci=str(d["dAUC_post_minus_front"]["ci95"]),
         n=str(d["n"]), distinct_subjects=str(d["n_subjects"]), split="subject", mode="confirmatory",
         family="T16-dream", family_size="2", replicated_independently="no", readme_claim="no",
         ground_truth="delayed_report", note="CI includes 0; point estimate favours frontal"),
    dict(id="T16-IIT-H3", claim="posterior delta adds over 1-30 Hz exponent, subject-held-out", area="theory_tests",
         file="experiments/theory_tests/dream_results.json", statistic=f"dAUC {f(d['H3_posterior']['dAUC'])}",
         p_value="", p_source="subject-cluster bootstrap CI", ci=str(d["H3_posterior"]["ci95"]),
         n=str(d["n"]), distinct_subjects=str(d["n_subjects"]), split="subject", mode="confirmatory",
         family="T16-dream", family_size="2", replicated_independently="no", readme_claim="no",
         ground_truth="delayed_report", note="adding posterior delta lowered held-out AUC"),
    dict(id="T16-GNWT-H1", claim="frontal delta lower before N2 experience (GNWT workspace)", area="theory_tests",
         file="experiments/theory_tests/dream_results.json", statistic=f"AUC {f(d['frontal']['auc'])}",
         p_value=f(d["frontal"]["p_one_sided"], 4), p_source="permutation within dataset, 5000",
         ci=str(d["frontal"]["ci95"]), n=str(d["n"]), distinct_subjects=str(d["n_subjects"]), split="subject",
         mode="confirmatory", family="T16-dream", family_size="2", replicated_independently="no",
         readme_claim="no", ground_truth="delayed_report", note=d["verdict_GNWT"]),
    dict(id="T16-GNWT-H2", claim="frontal delta adds over 1-30 Hz exponent, subject-held-out", area="theory_tests",
         file="experiments/theory_tests/dream_results.json", statistic=f"dAUC {f(d['H3_frontal']['dAUC'])}",
         p_value="", p_source="subject-cluster bootstrap CI", ci=str(d["H3_frontal"]["ci95"]),
         n=str(d["n"]), distinct_subjects=str(d["n_subjects"]), split="subject", mode="confirmatory",
         family="T16-dream", family_size="2", replicated_independently="no", readme_claim="no",
         ground_truth="delayed_report", note=""),
    dict(id="T16-ENT-H2", claim="phase-normalised LZ lower at moderate propofol (entropic brain, beyond spectrum)",
         area="theory_tests", file="experiments/theory_tests/chennu_results.json",
         statistic=f"median diff {c['pnlz']['median_diff']:.4f}", p_value=f(c["pnlz"]["wilcoxon_p_less"], 4),
         p_source="Wilcoxon signed-rank one-sided", ci=str(c["pnlz"]["ci95"]), n=str(c["subjects"]),
         distinct_subjects=str(c["subjects"]), split="subject", mode="confirmatory", family="T16-ENT",
         family_size="2", replicated_independently="no", readme_claim="no", ground_truth="behaviour",
         note=c["verdict_ENT"]),
    dict(id="T16-ENT-H1", claim="LZ lower at moderate propofol", area="theory_tests",
         file="experiments/theory_tests/chennu_results.json", statistic=f"median diff {c['lz']['median_diff']:.4f}",
         p_value=f(c["lz"]["wilcoxon_p_less"], 4), p_source="Wilcoxon signed-rank one-sided", ci=str(c["lz"]["ci95"]),
         n=str(c["subjects"]), distinct_subjects=str(c["subjects"]), split="subject", mode="confirmatory",
         family="T16-ENT", family_size="2", replicated_independently="no", readme_claim="no",
         ground_truth="behaviour", note=""),
    dict(id="T16-planted-dream", claim="pipeline recovers planted posterior/frontal delta reduction", area="theory_tests",
         file="experiments/theory_tests/planted_dream.json", statistic=f"power {pl['posterior_a0.75']['power_at_0.025']} at a=0.75",
         p_value="", p_source="200 sims x 1000 perms", ci="", n=str(d["n"]), distinct_subjects=str(d["n_subjects"]),
         split="none", mode="method_check", family="", family_size="", replicated_independently="no",
         readme_claim="no", ground_truth="synthetic", note=f"FPR {pl['posterior_a1.0']['power_at_0.025']}"),
]
ledger_rows_write(os.path.join(HERE, "ledger_rows.csv"), L)
print(open(os.path.join(HERE, "scoreboard.csv")).read())
