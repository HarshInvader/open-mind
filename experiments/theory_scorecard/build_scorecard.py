"""Task #25 (B2): theory x constraint scorecard.
Reads ../constraint_ledger/ledger.csv, writes scorecard.csv, totals.csv, gaps.csv, splits.csv.
Marks: E explains, C compatible, S silent, T strained, X contradicts.
Each non-silent cell names a proponent source (key into SRC) or says 'no published position' (our reading).
Run: python3 -I build_scorecard.py
"""
import csv, os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "..", "constraint_ledger", "ledger.csv")

THEORIES = {
    "GNWT": "Global neuronal workspace",
    "IIT": "Integrated information theory 4.0",
    "RPT": "Recurrent processing theory",
    "HOT": "Higher-order theories (HOROR / PRM / higher-order state space)",
    "PP": "Predictive processing / active inference / beast machine",
    "AST": "Attention schema theory",
    "DIT": "Dendritic integration theory (thalamocortical, L5 pyramidal)",
    "ORCH": "Orch-OR",
    "EB": "Entropic brain / complexity",
    "TTC": "Temporo-spatial theory",
    "BSA": "Brainstem affect theory (Solms; Merker)",
    "SL": "Strange loop (Hofstadter)",
}

# Proponent sources (all DOIs resolved on Crossref; quotes copied from abstracts or open full text read in this task).
SRC = {
    "mashour20": ("10.1016/j.neuron.2020.01.026", "Mashour, Roelfsema, Changeux & Dehaene 2020 (full text)"),
    "dehaene06": ("10.1016/j.tics.2006.03.007", "Dehaene et al. 2006 (abstract)"),
    "dehaene11": ("10.1016/j.neuron.2011.03.018", "Dehaene & Changeux 2011 (abstract)"),
    "delcul09": ("10.1093/brain/awp111", "Del Cul, Dehaene et al. 2009 (abstract)"),
    "dehaene01": ("10.1038/89551", "Dehaene et al. 2001 (Crossref)"),
    "dehaene98": ("10.1038/26967", "Dehaene et al. 1998 (Crossref)"),
    "sergent05": ("10.1038/nn1549", "Sergent, Baillet & Dehaene 2005"),
    "sergent21": ("10.1038/s41467-021-21393-z", "Sergent et al. 2021 (abstract)"),
    "bekin09": ("10.1073/pnas.0809667106", "Bekinschtein, Dehaene et al. 2009 (abstract)"),
    "vanvugt18": ("10.1126/science.aar7186", "van Vugt, ..., Dehaene & Roelfsema 2018 (Crossref)"),
    "pal18": ("10.1016/j.cub.2018.05.025", "Pal, ..., Mashour 2018 (abstract)"),
    "cogitate": ("10.1038/s41586-025-08888-1", "COGITATE Consortium 2025 (abstract)"),
    "albantakis23": ("10.1371/journal.pcbi.1011465", "Albantakis et al. 2023, IIT 4.0 (full text)"),
    "tk15": ("10.1098/rstb.2014.0167", "Tononi & Koch 2015 (full text)"),
    "koch16": ("10.1038/nrn.2016.22", "Koch, Massimini, Boly & Tononi 2016 (abstract)"),
    "boly17": ("10.1523/JNEUROSCI.3218-16.2017", "Boly et al. 2017"),
    "casali13": ("10.1126/scitranslmed.3006294", "Casali et al. 2013 (abstract)"),
    "sarasso15": ("10.1016/j.cub.2015.10.014", "Sarasso et al. 2015 (abstract; IIT-aligned group)"),
    "siclari17": ("10.1038/nn.4545", "Siclari, ..., Tononi 2017 (abstract)"),
    "rosanova18": ("10.1038/s41467-018-06871-1", "Rosanova et al. 2018 (abstract; IIT-aligned group)"),
    "vyaz11": ("10.1038/nature10009", "Vyazovskiy, ..., Tononi 2011 (abstract)"),
    "kochtsuchiya07": ("10.1016/j.tics.2006.10.012", "Koch & Tsuchiya 2007 (Crossref)"),
    "lr00": ("10.1016/S0166-2236(00)01657-X", "Lamme & Roelfsema 2000 (abstract)"),
    "lamme06": ("10.1016/j.tics.2006.09.001", "Lamme 2006 (abstract)"),
    "lamme10": ("10.1080/17588921003731586", "Lamme 2010 (abstract)"),
    "pinto17": ("10.1093/brain/aww358", "Pinto, ..., Lamme, ... 2017 (abstract)"),
    "tsuchiya15": ("10.1016/j.tics.2015.10.002", "Tsuchiya, Wilke, Frässle & Lamme 2015"),
    "lr11": ("10.1016/j.tics.2011.05.009", "Lau & Rosenthal 2011 (abstract)"),
    "bll19": ("10.1016/j.tics.2019.06.009", "Brown, Lau & LeDoux 2019 (abstract)"),
    "fleming20": ("10.1093/nc/niz020", "Fleming 2020 (full text)"),
    "lp06": ("10.1073/pnas.0607716103", "Lau & Passingham 2006 (Crossref)"),
    "odegaard17": ("10.1523/JNEUROSCI.3217-16.2017", "Odegaard, Knight & Lau 2017"),
    "hohwyseth20": ("10.33735/phimisci.2020.II.64", "Hohwy & Seth 2020 (abstract)"),
    "hohwy08": ("10.1016/j.cognition.2008.05.010", "Hohwy, Roepstorff & Friston 2008 (abstract)"),
    "seth13": ("10.1016/j.tics.2013.09.007", "Seth 2013 (abstract)"),
    "seth18": ("10.1016/j.tics.2018.08.008", "Seth & Tsakiris 2018 (abstract)"),
    "rebus19": ("10.1124/pr.118.017160", "Carhart-Harris & Friston 2019, REBUS (full text searched)"),
    "gw15": ("10.3389/fpsyg.2015.00500", "Graziano & Webb 2015 (full text)"),
    "aru20": ("10.1016/j.tics.2020.07.006", "Aru, Suzuki & Larkum 2020 (abstract)"),
    "sl20": ("10.1016/j.cell.2020.01.024", "Suzuki & Larkum 2020 (abstract)"),
    "aru19": ("10.3389/fnsys.2019.00043", "Aru, Suzuki, Rutiku, Larkum & Bachmann 2019 (full text)"),
    "bachmann20": ("10.33735/phimisci.2020.II.52", "Bachmann, Suzuki & Aru 2020 (abstract)"),
    "hp14": ("10.1016/j.plrev.2013.08.002", "Hameroff & Penrose 2014 (abstract)"),
    "hameroff06": ("10.1097/00000542-200608000-00024", "Hameroff 2006 (Crossref; no abstract)"),
    "khan24": ("10.1523/ENEURO.0291-24.2024", "Khan et al. 2024 (abstract)"),
    "ch14": ("10.3389/fnhum.2014.00020", "Carhart-Harris et al. 2014 (full text)"),
    "ch18": ("10.1016/j.neuropharm.2018.03.010", "Carhart-Harris 2018 (abstract)"),
    "schartner17": ("10.1038/srep46421", "Schartner et al. 2017 (abstract)"),
    "muthu13": ("10.1523/JNEUROSCI.2063-13.2013", "Muthukumaraswamy, Carhart-Harris et al. 2013 (abstract)"),
    "nh17": ("10.1016/j.neubiorev.2017.07.013", "Northoff & Huang 2017 (abstract)"),
    "nz22": ("10.1016/j.bbr.2022.113788", "Northoff & Zilio 2022 (abstract)"),
    "solms19": ("10.3389/fpsyg.2018.02714", "Solms 2019 (full text)"),
    "merker07": ("10.1017/S0140525X07000891", "Merker 2007 (abstract)"),
    # Task #36 (theory2). Hofstadter's books have no DOI; the first field is an ISBN or URL.
    # The archive.org copies are lending-restricted (search-inside 403) and Google Books returned a captcha,
    # so book quotes and pages are taken from reader transcriptions and were NOT checked against the printed page.
    "ias07": ("isbn:9780465030781", "Hofstadter, I Am a Strange Loop (Basic Books 2007); quote and page via https://intertwingled.org/i-am-not-a-strange-loop/, not checked against the book"),
    "geb79": ("url:https://www.mccurdyc.dev/books/2024-godel-escher-bach/", "Hofstadter, Godel, Escher, Bach (1979); quote and page from a reader's notes (edition not stated), not checked against the book"),
}

NP = None  # no published position found in the sources read
# CELLS[cid][theory] = (mark, src_key or NP, note). Theories not listed = silent, no published position.
CELLS = {
 "C01": {"RPT": ("E", "lr00", "'The feedforward sweep ... is probably incapable of yielding visual awareness'; without V1 feedback only feedforward vision remains."),
         "HOT": ("E", "fleming20", "'it may be possible to silence ... the neural substrates of an awareness state without affecting performance—a type of blindsight'."),
         "AST": ("E", "gw15", "'subjective awareness, the component that is lost in blindsight and neglect'."),
         "GNWT": ("C", "dehaene06", "Subliminal processing without workspace access is in the taxonomy; why V1 is needed is not derived."),
         "IIT": ("C", NP, "V1 loss removes part of the posterior complex; no IIT text on blindsight found."),
         "DIT": ("C", NP, "No DIT text on blindsight found."),
         "PP": ("C", NP, ""), "BSA": ("C", NP, "Cortex supplies content in this view.")},
 "C02": {"AST": ("E", "gw15", "Abstract: the theory 'explains how awareness and attention can sometimes become dissociated'."),
         "IIT": ("C", "kochtsuchiya07", "Koch (IIT co-author) argues attention and consciousness are distinct processes."),
         "GNWT": ("C", "mashour20", "Discusses attention and working memory as intertwined with conscious access."),
         "RPT": ("C", "lamme10", ""), "HOT": ("C", NP, "")},
 "C03": {"IIT": ("E", "tk15", "'multiple NCCs in a single brain, as shown by split-brain patients ... multiple local maxima of integrated information'."),
         "GNWT": ("C", NP, "A callosal cut should split long-range broadcasting; no GNWT text found."),
         "RPT": ("C", "pinto17", "Lamme co-authored: severing the connections 'splits visual perception'.")},
 "C04": {"IIT": ("T", "tk15", "IIT predicts two complexes; Pinto 2017 finds unified detection across the field. Needs an account of why one subject reports."),
         "RPT": ("C", "pinto17", "Lamme co-authored the 'undivided consciousness' reading; not derived from RPT."),
         "GNWT": ("S", NP, "")},
 "C05": {"IIT": ("E", "albantakis23", "'the cerebellum, whose anatomical organization is highly modular, does not contribute to consciousness'."),
         "DIT": ("C", "aru19", "'cerebellum, which are detached from the loop of consciousness' (stated, not derived)."),
         "GNWT": ("C", NP, "Cerebellum lacks workspace neurons; Mashour 2020 notes cerebellar nuclei take part in persistent-activity loops."),
         "RPT": ("C", NP, "Mostly feedforward circuitry."), "HOT": ("C", NP, ""),
         "PP": ("T", NP, "Cerebellum runs forward models; PP needs an extra rule for which predictions are conscious."),
         "ORCH": ("T", NP, "Cerebellar neurons contain microtubules; Orch-OR needs a reason they do not count.")},
 "C06": {t: ("C", NP, "Any theory with a cortical substrate survives one hemisphere.") for t in ["GNWT", "IIT", "RPT", "HOT", "DIT", "AST", "BSA"]},
 "C07": {"IIT": ("E", "koch16", "NCC 'primarily localized to a posterior cortical hot zone that includes sensory areas'."),
         "RPT": ("E", "lamme06", "Local recurrence in sensory areas specifies content."),
         "GNWT": ("C", "dehaene06", "Specialised processors supply content to the workspace."),
         "HOT": ("C", NP, "First-order states removed."), "PP": ("C", NP, ""), "DIT": ("C", NP, ""), "AST": ("C", NP, ""),
         "BSA": ("C", "solms19", "Solms: 'occipital lesions caused \"mind blindness\"'; cortex supplies content.")},
 "C08": {"IIT": ("E", "tk15", "'there can be consciousness without frontal cortex involvement'."),
         "RPT": ("E", "lamme10", "Phenomenal vision is sensory-cortical; access is frontal."),
         "BSA": ("E", "solms19", "Patients with destroyed prefrontal lobes and insula 'report preserved feeling states'."),
         "GNWT": ("C", "mashour20", "'focal lesions are unlikely to lead to a complete loss of consciousness ... except the most severe cases of bilateral damage'."),
         "HOT": ("T", "lr11", "Proponents defend against 'prefrontal lesion does not abolish awareness'; Fleming 2020: lesions 'may belie redundancy'. Needs redundancy assumption."),
         "PP": ("C", NP, ""), "DIT": ("C", NP, ""), "AST": ("C", NP, "")},
 "C09": {"GNWT": ("E", "delcul09", "GNWT authors' own lesion test of prefrontal amplification."),
         "HOT": ("E", "fleming20", "Fleming 2020 cites Del Cul 2009 as a blindsight-like loss of awareness with performance kept."),
         "IIT": ("C", NP, "Could be read as a change in report criterion."), "RPT": ("C", "lamme10", "Access, not seeing, affected.")},
 "C10": {"IIT": ("E", "koch16", "Posterior hot zone holds content."), "RPT": ("C", NP, ""), "GNWT": ("C", NP, ""), "HOT": ("C", NP, ""),
         "PP": ("C", NP, ""), "DIT": ("C", NP, ""), "BSA": ("C", NP, "")},
 "C11": {"IIT": ("E", "boly17", "Front-vs-back argument from stimulation and lesions."), "RPT": ("C", NP, ""),
         "GNWT": ("T", NP, "Lateral PFC is a workspace hub; needs an account of why stimulating it seldom changes experience."),
         "HOT": ("T", NP, "Same strain for prefrontal higher-order representations."), "BSA": ("C", NP, "")},
 "C12": {"GNWT": ("E", "mashour20", "Propofol, sevoflurane and ketamine 'have all been found by fMRI to functionally disconnect the prefrontal cortex and posterior parietal cortices'."),
         "IIT": ("E", "albantakis23", "'IIT can also account mechanistically for the loss of consciousness in deep sleep and anesthesia'."),
         "DIT": ("E", "sl20", "'three different anesthetics have the same disruptive influence on signaling along apical dendrites in cortical layer 5 pyramidal neurons in mice'."),
         "ORCH": ("E", "hameroff06", "Proponents propose microtubules as the common anaesthetic target (Hameroff 2006; Khan 2024 rat data). Weak evidence: see C58."),
         "EB": ("C", "ch18", "Entropy falls below a 'lower limit' and consciousness is lost; describes, no target-level mechanism."),
         "RPT": ("C", NP, "Loss of feedback fits, but no RPT-proponent text on anaesthesia read."),
         "TTC": ("C", "nh17", "Level = 'temporo-spatial nestedness' of spontaneous activity; no drug-specific account read."),
         "HOT": ("C", NP, ""), "PP": ("C", NP, ""), "BSA": ("C", NP, "")},
 "C13": {"DIT": ("E", "sl20", "Apical decoupling across three anaesthetics; also via cholinergic block and higher-order thalamus inactivation."),
         "RPT": ("E", NP, "Loss of feedback = loss of recurrence; predicted by RPT's core claim, but no RPT-proponent text on these data read."),
         "GNWT": ("C", "mashour20", "Frontoparietal disconnection under three drugs."), "IIT": ("C", NP, ""), "PP": ("C", NP, "Loss of top-down predictions.")},
 "C14": {"IIT": ("E", "sarasso15", "PCI (IIT-derived) stays wake-like under ketamine, which comes with dream reports."),
         "GNWT": ("T", "mashour20", "Ketamine disconnects PFC from parietal cortex, yet vivid experience is reported. Mashour 2020 notes anaesthesia 'is associated with dream states and other disconnected states'. Needs disconnection to spare internal ignition."),
         "EB": ("C", "schartner17", "Subanaesthetic ketamine raises diversity; anaesthetic-dose data not in EB papers read."),
         "DIT": ("S", NP, "Which anaesthetics Suzuki & Larkum used was not checked here.")},
 "C15": {"GNWT": ("C", "mashour20", "Discusses disconnected and connected states under anaesthesia."), "IIT": ("C", NP, ""), "RPT": ("C", NP, ""), "HOT": ("C", NP, "")},
 "C16": {"IIT": ("E", "albantakis23", "'Φ should be high in conscious states, such as wakefulness and dreaming, and low in ... dreamless sleep'."),
         "GNWT": ("C", "mashour20", "Cites Siclari 2017 dreaming in REM and NREM."),
         "EB": ("C", "ch14", "REM proposed as a candidate 'primary state'."), "PP": ("C", NP, ""), "DIT": ("C", NP, "")},
 "C17": {"IIT": ("E", "siclari17", "Tononi-lab study; posterior hot zone predicted by IIT."),
         "GNWT": ("C", "mashour20", "Cites the posterior hot-zone result without conflict claim."),
         "RPT": ("C", NP, ""), "HOT": ("T", NP, "No frontal correlate found; HOT needs frontal higher-order states during dreams.")},
 "C18": {t: ("C", NP, "Content in visual cortex fits any cortical theory.") for t in ["GNWT", "IIT", "RPT", "HOT", "PP", "DIT"]},
 "C19": {},
 "C20": {**{t: ("C", NP, "Experience is defined by brain criteria, not behaviour.") for t in ["RPT", "HOT", "PP", "DIT", "AST", "TTC", "EB", "BSA"]},
         "GNWT": ("C", "mashour20", "Notes 'the possibility of covert consciousness in the setting of behavioral unresponsiveness'."),
         "IIT": ("C", "casali13", "PCI was built to assess consciousness 'independent of sensory processing and behavior'.")},
 "C21": {"IIT": ("E", "rosanova18", "OFF-periods 'prevent the build-up of global complexity in UWS'."),
         "GNWT": ("E", "dehaene06", "The taxonomy 'distinguishes between vigilance and access'."),
         "DIT": ("C", "aru19", "State depends on thalamic coupling to L5p cells, not arousal alone."),
         "RPT": ("C", NP, ""), "HOT": ("C", NP, ""), "EB": ("C", NP, ""), "TTC": ("C", "nh17", "Level separated from arousal."),
         "BSA": ("T", NP, "Brainstem arousal is intact in UWS yet no awareness is shown; needs cortex as more than content.")},
 "C22": {"GNWT": ("E", "mashour20", "Simulations of masking; 'non-linear divergence occurs regardless of ... paradigm (e.g., ... masking ...)'."),
         "RPT": ("E", "lr00", "Masking interrupts recurrent processing while the feedforward sweep survives."),
         "HOT": ("E", "fleming20", "Simulated masking yields an ignition-like asymmetry in the higher-order model."),
         "DIT": ("C", "aru19", "Discusses backward masking."), "PP": ("C", NP, ""), "AST": ("C", NP, ""),
         "IIT": ("S", NP, "GNWT authors write IIT 'does not easily capture ... masking, attentional blink' (Mashour 2020); no IIT reply read.")},
 "C23": {"GNWT": ("E", "dehaene98", "GNWT lab's own evidence for subliminal semantic processing; its size is contested (C23 grade C)."),
         "RPT": ("C", NP, ""), "HOT": ("C", NP, "")},
 "C24": {"GNWT": ("E", "sergent05", "Late divergence on blinked trials; Mashour 2020 lists attentional blink among ignition paradigms."),
         "AST": ("C", NP, ""), "HOT": ("C", NP, ""), "RPT": ("C", NP, ""), "PP": ("C", NP, ""), "DIT": ("C", "aru19", "Discusses the attentional blink."),
         "IIT": ("S", NP, "See C22 note.")},
 "C25": {"GNWT": ("E", "mashour20", "Simulations of inattention as loss of conscious access."),
         "AST": ("E", "gw15", "'One example of the close link between awareness and attention is inattentional blindness'."),
         "RPT": ("C", "lamme10", "'we see much more than we think': unnoticed items may be seen but not accessed."),
         "HOT": ("C", NP, ""), "PP": ("C", NP, ""), "IIT": ("C", NP, "")},
 "C26": {"RPT": ("E", "lamme10", "'we see much more than we think ... Global Workspace theory is all about access but not about seeing'."),
         "GNWT": ("C", "dehaene06", "Accounted for as 'preconscious' representations."),
         "HOT": ("C", NP, ""), "IIT": ("C", NP, "")},
 "C27": {"HOT": ("E", "lp06", "Relative blindsight was put forward as evidence for HOT (Lau & Passingham 2006; Lau & Rosenthal 2011)."),
         "GNWT": ("C", "delcul09", "'dual-route signal detection theory of objective and subjective decision making'."),
         "AST": ("C", "gw15", "Separates subjective from objective awareness."), "RPT": ("C", NP, "")},
 "C28": {"IIT": ("E", "tk15", "'consciousness without a frontal P300, for example, during dreaming sleep'; Koch 2016 lists 'illusory' markers."),
         "RPT": ("E", "tsuchiya15", "Lamme co-authored the no-report programme that predicts report-related components drop out."),
         "GNWT": ("T", "mashour20", "Earlier stressed the P300 as 'the most consistent scalp-recorded correlate of conscious ignition'; now an ignition marker must be separated from the P3b (Sergent 2021)."),
         "HOT": ("C", "bll19", "'most proponents of HOT do not stipulate consciousness as equivalent to metacognition'."),
         "PP": ("C", NP, "")},
 "C29": {"GNWT": ("E", "sergent21", "GNWT group: bifurcation 'around 250-300 milliseconds' without any task."), "RPT": ("C", NP, ""), "IIT": ("C", NP, "")},
 "C30": {t: ("C", NP, "Frontal decoding without univariate response fits several readings.") for t in ["GNWT", "HOT", "IIT", "RPT"]},
 "C31": {"IIT": ("E", "koch16", "Frontal activity tied to 'task monitoring and reporting'."),
         "RPT": ("E", "tsuchiya15", "Frässle and Lamme co-authored the no-report argument."),
         "GNWT": ("T", NP, "Needs frontal ignition that fMRI does not see without report."),
         "HOT": ("T", NP, "Same strain for prefrontal higher-order states."), "PP": ("C", NP, "")},
 "C32": {"GNWT": ("E", "mashour20", "'prefrontal neurons encode ... the specific current content of consciousness during binocular rivalry'."),
         "HOT": ("C", "fleming20", "Cites symmetric presence/absence coding in LPFC (Panagiotaropoulos 2012)."),
         "IIT": ("T", NP, "Needs PFC content signals to be non-conscious correlates."),
         "RPT": ("T", NP, "Needs PFC content signals to be access, not experience.")},
 "C33": {"PP": ("E", "hohwy08", "Title: 'Predictive coding explains binocular rivalry'."),
         "RPT": ("C", NP, ""), "IIT": ("C", NP, ""), "GNWT": ("C", NP, ""), "HOT": ("C", NP, ""), "DIT": ("C", "aru19", "Cites Leopold & Logothetis 1996.")},
 "C34": {"GNWT": ("E", "vanvugt18", "Dehaene and Roelfsema co-authored; all-or-none ignition predicted."),
         "HOT": ("E", "fleming20", "The presence/absence asymmetry 'provides a natural account of ... global ignition'."),
         "RPT": ("C", NP, ""), "PP": ("C", NP, "")},
 "C35": {"GNWT": ("E", "mashour20", "'a sudden divergence in brain activity, around 200 to 300 ms after stimulus onset'."),
         "PP": ("C", NP, "Expectation effects (Melloni 2011) fit priors lowering thresholds; no PP-proponent derivation read."),
         "RPT": ("C", NP, ""), "HOT": ("C", NP, "")},
 "C36": {"PP": ("C", NP, "Smoothing over a window fits Bayesian inference; no proponent derivation read."),
         "GNWT": ("C", NP, "Late access leaves room for later input to change content; no proponent derivation read.")},
 "C37": {"TTC": ("E", "nh17", "'temporo-spatial alignment of the pre-stimulus activity accounts for the content/form of consciousness'."),
         "PP": ("C", NP, "Prestimulus state as prior or precision."), "GNWT": ("C", NP, "")},
 "C38": {"GNWT": ("E", "bekin09", "GNWT group: global effect needs awareness; Mashour 2020 repeats this."),
         "PP": ("C", NP, "Strauss 2015 frames it as hierarchical predictive coding; authors are GNWT, not PP proponents."), "IIT": ("C", NP, "")},
 "C39": {"GNWT": ("T", "cogitate", "'challenged by the general lack of ignition at stimulus offset and limited representation ... in the prefrontal cortex'. Bandara 2026 (preprint) disputes."),
         "IIT": ("T", "cogitate", "'a lack of sustained synchronization within the posterior cortex contradicts the claim that network connectivity specifies consciousness'."),
         "RPT": ("S", NP, "COGITATE says challenges 'extend to other theories ... that share some of the predictions'.")},
 "C40": {"IIT": ("E", "tk15", "In deep sleep and anaesthesia 'interactions among different cortical regions become weaker or highly stereotypical'."),
         "DIT": ("C", "aru19", "Cites bistability (Massimini 2005) as failure to engage the rest of the brain."),
         "GNWT": ("C", NP, ""), "RPT": ("C", NP, ""), "EB": ("C", NP, "Lower entropy.")},
 "C41": {"IIT": ("E", "casali13", "PCI built from integration plus differentiation, as IIT requires."),
         "GNWT": ("C", NP, ""), "EB": ("C", NP, ""), "DIT": ("C", NP, ""), "RPT": ("C", NP, "")},
 "C42": {"IIT": ("C", NP, "IIT ties experience to causal structure, not spectra."),
         "EB": ("T", NP, "High-amplitude delta lowers signal entropy, yet people stay conscious; needs a spectral correction.")},
 "C43": {"IIT": ("E", "tk15", "Interactions become stereotypical 'as they do during generalized epileptic seizures'."),
         "GNWT": ("C", NP, ""), "DIT": ("C", NP, "Thalamocortical spike-wave fits, no DIT text found."),
         "BSA": ("C", "solms19", "Solms cites hydranencephalic children who have absence seizures (Shewmon)."),
         "EB": ("C", NP, "")},
 "C44": {"IIT": ("C", "vyaz11", "Tononi-lab finding; reported as a performance effect, not an experience effect.")},
 "C45": {"EB": ("E", "ch18", "'the entropy of brain activity is elevated in the psychedelic state'; Muthukumaraswamy 2013 desynchronisation."),
         "PP": ("E", "rebus19", "REBUS: psychedelics relax high-level priors (Carhart-Harris & Friston 2019)."),
         "DIT": ("C", "muthu13", "Muthukumaraswamy 2013 links the effect to 5-HT2A-rich deep-layer pyramidal cells; no DIT text read.")},
 "C46": {"EB": ("E", "schartner17", "'reliably higher spontaneous signal diversity, even when controlling for spectral changes'."),
         "PP": ("C", "rebus19", ""), "IIT": ("C", NP, "Diversity is one half of IIT-inspired complexity.")},
 "C47": {"BSA": ("E", "solms19", "'the smallest lesions within the brainstem which cause total loss of consciousness (i.e., coma) are located in or near the parabrachial nuclei'."),
         **{t: ("C", NP, "Brainstem as enabling condition.") for t in ["GNWT", "IIT", "RPT", "HOT", "DIT", "TTC"]}},
 "C48": {"DIT": ("E", "aru19", "'injuries and tumors localized in the NSP thalamus often cause absence of consciousness'."),
         "BSA": ("C", "solms19", "Part of the 'extended reticulothalamic activating system'."),
         "GNWT": ("C", NP, ""), "IIT": ("C", NP, "")},
 "C49": {"DIT": ("E", "aru19", "Non-specific thalamus stimulation restores wake-like activity (cites Honjoh 2018)."),
         "GNWT": ("C", NP, ""), "IIT": ("C", NP, ""), "RPT": ("C", NP, "Deep-to-superficial feedback was needed."), "BSA": ("C", NP, "")},
 "C50": {},
 "C51": {"GNWT": ("C", "pal18", "Mashour co-authored; PFC controls level."),
         "DIT": ("C", "sl20", "Cholinergic block decouples apical dendrites like anaesthesia."),
         "HOT": ("C", NP, ""),
         "IIT": ("T", NP, "IIT places the substrate posteriorly; a prefrontal-only reversal needs PFC to act as an arousal modulator.")},
 "C52": {"GNWT": ("E", "dehaene06", "Early sensory activation without access."),
         "AST": ("E", "gw15", "Neglect patients 'lose subjective awareness ... but retain objective awareness'."),
         "RPT": ("C", NP, ""), "HOT": ("C", NP, ""), "IIT": ("C", NP, "")},
 "C53": {"PP": ("E", "seth18", "Predictive accounts of interoception explain 'experiences of body ownership' (Seth 2013; Seth & Tsakiris 2018). Lush 2020 shows demand effects."),
         "AST": ("C", "gw15", "Body schema is the model for the attention schema.")},
 "C54": {},
 "C55": {"BSA": ("E", "solms19", "'Consciousness persists in the absence of cerebral cortex, as does volitional behavior'; Merker 2007."),
         "PP": ("C", "solms19", "Solms frames the brainstem view in free-energy terms."),
         **{t: ("T", NP, "Must deny these children are conscious or credit residual cortex.") for t in ["GNWT", "IIT", "RPT", "HOT", "DIT"]}},
 "C56": {},
 "C57": {},
 "C58": {"ORCH": ("E", "khan24", "'binding of the anesthetic gas isoflurane to MTs causes unconsciousness' (authors' reading of one rat study).")},
 "C59": {"ORCH": ("T", "hp14", "Proponents answer decoherence critiques; Donadi 2021 rules out the parameter-free Diosi-Penrose variant only."),
         **{t: ("C", NP, "Classical theory; needs no quantum coherence.") for t in ["GNWT", "IIT", "RPT", "HOT", "PP", "AST", "DIT", "EB", "TTC", "BSA"]}},
}

# Task #36 (theory2): Strange loop (Hofstadter). Non-silent cells quote his own words; every other row is silent
# because no statement by him on the finding was found. Strains that fall outside the ledger rows are in RESULTS.md.
SL_SILENT_NOTE = "Silent: no Hofstadter statement on this finding found in the sources read; not extrapolated."
SL_CELLS = {
 "C07": ("C", "ias07", "Closest statement, not about lesions: 'Those little sensual experiences (e.g., seeing purple, tasting chocolate) are to the grand pattern of your mental life as the letters in a novel are to the novel's plot and characters' (p. 287). Losing a content leaves the self-pattern intact."),
 "C16": ("S", NP, SL_SILENT_NOTE + " Strain outside the ledger: he equates consciousness with the self ('self, soul, I, a light on inside, and consciousness ... names for the same phenomenon', p. 275), yet dreams often have weak self-reflection."),
 "C45": ("S", NP, SL_SILENT_NOTE + " Strain outside the ledger: psychedelic ego dissolution with intensified experience conflicts with consciousness = 'I' (p. 275)."),
 "C20": ("S", NP, SL_SILENT_NOTE),
 "C21": ("S", NP, SL_SILENT_NOTE),
 "C59": ("C", "ias07", "'The cells inside a brain are not the bearers of its consciousness; the bearers of consciousness are patterns. The pattern of organization is what matters, not the substance' (p. 257). Classical; needs no quantum coherence."),
}
for _cid, _cell in SL_CELLS.items():
    CELLS.setdefault(_cid, {})["SL"] = _cell

MARKS = {"E": "explains", "C": "compatible", "S": "silent", "T": "strained", "X": "contradicts"}
PTS = {"E": 2, "C": 1, "S": 0, "T": -1, "X": -2}
W = {"A": 3, "B": 2, "C": 1}
OUT_OF_SCOPE = {"C59"}  # physics constraint on quantum theories, not a fact about experience

def main():
    led = list(csv.DictReader(open(LEDGER)))
    ids = [r["id"] for r in led]
    assert set(CELLS) <= set(ids), set(CELLS) - set(ids)
    rows = []
    for r in led:
        for t in THEORIES:
            m, s, note = CELLS.get(r["id"], {}).get(t, ("S", NP, ""))
            ref = SRC[s][0] if s and SRC[s][0].startswith(("isbn:", "url:")) else f"doi:{SRC[s][0]}" if s else ""
            pos = f"{SRC[s][1]}, {ref}" if s else "no published position"
            rows.append(dict(constraint_id=r["id"], grade=r["evidence_grade"], theory=t, mark=MARKS[m],
                             proponent_position=pos, basis="proponent" if s else "our reading",
                             note=note, constraint=r["constraint"]))
    with open(os.path.join(HERE, "scorecard.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    # totals
    tot = []
    for t in THEORIES:
        rs = [x for x in rows if x["theory"] == t and x["constraint_id"] not in OUT_OF_SCOPE]
        cnt = Counter(x["mark"] for x in rs)
        inv = {v: k for k, v in MARKS.items()}
        score = sum(W[x["grade"]] * PTS[inv[x["mark"]]] for x in rs)
        maxs = sum(W[x["grade"]] * 2 for x in rs)
        expl_w = sum(W[x["grade"]] for x in rs if x["mark"] == "explains")
        prop = sum(1 for x in rs if x["basis"] == "proponent")
        tot.append(dict(theory=t, name=THEORIES[t], explains=cnt["explains"], compatible=cnt["compatible"], silent=cnt["silent"],
                        strained=cnt["strained"], contradicts=cnt["contradicts"], weighted_score=score, max_possible=maxs,
                        weighted_explains=expl_w, cells_with_proponent_source=prop))
    tot.sort(key=lambda d: -d["weighted_score"])
    with open(os.path.join(HERE, "totals.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(tot[0])); w.writeheader(); w.writerows(tot)

    # gaps and splits
    by_c = defaultdict(list)
    for x in rows: by_c[x["constraint_id"]].append(x)
    gaps, splits = [], []
    for r in led:
        cid = r["id"]
        if cid in OUT_OF_SCOPE: continue
        ms = [x["mark"] for x in by_c[cid]]
        ex = [x["theory"] for x in by_c[cid] if x["mark"] == "explains"]
        bad = [x["theory"] for x in by_c[cid] if x["mark"] in ("strained", "contradicts")]
        if not ex:
            kind = "all silent/strained" if "compatible" not in ms else "none explains"
            gaps.append(dict(constraint_id=cid, grade=r["evidence_grade"], kind=kind,
                             compatible=" ".join(x["theory"] for x in by_c[cid] if x["mark"] == "compatible"),
                             strained=" ".join(bad), constraint=r["constraint"]))
        if ex and bad:
            splits.append(dict(constraint_id=cid, grade=r["evidence_grade"], explains=" ".join(ex), strained_or_contradicts=" ".join(bad),
                               split_strength=W[r["evidence_grade"]] * min(len(ex), len(bad)), constraint=r["constraint"]))
    gaps.sort(key=lambda d: ("ABC".index(d["grade"]), d["constraint_id"]))
    splits.sort(key=lambda d: (-d["split_strength"], "ABC".index(d["grade"]), d["constraint_id"]))
    for name, data in (("gaps.csv", gaps), ("splits.csv", splits)):
        with open(os.path.join(HERE, name), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0])); w.writeheader(); w.writerows(data)

    print(f"{len(rows)} cells; {sum(1 for x in rows if x['basis']=='proponent')} with proponent source")
    print(Counter(x["mark"] for x in rows))
    for d in tot: print(d)
    print("GAPS", len(gaps)); [print(" ", g["constraint_id"], g["grade"], g["kind"], "| compat:", g["compatible"], "| strained:", g["strained"]) for g in gaps]
    print("SPLITS", len(splits)); [print(" ", s["constraint_id"], s["grade"], "E:", s["explains"], "| T/X:", s["strained_or_contradicts"]) for s in splits]

if __name__ == "__main__":
    main()
