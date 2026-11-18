"""Ledger coverage marks for our candidate theories T1 (settling window) and T2 (anterior-posterior settling).

Each entry: id -> (T1 mark, T1 post hoc?, T1 reason, T2 mark, T2 post hoc?, T2 reason).
Marks: explains / compatible / silent / strained / contradicts (same scale as experiments/theory_scorecard).
"post hoc" = the theory was written knowing the finding, so the 'explains' is a retrodiction, not a prediction.
T2 reason "same" means the T1 reasoning applies unchanged.
Run: python3 -I marks.py  -> writes coverage.csv and prints the score tables.
"""
import csv, os

M = {
"C01": ("compatible", 0, "V1 loss removes the patch where visual content would be held; the LGN-extrastriate route drives behaviour without a held state. Why extrastriate cortex cannot hold the state alone is not derived.",
        "compatible", 0, "same"),
"C02": ("compatible", 0, "Attention sets gain on inputs; holding is a separate condition, so attention without awareness is allowed. Not predicted.",
        "compatible", 0, "same"),
"C03": ("compatible", 0, "Each hemisphere's posterior cortex can hold its own state; comparing them needs callosal coupling. Allowed, not predicted.",
        "compatible", 0, "same"),
"C04": ("strained", 0, "T1 says a held state cannot span uncoupled hemispheres, so it predicts two streams. Pinto 2017 (n = 2) argue for one. Contested data, so strained, not contradicted.",
        "strained", 0, "same"),
"C05": ("compatible", 1, "T1 restricts the substrate to recurrent thalamocortical sensory-format cortex. That restriction is a stipulation borrowed from IIT/RPT, not derived, so compatible only.",
        "compatible", 1, "same"),
"C06": ("compatible", 0, "One hemisphere has a full posterior cortex that can hold states. Trivially allowed.",
        "compatible", 0, "One hemisphere keeps its own anterior-posterior loop. Trivially allowed."),
"C07": ("explains", 1, "Content is set by which posterior patches hold a state; removing a patch removes that content dimension while others still hold. Post hoc; shared with IIT and RPT.",
        "explains", 1, "same"),
"C08": ("explains", 1, "Frontal cortex is not in the presence condition, so frontal lesions cannot abolish experience. Post hoc; shared with IIT and RPT.",
        "strained", 0, "T2 needs anterior re-entry. It survives large frontal lesions only by assuming the orbitofrontal/cingulate/inferior-frontal loop sites are spared or redundant (an auxiliary)."),
"C09": ("strained", 0, "T1 must add that left anterior PFC sets the report criterion, not the held state. That is an auxiliary assumption.",
        "compatible", 0, "Damage to the anterior loop could raise the threshold for holding, and subjective visibility more than objective performance. Allowed, not predicted (one study)."),
"C10": ("explains", 1, "Stimulating a posterior patch imposes a pattern that the patch then holds; the content matches the site's tuning. Post hoc.",
        "compatible", 0, "Allowed if the anterior loop is intact (it is in these patients); T2 adds nothing beyond T1."),
"C11": ("compatible", 0, "Lateral PFC is outside the holding substrate, so its stimulation should seldom change experience. OFC/ACC effects need the auxiliary that affective/interoceptive cortex is also sensory-format cortex.",
        "explains", 1, "T2 names OFC, ACC and inferior frontal cortex as the re-entry sites and excludes dorsolateral PFC, so stimulation should change experience there and not laterally. Post hoc: the sites were chosen knowing this result."),
"C12": ("explains", 1, "All agents except ketamine push cortex into bistability, so OFF-periods cut every run shorter than the hold time. Post hoc: mechanism borrowed from the bistability line (Massimini, Sanchez-Vives).",
        "explains", 1, "same, plus anterior OFF-periods suffice under T2"),
"C13": ("compatible", 0, "Layer 5 apical decoupling is a plausible cellular route to failed holding; reduced frontal-to-parietal feedback is allowed but not required.",
        "explains", 1, "Reduced frontal-to-parietal feedback across agents is exactly loss of the anterior re-entry T2 requires. Post hoc; this is Mashour/Lee's own reading."),
"C14": ("explains", 1, "Ketamine does not make posterior cortex bistable (wake-like PCI), so states are still held: rich experience. Unresponsiveness is disconnection, which T1 treats as irrelevant to presence. Post hoc; rests on one cohort.",
        "strained", 0, "Lee 2013 reports reduced frontal-to-parietal feedback under ketamine too, yet people dream. T2 must assume ketamine spares re-entry at the loop sites, against the only connectivity data in the ledger."),
"C15": ("explains", 1, "Presence needs only holding; memory encoding is a separate downstream process, so connected experience without recall is expected. Post hoc.",
        "explains", 1, "same"),
"C16": ("explains", 1, "Within NREM the amount of OFF-free posterior time varies, so some awakenings follow held states and some do not; REM is mostly OFF-free, so more reports. Post hoc.",
        "compatible", 0, "Allowed, but T2 adds a frontal condition that NREM data were not shown to need."),
"C17": ("explains", 1, "Fewer posterior slow waves = more OFF-free time = more held states. Post hoc; shared with IIT.",
        "strained", 0, "T2 predicts frontal OFF-periods also block experience. Siclari 2017 found the effect posterior; Siclari 2018 found large steep frontal slow waves with micro-arousals before successful recall, the opposite sign."),
"C18": ("explains", 1, "Content is the held pattern in sensory-format cortex, the same format as waking perception, so wake-trained decoders should transfer. Post hoc.",
        "compatible", 0, "Allowed; T2's frontal loop is not visible in this result."),
"C19": ("compatible", 0, "T1 makes connection orthogonal to presence, so a dreamer who is selectively connected (hears, answers by eye) is allowed. T1 does not say when connection reopens.",
        "compatible", 0, "same"),
"C20": ("compatible", 0, "Allowed: behaviour is not part of the presence condition. T1 makes a risky prediction of WHO (prediction P2) but there is no data yet, so not 'explains'.",
        "compatible", 0, "Allowed; T2 predicts covert awareness only where both posterior and anterior loop sites lack OFF-periods."),
"C21": ("explains", 1, "Arousal (eyes open, sleep-wake cycles) is brainstem-driven; awareness needs held cortical states, which TMS-evoked OFF-periods in UWS prevent (Rosanova 2018: phase-locking ends at 167-188 ms in UWS vs 248 ms in awake controls). Post hoc: the hold time was chosen knowing these numbers.",
        "explains", 1, "same"),
"C22": ("explains", 1, "A mask arriving before the hold time rewrites the patch before the target state is held, so the target is never experienced, while early feed-forward processing (priming) runs. A sharp threshold follows from holding being all-or-none. Post hoc; shared with RPT, Herzog, Bachmann.",
        "explains", 1, "same"),
"C23": ("compatible", 0, "Unheld processing can be deep or shallow; T1 does not set its depth.",
        "compatible", 0, "same"),
"C24": ("compatible", 0, "Needs an attention/capacity auxiliary: T1 alone does not say why T2 fails at 200-500 ms but not at lag 1.",
        "compatible", 0, "same"),
"C25": ("compatible", 0, "Unattended input may never drive a held state, or be held and forgotten; T1 allows both.",
        "compatible", 0, "same"),
"C26": ("compatible", 0, "T1 sides with 'held content is richer than what is encoded for report', but the overflow reading is contested, so compatible.",
        "compatible", 0, "same"),
"C27": ("compatible", 0, "Visibility reports read the held state through a separate confidence process; dissociation allowed.",
        "compatible", 0, "same"),
"C28": ("explains", 1, "No late frontal component is needed; the earlier posterior negativity (~200-240 ms) falls inside the hold time. Post hoc; shared with IIT and RPT.",
        "compatible", 0, "T2's re-entry is not the P3b, so its loss without report is allowed but not predicted."),
"C29": ("explains", 1, "Sustained activity from ~250-300 ms on some trials = the state was held; it predicts later reports. Post hoc; one study (grade C).",
        "explains", 1, "same"),
"C30": ("compatible", 0, "Frontal cortex can carry copies of held content without being needed. Allowed.",
        "explains", 1, "Frontal patterns that carry awareness without a univariate response fit low-level re-entry. Post hoc."),
"C31": ("explains", 1, "Frontal fMRI follows report, not percept, because frontal cortex is outside the presence condition. Post hoc.",
        "strained", 0, "T2 says re-entry from frontal sites is needed for each held percept. Frässle 2014 saw no frontal activity tied to switches without report. T2 must claim the re-entry is too weak for fMRI."),
"C32": ("compatible", 0, "Prefrontal neurons may hold copies of the held content; T1 does not forbid frontal content, only frontal necessity.",
        "explains", 1, "Prefrontal content without report is what T2's re-entry predicts. Post hoc."),
"C33": ("compatible", 0, "The held state spans the posterior hierarchy; percept-following rising along it is allowed.",
        "compatible", 0, "same"),
"C34": ("explains", 1, "Holding is all-or-none (a state is held for the full hold time or it is not), so near-threshold responses in higher areas should be bimodal. Post hoc.",
        "explains", 1, "same"),
"C35": ("explains", 1, "Seen and unseen diverge when the hold completes (~200-250 ms); a prior speeds settling, so expectation moves it earlier. Post hoc: the hold time was chosen from this range.",
        "explains", 1, "same"),
"C36": ("explains", 1, "A content is experienced only once held; inputs arriving before then rewrite it, and the held content is dated to the start of its input. Long postdiction (hundreds of ms) needs the rule that a changing input resets the hold. Post hoc; mechanism shared with Herzog's discrete-perception model.",
        "explains", 1, "same"),
"C37": ("compatible", 0, "Excitability changes how easily a state is held, so a criterion shift is allowed.",
        "compatible", 0, "same"),
"C38": ("compatible", 0, "The local mismatch response is feed-forward; the global rule response needs held states across time. Allowed.",
        "compatible", 0, "same"),
"C39": ("compatible", 0, "T1 needs uninterrupted activity, not sustained synchrony, and no ignition at offset. Our reading; not checked against COGITATE's duration analyses.",
        "explains", 1, "Content in inferior frontal cortex with limited dorsolateral content fits T2's choice of loop sites. Post hoc."),
"C40": ("explains", 1, "Bistability is the mechanism that stops holding. T1 was built on this, so post hoc.",
        "explains", 1, "same"),
"C41": ("explains", 1, "OFF-periods cut causal chains, so evoked complexity is low exactly when holding fails. Post hoc; inherits PCI's one-consortium evidence.",
        "explains", 1, "same"),
"C42": ("compatible", 0, "Allowed only if delta in conscious people lacks neuronal OFF-periods (no broadband suppression at troughs). That is prediction P4, untested.",
        "compatible", 0, "same"),
"C43": ("compatible", 0, "Larger network changes in impairing seizures fit wider cortical silencing; not derived.",
        "compatible", 0, "same"),
"C44": ("explains", 1, "Local OFF-periods remove only the contents held in that patch; the rest still holds, so the animal stays awake with local lapses. Post hoc.",
        "explains", 1, "same"),
"C45": ("compatible", 0, "Power and hub activity do not enter the presence condition; reduced alpha with no OFF-periods leaves holding intact. Richer content is not derived.",
        "compatible", 0, "same"),
"C46": ("compatible", 0, "Higher signal diversity is allowed; T1 says nothing about intensity.",
        "compatible", 0, "same"),
"C47": ("compatible", 0, "Brainstem arousal is an enabling condition that keeps cortex out of bistability. Allowed, not derived.",
        "compatible", 0, "same"),
"C48": ("compatible", 0, "Same as C47 for paramedian thalamus.",
        "compatible", 0, "same"),
"C49": ("compatible", 0, "Central lateral thalamic stimulation removes bistability, so holding returns. Allowed; T1 adds the testable claim that recovery tracks posterior OFF-period loss.",
        "compatible", 0, "same"),
"C50": ("silent", 0, "Nothing in T1 concerns the claustrum.",
        "silent", 0, "same"),
"C51": ("strained", 0, "T1's substrate is posterior; it needs the auxiliary that prefrontal acetylcholine acts through arousal nuclei, and that the righting reflex tracks arousal.",
        "explains", 1, "Prefrontal (not parietal) cholinergic drive restoring consciousness fits a required anterior site. Post hoc; rats, righting reflex."),
"C52": ("compatible", 0, "Early visual activation without holding is allowed; T1 predicts such responses are brief.",
        "compatible", 0, "same"),
"C53": ("compatible", 0, "Bodily content is held in multisensory cortex; T1 does not explain why synchrony drives the illusion.",
        "compatible", 0, "same"),
"C54": ("silent", 0, "Nothing in T1 predicts zolpidem awakenings.",
        "silent", 0, "same"),
"C55": ("strained", 0, "T1 requires cortex. If these children are conscious, T1 is wrong; the evidence is behavioural and contested, so strained.",
        "strained", 0, "same"),
"C56": ("silent", 0, "Experience in dying rats is unknown; T1 cannot be scored on it.",
        "silent", 0, "same"),
"C57": ("silent", 0, "T1 is about sensory-format content; it says nothing firm about felt intention timing.",
        "silent", 0, "same"),
"C58": ("silent", 0, "Microtubules play no role in T1.",
        "silent", 0, "same"),
}

W_GRADE = {"A": 3, "B": 2, "C": 1}
W_MARK = {"explains": 2, "compatible": 1, "silent": 0, "strained": -1, "contradicts": -2}
HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "..", "constraint_ledger", "ledger.csv")

def main():
    led = {r["id"]: r for r in csv.DictReader(open(LEDGER))}
    rows = []
    for cid, (m1, p1, r1, m2, p2, r2) in M.items():
        g = led[cid]["evidence_grade"]
        rows.append(dict(id=cid, grade=g, T1_mark=m1, T1_post_hoc=p1, T1_reason=r1,
                         T2_mark=m2, T2_post_hoc=p2, T2_reason=(r1 if r2 == "same" else r2 if not r2.startswith("same,") else r1 + " " + r2[5:].strip()),
                         constraint=led[cid]["constraint"]))
    assert len(rows) == 58 and "C59" not in M
    with open(os.path.join(HERE, "coverage.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    for t in ("T1", "T2"):
        cnt = {k: 0 for k in W_MARK}; score = 0; harsh = 0; ph = 0
        for r in rows:
            m = r[f"{t}_mark"]; g = W_GRADE[r["grade"]]
            cnt[m] += 1; score += g * W_MARK[m]
            # harsh: a post-hoc 'explains' counts as 'compatible'
            mh = "compatible" if (m == "explains" and r[f"{t}_post_hoc"]) else m
            harsh += g * W_MARK[mh]; ph += (m == "explains" and r[f"{t}_post_hoc"])
        print(f"{t}: " + ", ".join(f"{k} {v}" for k, v in cnt.items()) + f" | weighted {score}/250 | post-hoc explains {ph} | harsh (post-hoc explains as compatible) {harsh}/250")

if __name__ == "__main__":
    main()
