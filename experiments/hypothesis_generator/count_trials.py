"""Per-subject hit/miss counts in OpenNeuro ds006394 (v1.0.5), from the beh TSVs only.

Usage: python -I count_trials.py <dir with sub-XX_task-{SiB,SiD}_beh.tsv>
Hit = probe present and response in {VISUAL, AUDITORY, PRESENT}; miss = probe present
and response ABSENT. NONE (no response) and practice trials are dropped.
"""
import glob, re, sys
import pandas as pd

rows = []
for f in sorted(glob.glob(f"{sys.argv[1]}/*_beh.tsv")):
    s, t = re.findall(r"sub-(\d+)_task-(\w+)_beh", f)[0]
    d = pd.read_csv(f, sep="\t")
    d = d[d.practice.astype(str).str.upper() == "FALSE"]
    pp = d[(d.probe_presence == "Present") & (d.probe_response != "NONE")]
    ab = d[(d.probe_presence == "Absent") & (d.probe_response != "NONE")]
    surp = pp.surprise_img.notna() | pp.surprise_sound.notna()
    hit = pp.probe_response.isin(["VISUAL", "AUDITORY", "PRESENT"])
    rows.append(dict(sub=s, task=t, hit=int(hit.sum()), miss=int((~hit).sum()),
                     miss_surprise=int((~hit & surp).sum()), hit_surprise=int((hit & surp).sum()),
                     miss_nosurprise=int((~hit & ~surp).sum()),
                     false_alarm_rate=round(float((ab.probe_response != "ABSENT").mean()), 3)))
pd.DataFrame(rows).to_csv("trial_counts.csv", index=False)
print("wrote trial_counts.csv", len(rows))
