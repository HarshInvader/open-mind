# Chennu 2016 propofol EEG within the download budget (task #21)

**Verdict: solved without a lead decision.** The 3.69 GB zip (doi:10.17863/CAM.68959, CC BY 2.0 UK) never needs to be downloaded whole. The Cambridge server answers HTTP range requests, so any single recording, or just its first N seconds, can be streamed out of the zip.

## How
- Bitstream: https://api.repository.cam.ac.uk/server/api/core/bitstreams/e94a6722-da5b-4e53-8673-5e8ec106e0f7/content (3,694,326,663 bytes).
- Read the central directory from the zip's tail (one 70 kB request): 80 `.fdt` + 80 `.set` members and `datainfo.mat`.
- Pull one member's byte range and inflate it as a stream, stopping after the bytes you need. mind-3's `experiments/theory_tests/ziprange.py` (`RemoteZip(url).read(name, max_out=...)`) does this; I used it here unchanged.
- `.fdt` = float32, 91 channels, channel-fastest, 250 Hz. One recording is 35.49 MB uncompressed = 97,500 samples, about 6.5 min.

## Check (results.json)
- First 60 s of `02-2010-anest 20100210 135.003.fdt` (baseline): 5.46 MB inflated, 15,000 x 91 samples, all finite, median channel SD 7.2 µV. Took 5.3 s.
- `datainfo.mat` (1.5 kB) fetched the same way. Columns are name, level 1-4, plasma propofol ng/ml, RT ms, hits/40. The meanings are inferred, but they match the paper's 13 responsive / 7 drowsy at moderate (see experiments/ground_truth).

## Budget
- Whole set, all 80 recordings: 3.69 GB. Over the budget.
- First 60 s of all 80 recordings: about 0.45 GB transferred. Baseline + moderate only: about 0.22 GB. Both fit.
- Take only what a sealed prereg needs; save features; delete the raw arrays.

## Not checked
- `.set` headers (channel locations, event lists) were not parsed here. The channel count of 91 comes from the paper and the byte arithmetic.
- No file other than recording 02/baseline was streamed.
