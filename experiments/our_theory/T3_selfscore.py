"""SELF-SCORE of T3 (write-back theory) on the 59-row constraint ledger, by its author (theory2, task #32).
Not blind. Blind scoring is task #35. Same scale and weights as experiments/theory_scorecard/build_scorecard.py.
Writes T3_selfscore.csv and prints totals (weighted, and harsh = every post hoc 'explains' counted as 'compatible').
Run: python3 -I T3_selfscore.py
"""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "..", "constraint_ledger", "ledger.csv")
E, C, S, T = "explains", "compatible", "silent", "strained"
# id: (mark, post_hoc, reason)
M = {
"C01": (C, 0, "Residual LGN-extrastriate vision is feedforward fast activity that need not write back; why it fails to without V1 is not derived."),
"C02": (C, 0, "Attention sets gain on fast activity; write-back is a separate condition. Allowed."),
"C03": (C, 0, "Comparing half-fields needs one slow-layer record both hemispheres write into; the cut removes it. Allowed."),
"C04": (S, 0, "T3 gives each hemisphere its own record and does not say whether that makes two subjects."),
"C05": (C, 1, "Cortex-only scope (S2) is a stipulation borrowed from IIT/RPT."),
"C06": (C, 0, "One hemisphere has both layers. Trivial."),
"C07": (E, 1, "Content comes from the areas whose fast activity writes back; removing an area removes its content. Shared with IIT/RPT."),
"C08": (E, 1, "S1: write-back in any region suffices, so prefrontal loss leaves posterior write-back and consciousness."),
"C09": (C, 0, "Frontal damage could reduce write-back of frontal (visibility) content. Allowed, not predicted."),
"C10": (C, 0, "Stimulation drives fast activity that writes back; why some sites evoke nothing is not derived."),
"C11": (S, 0, "T3 makes no site-specific claim about prefrontal subregions."),
"C12": (C, 0, "T3 claims all agents but ketamine make the slow layer autonomous; a claim, not derived from molecular targets; untested (P4)."),
"C13": (C, 0, "L5 apical decoupling could be a cellular route, but DIT tested the read direction; frontal-parietal feedback is not required."),
"C14": (C, 0, "Predicts preserved W under anaesthetic ketamine; no data yet."),
"C15": (C, 0, "Memory encoding is downstream of the written record. Allowed."),
"C16": (E, 1, "Presence is independent of delta, so high-delta NREM can carry experience; W varies within every stage."),
"C17": (C, 0, "Posterior low-frequency drop and HF content signals are correlates; T3 predicts direction beats them (P1)."),
"C18": (C, 0, "Content is sensory-area fast activity that writes back; same format as waking."),
"C19": (C, 0, "Connection is orthogonal; REM theta layer stays written so input that drives fast activity is incorporated. When gating opens is not derived."),
"C20": (C, 0, "Behaviour is not part of the condition; P2 says which patients. No data, so not explains."),
"C21": (E, 1, "Arousal and write-back are different; UWS without awareness = arousal without write-back. That OFF-periods imply null W is assumed."),
"C22": (E, 1, "A mask within the write-back time overwrites the slow-layer state before the target is recorded; feedforward priming survives. Shared with RPT/Herzog."),
"C23": (C, 0, "Fast activity without write-back can be deep or shallow."),
"C24": (C, 0, "Needs a capacity auxiliary for why the second target fails to write back."),
"C25": (C, 0, "Unattended input may not write back, or be written and forgotten."),
"C26": (C, 0, "The record may hold more than is encoded for report."),
"C27": (C, 0, "Visibility reports read the record through a separate confidence process."),
"C28": (C, 0, "Report is not part of the condition; P3b loss without report allowed."),
"C29": (C, 0, "Late sustained activity on some trials fits write-back on those trials; not derived."),
"C30": (C, 0, "Write-back can change slow-layer patterns without univariate change."),
"C31": (C, 0, "No frontal requirement; allowed."),
"C32": (C, 0, "Frontal content allowed; not required."),
"C33": (C, 0, "Allowed."),
"C34": (S, 0, "T3 says nothing about all-or-none responses."),
"C35": (C, 0, "Write-back takes time; a prior presets the slow layer. Not derived as a number."),
"C36": (E, 1, "The slow layer integrates written content over tau_w; later input within tau_w changes the same state. Window = measured tau_w (P3)."),
"C37": (C, 0, "Excitability changes how readily fast activity writes back; criterion shift allowed."),
"C38": (C, 0, "Global rule response needs a record across seconds; local mismatch is fast-only. Allowed."),
"C39": (C, 0, "Needs neither sustained synchrony nor ignition; inferior frontal content allowed."),
"C40": (E, 1, "Bistable up/down states come from intrinsic currents, so the slow layer runs autonomously and fast activity is only read."),
"C41": (C, 0, "PCI and W should mostly agree; T3 allows dissociations."),
"C42": (E, 1, "Delta amplitude is slow-layer size, not drive direction; conscious delta keeps write-back. Core of P1."),
"C43": (C, 0, "Spike-wave is an imposed slow rhythm (read without write); network-size differences not derived."),
"C44": (E, 1, "Local slow wave = local write-back stops: local content lapses while the rest writes back."),
"C45": (C, 0, "Power and hub activity are not in the condition; richer content not derived."),
"C46": (C, 0, "Signal diversity not in the condition."),
"C47": (C, 0, "Enabling condition."),
"C48": (C, 0, "Enabling condition."),
"C49": (C, 0, "Central lateral thalamic drive makes the slow layer input-driven again. Allowed."),
"C50": (S, 0, ""),
"C51": (C, 0, "ACh restores input-driven slow dynamics; why prefrontal and not parietal is not derived."),
"C52": (C, 0, "Early visual activation without write-back allowed."),
"C53": (S, 0, "T3 says nothing about multisensory body ownership."),
"C54": (S, 0, ""),
"C55": (T, 0, "Cortex-only (S2): must deny these children are conscious or credit residual cortex."),
"C56": (S, 0, "A gamma surge counts only if it writes back; no direction data exist."),
"C57": (S, 0, ""),
"C58": (S, 0, ""),
"C59": (C, 0, "Classical theory; out of scope for totals."),
}
PTS = {E: 2, C: 1, S: 0, T: -1, "contradicts": -2}
W = {"A": 3, "B": 2, "C": 1}
led = list(csv.DictReader(open(LEDGER)))
assert set(M) == {r["id"] for r in led}
rows = []
for r in led:
    m, ph, why = M[r["id"]]
    rows.append(dict(id=r["id"], grade=r["evidence_grade"], T3_mark=m, post_hoc=ph, reason=why, constraint=r["constraint"]))
with open(os.path.join(HERE, "T3_selfscore.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
ins = [x for x in rows if x["id"] != "C59"]
from collections import Counter
cnt = Counter(x["T3_mark"] for x in ins)
score = sum(W[x["grade"]] * PTS[x["T3_mark"]] for x in ins)
harsh = sum(W[x["grade"]] * PTS[C if (x["T3_mark"] == E and x["post_hoc"]) else x["T3_mark"]] for x in ins)
print(dict(cnt), "weighted", score, "harsh", harsh, "max", sum(W[x["grade"]] * 2 for x in ins))
