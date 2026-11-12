# Lab #5 - System Selection and Reproducibility Record

Software Quality and Metrics · MSc Software Engineering · Free University of Bozen-Bolzano
Lab instructor: Diaeddin Rimawi · Team: Blind Spot · Date of record: 2026-11-12

Raw logs and output artefacts: [`lab5-evidence/`](lab5-evidence/).

**All three shortlisted candidates were installed and executed**, not merely read about. The two
non-selected candidates were installed outside the fork, in separate virtual environments, so
nothing could contaminate the System Under Test.

## People and collaboration

- Working mode: [x] Solo  [ ] Pair
- Student A (name / GitHub): Nidhal Karchouid / [@yar01110](https://github.com/yar01110)
- Student B (name / GitHub; if pair): not applicable
- Fork owner: yar01110
- Collaborator invitation accepted? Not applicable (solo work)
- Individual work differentiation: not applicable (solo work). A single `QUALITY_INVESTIGATION.md` will be added on this branch in Lab #6 when measurement goals are formulated.

## First shortlist - catalogue only

Shortlisted from the computer-vision section of the 21-system catalogue using only the catalogue
descriptions, before opening any repository. Three different CV problem types were chosen
deliberately - a detector, a classifier and an anomaly localiser - so the comparison is not
between three variants of the same task.

| Candidate | Catalogue-based reason | One concern to investigate |
|---|---|---|
| A - Ultralytics YOLO (#18, Advanced CV) | Single package covering detection, segmentation, tracking **and** evaluation; catalogue names a validation tutorial and labelled held-out evaluation, so Lab #8 has a documented entry point | Catalogue flags AGPL-3.0 with separate weight/data terms, and warns the bundled COCO8 demo is not representative - both need checking before committing a semester to it |
| B - timm / PyTorch Image Models (#16, Core CV) | Marked laptop-friendly with permissive Apache-2.0 code; a large model pool implies a substantial codebase for Lab #6 static analysis | Catalogue states tests on synthetic tensors "do not establish prediction accuracy" - so where does credible classification ground truth come from? |
| C - Anomalib (#17, Advanced CV) | Only shortlisted candidate whose catalogue entry promises anomaly labels **and** pixel masks (MVTec AD) - the strongest ground-truth starting point for Lab #8 | Catalogue flags MVTec AD as CC BY-NC-SA 4.0 (non-commercial) and "do not upload into fork", plus strict PyTorch-version requirements |
| D | Not applicable - solo work requires 2-3 candidates; three were assessed | - |

## Evidence-based candidate assessment

Use Y = Yes; P = Partial; N = No; U = Unknown. **Attach links or file paths for factual claims.**

Scores marked *(measured)* were obtained by running the system on this laptop, not read from the
catalogue. Commands and outputs are recorded in [`lab5-evidence/`](lab5-evidence/).

| Criterion | Candidate A + evidence | Candidate B + evidence | Candidate C + evidence | Candidate D + evidence (pairs) |
|---|---|---|---|---|
| C1 Public repository / licence / data rights | **P** - public and forkable; AGPL-3.0 confirmed in [`LICENSE`](LICENSE) and `license = { "text" = "AGPL-3.0" }` in [`pyproject.toml`](pyproject.toml). Copyleft, not use-restricting; obligations only on redistribution or network service. Weight/dataset terms separate | **Y** - Apache-2.0 code ([repo](https://github.com/huggingface/pytorch-image-models)). *(measured)* 1826 pretrained weight sets vs 1371 architectures - more weights than models, each weight tag carrying its own terms | **P** - Apache-2.0 code ([repo](https://github.com/open-edge-platform/anomalib)); MVTec AD is CC BY-NC-SA 4.0, non-commercial, must not be committed | n/a |
| C2 Pinned revision / runtime | **Y** - pinned to tag `v8.4.211`, SHA `d2b7876e79ad2e02fd77221622774b511a8f0cb3`; `git describe --tags` returns `v8.4.211`. Upstream `main` advanced 8 commits past the pin within 13 h of tagging, confirming why pinning is required | **Y** *(measured)* - `timm 1.0.31` installed on Python 3.14 in 26 packages, no manual pinning, no compiler. Log: [`candidate-timm-log.txt`](lab5-evidence/candidate-timm-log.txt) | **Y** *(measured, revised up from P)* - `anomalib 2.7.0` installed clean on Python 3.14; `freia 0.2` compiled from source successfully. **The catalogue's PyTorch-version warning was tested and did not materialise.** Caveat: model construction downloads backbone weights, so it is not offline. Log: [`candidate-anomalib-log.txt`](lab5-evidence/candidate-anomalib-log.txt) | n/a |
| C3 Nontrivial source + refactoring | **Y** - 5,796 commits of accumulated Python. The project publishes its own debt policy in [`AGENTS.md`](AGENTS.md) ("Delete > Replace > Add"; PRs over 50 net added lines treated as high-barrier exceptions), giving a *declared* standard to measure against rather than an invented one | **Y** - large, with many near-parallel model definitions (duplication/clone-detection study potential) | **Y** *(measured)* - large Lightning-based codebase, and on import it emits `FutureWarning`s about **its own internals**: `anomalib.models.components.dinov2` is deprecated in favour of a timm-based extractor, yet another Anomalib module still imports it. Self-referential debt, observed without running any tool | n/a |
| C4 Tests and expected-output **oracle** | **Y** - 12 modules in [`tests/`](tests/): `test_python.py`, `test_cli.py`, `test_engine.py`, `test_exports.py`, `test_cuda.py`, `test_solutions.py`, `test_integrations.py` and others, asserting shapes, CLI paths and export round-trips - functional oracles, not accuracy | **Y** - extensive but very slow parametrised suite; the project itself states its synthetic-tensor tests do not establish prediction accuracy | **Y** - model tests present | n/a |
| C5 AI/recommender **ground-truth** source and terms | **P** - bundled COCO8 inadmissible (data leakage - see notes); admissible alternative exists and is obtainable: COCO `val2017`, 5,000 held-out labelled images, annotations CC BY 4.0, ~1 GB. Not yet obtained | **P** *(measured)* - inference verified working (`minibus` 90.36% on `bus.jpg`), but accuracy is **uncomputable**: one unlabelled image has no reference label. Would require the ImageNet validation split (50,000 images, registration-gated, licence-restricted) | **Y in principle, blocked in practice** *(measured)* - MVTec AD supplies image-level labels **and** pixel masks, the strongest of the three; but `MVTecAD(category="bottle")` confirms the dataset is absent locally, several GB, CC BY-NC-SA 4.0 | n/a |
| C6 Evaluation procedure and metrics | **Y** *(measured)* - `yolo val` produced P, R, mAP50 and mAP50-95 per class against labels, documented at [modes/val](https://docs.ultralytics.com/modes/val/); confusion matrix and PR curves written to disk | **Y** *(measured)* - pretrained `resnet18` resolved its own preprocessing config and produced a calibrated 1000-way distribution in 81.7 ms CPU; top-1/top-5 accuracy is the documented metric once labels exist | **Y** *(measured)* - 35 anomaly-detection models via `list_models()`; PaDiM (2,782,784 params) and PatchCore (24,862,528 params) both instantiated; image- and pixel-level AUROC are the documented metrics | n/a |
| C7 Upstream GitHub history | **Y** - 5,796 commits on `upstream/main`; 63,323 stars, 11,984 forks, 75 open issues, last push 2026-11-12T13:33Z (`gh api repos/ultralytics/ultralytics`). Dense PR-per-commit linkage suitable for Lab #9 | **Y** - active history | **P** - active but lower volume than A | n/a |
| C8 CI/DevOps possibility | **Y** - 12 workflows in [`.github/workflows/`](.github/workflows/): `ci.yml`, `docker.yml`, `docs.yml`, `format.yml`, `publish.yml`, `fuzz.yml`, `links.yml`, `stale.yml`, `cla.yml`, `mirror.yml`, `conda-check-prs.yml`, `merge-main-into-prs.yml`. Several require secrets or non-default runners and will fail in a fork, so they must be reviewed before being enabled | **Y** - CI present | **Y** - CI present | n/a |
| C9 Laptop setup feasibility | **Y** *(measured)* - installed and both functionalities executed on this laptop (i7-13620H, 16 GB RAM, RTX 4050 6 GB): 84.2 ms/image inference on CPU, no GPU required | **Y** *(measured)* - 81.7 ms/image on CPU; 26 packages, no build step | **P** *(measured, confirmed)* - library installs and runs, but 73 packages, one source build, and an end-to-end measurement gated on a multi-gigabyte non-commercial dataset that cannot live in the fork | n/a |
| C10 Continuation to Labs 6-9 / credible question | **Y** - all four labs supported. Credible question for Lab #9: *do files with higher cyclomatic complexity attract more bug-fixing commits?* - answerable by joining Lab #6 complexity measurements to the 5,796-commit upstream history | **P** - strong on #6, #7 and #9; weakest exactly where it matters most, on #8, until the ground-truth problem is solved | **Y** - strong on #8 specifically, with higher setup and licence risk across the rest | n/a |

### Ground-truth verification notes

- **Candidate A (Ultralytics YOLO):** functional test assertions in [`tests/test_python.py`](tests/test_python.py) and 11 sibling modules; evaluation-mode specification at [docs.ultralytics.com/modes/val](https://docs.ultralytics.com/modes/val/). Detection label source: COCO-format bounding boxes. **The bundled `coco8.yaml` is not an admissible ground truth** - its own header in [`ultralytics/cfg/datasets/coco8.yaml`](ultralytics/cfg/datasets/coco8.yaml) declares it the "first 8 images from COCO train2017", i.e. images from the split the pretrained weights were trained on, divided 4 train / 4 val. Evaluating on them violates the held-out requirement; the measured `mAP50-95 = 0.631` is correspondingly inflated against the published YOLO11n figure for COCO `val2017` (official model card to be cited in Lab #8). In measurement terms this is **data leakage**. Train/test protocol for Lab #8: pretrained weights, no further training, evaluated on COCO `val2017` only. Data terms: annotations CC BY 4.0, images under Flickr terms per [cocodataset.org/#termsofuse](https://cocodataset.org/#termsofuse); stored outside the repository, not redistributed.
- **Candidate B (timm):** architecture tests operate on synthetic tensors and are therefore functional oracles only. **Verified by running it:** `resnet18` with pretrained weights classified `bus.jpg` as `minibus` at 90.36%, with all five top predictions being road vehicles - plausible output, 81.7 ms CPU. That confidence figure is *not* an accuracy measurement, and the gap is the point: with one unlabelled image, top-1/top-5 accuracy and error analysis are not merely unknown but uncomputable. Label source would be ImageNet validation annotations; protocol top-1/top-5 on the held-out split; data terms registration-gated and restrictive, which is why C5 scores P.
- **Candidate C (Anomalib):** model tests present as functional oracles. **Verified by running it:** 35 models available, PaDiM and PatchCore instantiate successfully on Python 3.14. Label source MVTec AD, providing binary anomaly labels *and* pixel-level segmentation masks; protocol per-category normal-only training with a held-out mixed test set; data terms CC BY-NC-SA 4.0, non-commercial, share-alike, explicitly not to be uploaded into a fork. `MVTecAD(category="bottle")` confirmed the dataset is **not present** on this machine and nothing was downloaded, so no anomaly-quality claim is made.
- **Candidate D:** not applicable.

### A measurement error recorded against myself

The first Anomalib model-catalogue probe failed with `ImportError: cannot import name 'get_available_models' from 'anomalib.models'`. The fault was in my probe script, which called an API absent from version 2.7.0; the correct entry point is `anomalib.models.list_models`. This is recorded because attributing a defect in the measuring instrument to the system under test would itself be a measurement error, and separating the two is the purpose of the exercise.

## Decision

- **Final SUT and short description:** Ultralytics YOLO, pinned at `v8.4.211`. A Python/PyTorch package implementing the YOLO family of real-time computer-vision models - object detection, instance and semantic segmentation, classification, pose and oriented boxes - with training, validation, benchmarking, export and a `yolo` command-line interface.
- **Why it is better suited than rejected alternatives:** it is the only shortlisted candidate scoring Y on C2, C3, C4, C6, C7, C8, C9 and C10 simultaneously, so one system carries all four remaining laboratories instead of being strong in one and thin elsewhere. Lab #6 needs non-trivial code with a declared quality standard - satisfied by the codebase plus `AGENTS.md`; Lab #7 needs existing automation - satisfied by 12 workflows; Lab #9 needs mineable history - satisfied by 5,796 commits with dense PR linkage; Lab #8 needs a documented metric against labels - satisfied by `yolo val`, verified locally, leaving only the dataset to supply. The comparison also showed that the three candidates answer **different questions** on identical input: on `bus.jpg`, YOLO localised `4 persons, 1 bus` with boxes in 84.2 ms, timm reduced the whole image to `minibus` (90.36%) in 81.7 ms and never registered the people, and Anomalib could not answer at all without a corpus defining "normal". Detection gives the richest object-level signal to investigate.
- **Rejected alternatives and reasons:** *timm* - rejected on C5 and C10, after testing rather than on assumption. Its install was the cleanest of the three (26 packages, no build step) and its code and history are comparable, but credible classification ground truth means the ImageNet validation split, a larger and more licence-encumbered obstacle than labelled detection data, and that weakens Lab #8 specifically. *Anomalib* - rejected on C1 and C9, not on merit, and with its C2 score revised **upwards** after testing disproved the catalogue's version-compatibility warning. It has the best ground truth of the three (labels plus pixel masks), but the non-commercial MVTec AD licence constrains what may be stored and shown, it pulls 73 packages including a source build, and an end-to-end run is gated on a multi-gigabyte download.
- **Backup SUT and trigger for switching:** Anomalib. Switch triggers: (i) COCO `val2017` proves unobtainable or its terms incompatible, leaving Lab #8 without ground truth; (ii) the AGPL-3.0 licence is judged by the instructor to conflict with an intended laboratory activity; (iii) an unresolvable environment regression. Anomalib's installability on this machine is now verified, which de-risks the switch. Decision point: before the start of Lab #8.
- **Biggest unresolved risk / mitigation:** Lab #8 currently has **no admissible ground truth on disk** - the only labelled data present is COCO8, drawn from training images, which cannot support an accuracy claim. Mitigation: obtain COCO `val2017` early via a validation-only dataset configuration, since the stock `coco.yaml` download script also fetches `train2017.zip` (19 GB, not needed and to be excluded); store it outside the repository; and confirm the measured mAP against the official model-card figure as a reproducibility check. Fallback if bandwidth or disk is insufficient: a smaller labelled detection subset with verified licence terms.

## Repository provenance and pair access

- **Original upstream repo URL:** https://github.com/ultralytics/ultralytics
- **Selected original tag (if any):** `v8.4.211`, tagged 2026-11-12, commit `d2b7876e79ad2e02fd77221622774b511a8f0cb3`
- **Fork URL:** https://github.com/yar01110/ultralytics
- **Working branch:** `semester-investigation` → https://github.com/yar01110/ultralytics/tree/semester-investigation
- **Git and runtime versions:** git 2.51.0.windows.2 · Python 3.14.0 · torch 2.15.0+cpu · torchvision 0.29.2+cpu · ultralytics 8.4.211 · Windows 11 (26200), i7-13620H, 16 GB RAM, RTX 4050 6 GB (CUDA build not installed; CPU wheel in use, sufficient for Lab #5)
- **Applicable code licence (link + note):** AGPL-3.0 - [`LICENSE`](LICENSE) in the fork, unmodified, and declared in [`pyproject.toml`](pyproject.toml). Copyleft, not use-restricting: forking, modification, measurement and reporting are permitted. The fork remains public and AGPL-licensed; no modified version will be redistributed in closed form or served to third parties over a network, so the network clause is not engaged.
- **External dataset licence/limits:** COCO8 (bundled, ~1 MB) downloaded automatically to `C:\Users\lolag\Desktop\peak\datasets`, outside the repository. COCO `val2017`, required for Lab #8, not yet obtained: annotations CC BY 4.0, images under Flickr terms, research use permitted, redistribution not. MVTec AD (backup candidate) is CC BY-NC-SA 4.0 and was deliberately not downloaded. No dataset or model weight is committed - the root `.gitignore` already excludes `/datasets` and `*.pt`.
- **Partner collaborator invitation accepted? (pair only):** not applicable.

## Actual execution - not just installation

| Check | Official documentation link | Exact local command / path + input | Observed output / short log + evidence link | Status |
|---|---|---|---|---|
| Install/build source-aware baseline | [docs.ultralytics.com/quickstart](https://docs.ultralytics.com/quickstart/) | `cd C:\Users\lolag\Desktop\peak\ultralytics`; `python -m venv .venv`; `.\.venv\Scripts\Activate.ps1`; `python -m pip install -e .` | Editable install completed. `python -c "import ultralytics; print(ultralytics.__file__)"` → `C:\Users\lolag\Desktop\peak\ultralytics\ultralytics\__init__.py`; `pip list` reports `ultralytics 8.4.211 C:\Users\lolag\Desktop\peak\ultralytics`. Log: [`lab5-evidence/terminal-log.txt`](lab5-evidence/terminal-log.txt) | **Success** |
| Functionality 1 (real behaviour) | [docs.ultralytics.com/modes/predict](https://docs.ultralytics.com/modes/predict/) | `yolo predict model=yolo11n.pt source=https://ultralytics.com/images/bus.jpg` (input: official sample image, 640x480) | `4 persons, 1 bus, 84.2ms`; 7.3 ms preprocess / 84.2 ms inference / 30.8 ms postprocess on CPU; annotated image written to `runs/detect/predict-2`. Evidence: [`lab5-evidence/functionality1-predict-bus.jpg`](lab5-evidence/functionality1-predict-bus.jpg) | **Success** |
| Functionality 2 (different behaviour) | [docs.ultralytics.com/modes/val](https://docs.ultralytics.com/modes/val/) | `yolo val model=yolo11n.pt data=coco8.yaml` (input: bundled COCO8 validation split, 4 images, 17 instances, 6 classes) | `all 4 17 P=0.57 R=0.85 mAP50=0.854 mAP50-95=0.631`, with per-class rows (person 0.273, dog 0.697, horse 0.671, elephant 0.256, umbrella 0.995, potted plant 0.895); confusion matrix and PR curves written to `runs/detect/val-2`. Evidence: [`lab5-evidence/functionality2-confusion-matrix.png`](lab5-evidence/functionality2-confusion-matrix.png), [`lab5-evidence/functionality2-PR-curve.png`](lab5-evidence/functionality2-PR-curve.png), [`lab5-evidence/functionality2-predictions.jpg`](lab5-evidence/functionality2-predictions.jpg) vs [`lab5-evidence/functionality2-groundtruth-labels.jpg`](lab5-evidence/functionality2-groundtruth-labels.jpg) | **Success (plumbing verified; not a performance measurement - see ground-truth notes)** |

The two functionalities are deliberately different in kind: the first *produces* predictions, the
second *scores* predictions against labels, exercising the label loader, the matching logic and
the metric computation. Candidates B and C were additionally installed and executed on the same
laptop, in separate virtual environments outside the fork; their documentation links, exact
commands and observed outputs are recorded in
[`lab5-evidence/candidate-timm-log.txt`](lab5-evidence/candidate-timm-log.txt) and
[`lab5-evidence/candidate-anomalib-log.txt`](lab5-evidence/candidate-anomalib-log.txt).

- **Is the installed code from the local source fork, or only a separately installed wheel/image?**
  From the local source fork. `ultralytics.__file__` resolves to `C:\Users\lolag\Desktop\peak\ultralytics\ultralytics\__init__.py`, inside the working copy, and `pip list` reports a source path in place of a plain version - the signature of an editable (`pip install -e .`) install. No wheel or container image is involved. This is a prerequisite for Labs #6-#8: source edits in the fork take effect on the next run with no reinstall, so refactorings are actually exercised by the code that runs.
- **Blockers and fallback date/action:** none blocking. Two open items, neither on today's critical path. (1) COCO `val2017` is not yet downloaded - required before Lab #8, action by the first session of Lab #8, fallback a smaller licence-verified labelled subset. (2) PyTorch is the CPU build, so the RTX 4050 is idle - a one-command reinstall from the CUDA index resolves it; needed only when Lab #8 validation runtime becomes inconvenient, as Labs #6, #7 and #9 require no GPU at all.

## Approval / action

- **Instructor status:** Pending
- **Changes needed before Lab #6:** none identified pending approval. Planned preparatory work: fix the module scope for static analysis (an unscoped sweep of this codebase would be shallow), define an independent lint ruleset rather than inheriting the project's own Ruff configuration, which already suppresses many rules and would otherwise measure their configuration instead of the code, and add `QUALITY_INVESTIGATION.md` with the Lab #6 measurement goals.
- **Date of record:** 2026-11-12
