"""List remote recordings for the ground-truth table (stdlib only). Writes raw/*.txt."""
import re, urllib.request, os
os.makedirs('raw', exist_ok=True)
def s3_keys(prefix):
    keys, token = [], None
    while True:
        u = f"https://s3.amazonaws.com/openneuro.org?list-type=2&prefix={prefix}" + (f"&continuation-token={urllib.parse.quote(token)}" if token else "")
        t = urllib.request.urlopen(u, timeout=60).read().decode()
        keys += re.findall(r"<Key>(.*?)</Key>", t)
        m = re.search(r"<NextContinuationToken>(.*?)</NextContinuationToken>", t)
        if not m: return keys
        token = m.group(1)
import urllib.parse
for ds in ("ds005620", "ds004541"):
    ks = [k for k in s3_keys(ds + "/sub-") if k.endswith((".vhdr", ".edf", ".set", ".snirf", ".bdf", "_events.tsv"))]
    open(f"raw/{ds}_keys.txt", "w").write("\n".join(ks))
    print(ds, len(ks))
r = urllib.request.urlopen("https://physionet.org/files/sleep-edfx/1.0.0/RECORDS", timeout=60).read().decode()
open("raw/sleepedf_RECORDS.txt", "w").write(r); print("sleep-edf", len(r.split()))
