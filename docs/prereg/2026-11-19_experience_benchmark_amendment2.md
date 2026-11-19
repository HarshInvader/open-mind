# Amendment 2 to the experience benchmark pre-registration

Amends `docs/prereg/2026-11-19_experience_benchmark.md` (sha256 de1f44ce…) and amendment 1 (sha256 bc1db71e…). Written 2026-11-19 at the coordinator's request, alongside outreach to the authors of wSMI. **No DREAM label has been joined to any EEG feature, and no DREAM EEG has been extracted yet** (extraction is queued behind the compute lock). Everything else stands.

## 1. wSMI stays in the sealed primary list, unchanged

wSMI remains primary measure 7, as sealed in `measures.py` (sha256 f8e2ea31…). It follows the definition in King et al. 2013 and Sitt et al. 2014:
- Each channel is turned into ordinal symbols of k = 3 samples with lag tau = 3 samples, which is 30 ms at the 100 Hz branch. That gives 6 symbols.
- Mutual information is computed between the symbol sequences of each channel pair. Joint symbol pairs that are identical or opposite get weight 0, which removes common-source and volume-conduction effects.
- The value is divided by log 6 and averaged over all pairs of the 10-20 subset.

**Not yet verified.** In this session I have not opened the original papers to check their exact choices: the tau values, any tau-specific low-pass filtering before symbolisation, the reference scheme, and the channel pairs. Until that check is done, the sealed version is described as "after King et al. 2013 / Sitt et al. 2014" and not as identical to them. Section 2 below is how we take in the authors' own parameters without changing the sealed version.

## 2. Rule: externally nominated parameter sets

Externally nominated parameter sets (for example, from a measure's original authors) may be added as a declared amendment, hashed, before the confirmation labels are opened. They are reported alongside the frozen version, never in place of it.

How it works:
- The nominated set is written into a new amendment file and the code that computes it, and both are sealed (HASHES.txt) before any Tier 1 label is joined. The amendment records who nominated the set and when it was received.
- Extraction streams the data and deletes it, so raw signals are not kept. A nominated set is therefore computed by a separate label-blind re-extraction pass, with the same windows, channels and exclusions as the sealed one. Its features file is sealed before unblinding.
- The nominated version is tested with the same Family A statistic and gate, but outside every Holm family. It does not count toward the A1 headline (6 of 8), and it cannot replace the frozen version in A2. It is reported in a separate table next to the frozen result, whatever either one shows.
- If a nominated set arrives after the confirmation labels are opened, it may still be run, but only as exploratory and labelled that way.
- Any nominated set is checked by planted checks P1(a)-(c) for that measure before unblinding.
