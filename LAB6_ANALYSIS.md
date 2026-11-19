# Lab #6 - Investigation Record

**Team / student(s):** Nidhal Karchoud - [@yar01110](https://github.com/yar01110)  
**Mode:** individual  
**Approved upstream project:** https://github.com/ultralytics/ultralytics (Ultralytics YOLO, AGPL-3.0)  
**Fork / working branch:** https://github.com/yar01110/ultralytics/tree/semester-investigation  
**Original Lab #5 version:** `d2b7876e79ad2e02fd77221622774b511a8f0cb3` (upstream tag `v8.4.211`, see [`LAB5_SELECTION.md`](LAB5_SELECTION.md)); Lab #5 record commit [`b6f53ded7b82437f25e2be3f6490ec839448e85f`](https://github.com/yar01110/ultralytics/commit/b6f53ded7b82437f25e2be3f6490ec839448e85f)  
**Lab #6 pre-refactoring baseline:** _pending - SHA of the commit that adds this file_ (adds only Lab #6 workflows, this record and a characterization test; the `ultralytics/` source tree is byte-identical to `b6f53ded`)

> Keep this file short and evidence-based. Every analysis/test link points to the fork's GitHub Actions runs.

## Task 1 - Stakeholder, GQM, and Code Smell Selection

**Selected stakeholder and exact fictional concern from handout:** Scenario B - Maya, Technical-Debt Manager:
"We have limited development time, and some implementation choices could make future changes more expensive. We cannot improve everything. Please investigate suspected technical debt, compare its likely impact and the effort to address it, and justify which small improvements are worth making now."

**GQM goal:** Analyze **the handwritten Python source of the `ultralytics/` package** for the purpose of **identifying and prioritizing technical debt worth repaying now**, with respect to **maintainability, i.e. the cost of future change caused by duplication and complexity**, from the viewpoint of **Maya, the technical-debt manager**, in the context of **an individual MSc lab with a few hours of effort on a fork of a fast-evolving open-source computer-vision library (upstream > 5,700 commits)**.

| Initial question | Question wording | Relevant metric(s) / observation(s) | Why useful? |
|---|---|---|---|
| **Q1** | Where in `ultralytics/` are duplication and complexity symptoms concentrated? | jscpd clones and duplicated lines (per file, total %); Ruff C901 cyclomatic complexity per function, PLR0912 branches, PLR0915 statements, PLR0913 parameters; radon CC/MI for the file finally refactored | Locates *candidate* debt. On its own it says nothing about cost - a complex function nobody changes charges no interest |
| **Q2** | Which of those symptoms sit in code that is actually changing, so the debt is already charging interest, and what would repayment cost? | Commits touching the file in the last 12 months (`git log --since`); number of recent commits that had to apply the **same edit to several clone instances**; number of dependent modules; estimated lines to change and whether a cheap, exact regression check is possible | Turns "warning count" into Maya's trade-off: likely future cost (interest) vs repayment effort and behavior risk |

**Code-smell types chosen from the lecture** (slide 32, "Major smells in object oriented programming"; individual: 4, from three of its five groups):

| Smell type | Lecture slide(s) | Why relevant to our GQM? | How we plan to investigate it (tool/rule/metric/inspection) |
|---|---|---|---|
| 1. Duplicated Code | 32 - *Dispensables* | Every duplicated fragment must be changed N times; directly raises future change cost (Q1, Q2) | **Automatic**: jscpd on GitHub Actions (clone fragments, counts) + source inspection to separate real from incidental clones |
| 2. Long Method | 32 - *Bloaters* ("also Brain method") | Long, branchy methods are expensive to understand and modify; size/complexity is Q1's main proxy | **Metric-based**: Ruff C901 (CC > 10), PLR0912, PLR0915; radon CC |
| 3. Long Parameter List | 32 - *Bloaters* | Many parameters can make call sites fragile and APIs hard to evolve | **Automatic rule**: Ruff PLR0913 (> 5 args) + inspection of whether parameters are optional keyword options |
| 4. Shotgun Surgery | 32 - *Change preventers* | One logical change spread over many places is the clearest observable "interest" payment (Q2) | **Manual inspection with GitHub-visible evidence**: no linter rule exists; upstream commit history showing the same edit repeated in several places, linked to commits |

**Primary GitHub-integrated tool:** jscpd 4.3.0 on GitHub Actions ([jscpd](https://github.com/kucherenko/jscpd)) - workflow [`.github/workflows/lab6-duplication.yml`](.github/workflows/lab6-duplication.yml)  
**Complementary tool (only if needed):** Ruff 0.14.4 + radon 6.0.1 on GitHub Actions ([Ruff rules](https://docs.astral.sh/ruff/rules/), [radon](https://radon.readthedocs.io/)) - workflow [`.github/workflows/lab6-python-ruff.yml`](.github/workflows/lab6-python-ruff.yml); git history for Shotgun Surgery.  
**Why these tools match our questions and selected smells:** jscpd detects Duplicated Code directly; Ruff's C901/PLR09xx rules give the size/complexity/parameter metrics for Long Method and Long Parameter List. Neither detects Shotgun Surgery, so Q2 is answered with change history, which is also what Maya needs to estimate interest. Everything runs on GitHub-hosted runners against the pushed commit, so results are tied to a SHA.

## Task 2 - Detect and Investigate Code Smells

**Analysis configuration:**

- Fork branch and **baseline SHA**: `semester-investigation` @ _pending (see header)_
- Source directory analyzed: `ultralytics/` (handwritten Python; 46,160 lines in jscpd's count)
- Exclusions: `tests/`, `docs/`, `examples/`, `docker/` and all non-Python files (outside the GQM object). No `.pyx`/Cython or generated code exists under `ultralytics/`.
- Tools and settings: jscpd 4.3.0 `--format python --min-lines 5 --min-tokens 50`; Ruff 0.14.4 `--isolated --select C901,PLR0912,PLR0913,PLR0915` (Ruff defaults: CC > 10, branches > 12, statements > 50, args > 5); radon 6.0.1 `cc`, `mi`, `raw` on the refactored file. Identical settings before and after.
- **Baseline GitHub scan / Actions run link(s):** _pending: Lab6 - Duplication run, Lab6 - Python Ruff run_

| Selected smell type | Found / not found / not assessable | Tool result or source link | Interpretation / limitations |
|---|---|---|---|
| Duplicated Code | **Found** - 35 clones, 378 duplicated lines (0.82 %) | jscpd run (pending link). Largest: `sam3/encoder.py` (29 lines, intra-file), **`trackers/utils/kalman_filter.py` (4 clones, 90 lines)**, `trackers/utils/gmc.py` (21 + 9 lines), `sam/build.py` vs `build_sam3.py` (21) | Low overall %, but concentrated. Token-based clones can be incidental (e.g. similar `nn.Module` boilerplate in SAM); each needs inspection |
| Long Method | **Found** - 93 × C901, 61 × PLR0912, 59 × PLR0915 | Ruff run (pending link). Worst: `Exporter.__call__` CC **88**, 459 lines ([source](https://github.com/yar01110/ultralytics/blob/b6f53ded7b82437f25e2be3f6490ec839448e85f/ultralytics/engine/exporter.py#L649-L1107)); `_convert_ndjson_to_yolo` CC 67; `BaseTrainer._do_train` CC 42 | CC counts decision points, not difficulty; a long `if format == ...` dispatcher inflates CC while each branch is simple |
| Long Parameter List | **Found by rule** - 230 × PLR0913 | Ruff run (pending link), e.g. `plot_images` (13 params) | Mostly optional keyword options with defaults; see challenged warning below |
| Shotgun Surgery | **Found (reasoned candidate)** - in the Kalman filter | 3 upstream commits applied the *same* edit to both Kalman classes: [`ea521665`](https://github.com/ultralytics/ultralytics/commit/ea5216656ea003a7b684986ebce03bf27e6663fb) (float64 cast, 2 copies), [`f4930e56`](https://github.com/ultralytics/ultralytics/commit/f4930e56d54b28f0710230b97363d3c147f484df) (slicing in `project`/`multi_predict`, 2 copies each), [`2e0fd58a`](https://github.com/ultralytics/ultralytics/commit/2e0fd58a7a840f09a8b932d5b971cc5fe488a4b1) (NSA-Kalman confidence in `project`/`update`, 2 copies each) | Not tool-detected; inferred from history. It is a *consequence* of the duplication, not a separate design problem |

**Candidate issues inspected in source (at least two):**

| Candidate ID | File/entity permalink | What was actually observed? | Why it might matter / why uncertain |
|---|---|---|---|
| C1 | [`KalmanFilterXYWH`](https://github.com/yar01110/ultralytics/blob/b6f53ded7b82437f25e2be3f6490ec839448e85f/ultralytics/trackers/utils/kalman_filter.py#L289-L485) vs [`KalmanFilterXYAH`](https://github.com/yar01110/ultralytics/blob/b6f53ded7b82437f25e2be3f6490ec839448e85f/ultralytics/trackers/utils/kalman_filter.py#L57-L199) | The subclass re-implements `initiate`, `predict`, `project`, `multi_predict` in full and overrides `update` only to call `super()`. The **only** real difference is which box dimension scales the noise std: XYAH uses height for x, y, h and a constant for the aspect ratio; XYWH uses width/height. The filter algebra (covariance propagation, NSA scaling, slicing) is copied verbatim. | Plausible maintainability concern, confirmed by history: 3 of the last 7 code-changing commits had to edit both copies. A fix applied to only one class would silently diverge ByteTrack/OC-SORT/FastTracker (XYAH) from BoT-SORT/TrackTrack (XYWH). Uncertain: the file changes only ~11×/year |
| C2 | [`Exporter.__call__`](https://github.com/yar01110/ultralytics/blob/b6f53ded7b82437f25e2be3f6490ec839448e85f/ultralytics/engine/exporter.py#L649-L1107) | 459-line method, CC 88: argument validation, device/format checks, model preparation, a format dispatch chain for ~20 export backends and metadata writing in one body. | Real Long Method and the most-changed file (227 commits in 12 months), so interest is high. But much of the CC comes from a flat per-format dispatch; the size reflects many supported formats rather than tangled logic |
| C3 (optional) | [`GMC.apply_sparseoptflow`](https://github.com/yar01110/ultralytics/blob/b6f53ded7b82437f25e2be3f6490ec839448e85f/ultralytics/trackers/utils/gmc.py#L288-L349) vs [`apply_features`](https://github.com/yar01110/ultralytics/blob/b6f53ded7b82437f25e2be3f6490ec839448e85f/ultralytics/trackers/utils/gmc.py#L165-L286) | jscpd: 21 + 9 duplicated lines (L265-284 vs L328-348, L183-190 vs L304-312) - both end with the same "filter matched points, `estimateAffinePartial2D`, rescale by downscale" block. | Smaller real clone; the two methods are different algorithms (ORB/SIFT vs optical flow) sharing a tail. Lower impact than C1 |

**One warning we challenged:** Ruff PLR0913 reports **230** "too many arguments" findings, e.g. [`plot_images`](https://github.com/yar01110/ultralytics/blob/b6f53ded7b82437f25e2be3f6490ec839448e85f/ultralytics/utils/plotting.py#L881-L895) with 13 parameters. On inspection, 12 of the 13 are optional keyword options with defaults (`max_size`, `conf_thres`, `show_conf`, ...) documented in the docstring; callers pass only what they need. PLR0913 counts defaulted options exactly like required positional arguments, so it measures "how configurable is this function", not "how fragile are its call sites". We treat most of these as **likely false alarms for the Long Parameter List smell** and did not prioritise them. Conversely, the duplication tool is the **only** tool that sees C1: radon rates `kalman_filter.py` grade **A** (average CC 1.57, MI 49.8), so a complexity-only investigation would have missed it entirely.

## Task 3 - Prioritize Technical Debt and Plan Refactoring

| Candidate | Expected future impact / relevance | Estimated effort and behavior risk | Prioritize now or defer? Why? |
|---|---|---|---|
| C1 Kalman duplication | **Interest observed, not guessed**: 3 recent commits paid it (double edits). Shared by 5 trackers, so a missed second copy is a silent behavior split between tracker families. Medium change frequency (11 commits / 12 months) | **Low**: ~90 duplicated lines in one file, pure NumPy, no I/O. Risk is numerical drift, but it can be checked **exactly** (bit-identical golden master) on a CPU runner in seconds | **Now** - best impact/effort ratio, and verifiable |
| C2 `Exporter.__call__` | Highest change frequency (227 commits / 12 months) so likely the highest absolute interest | **High**: ~460 lines, ~20 backends (ONNX, TensorRT, CoreML, TFLite, ...); a faithful regression check needs heavy optional deps, GPUs and weights - against the lab rules. Upstream also edits it daily, so a fork-local refactor would conflict immediately | **Defer** - biggest warning, but repayment cost and risk exceed a lab-sized budget. Recommend an upstream-coordinated Extract Method per format group |
| C3 GMC duplicated tail | Low: 2 call sites in one class, 14 commits / 12 months, no repeated edits observed | Low effort, but verifying needs image fixtures for OpenCV paths | **Defer** - real but cheap to live with |

**Selected documented issue(s) and individual ownership:**

| Contributor / GitHub handle | Candidate ID | Planned refactoring | Expected benefit | GitHub regression check planned |
|---|---|---|---|---|
| Nidhal Karchoud / @yar01110 | C1 | **Form Template Method / Pull Up Method + Extract Method**: keep one implementation of `initiate`, `predict`, `project`, `multi_predict`, `update` in `KalmanFilterXYAH`; extract the only varying part into a hook `_box_std(box, weight, fixed)`; `KalmanFilterXYWH` overrides just that hook | A future change to the filter algebra is made once instead of twice; the difference between the two filters becomes explicit (one 6-line method) | [`lab6-tests.yml`](.github/workflows/lab6-tests.yml): (1) golden master [`tests/test_lab6_kalman.py`](tests/test_lab6_kalman.py) generated on the baseline - 164 arrays, bit-identical value+dtype; (2) Kalman doctests; (3) upstream tracker tests in `tests/test_python.py` (ByteTrack, BoT-SORT, OC-SORT, Deep OC-SORT, TrackTrack) |

## Task 4 - Refactor, Verify, and Commit

**Baseline test/check run(s) on GitHub:** _pending_  
**After-refactoring SHA(s):** _pending_  
**After-refactoring scan / workflow run(s):** _pending_  
**After-refactoring test/check run(s):** _pending_

| Issue / contributor | Before (same scope and measurement) | After | Test / verification result | What does this actually establish? |
|---|---|---|---|---|
| C1 / @yar01110 | _pending_ | _pending_ | _pending_ | _pending_ |

**Answers to the original GQM questions:**

- **Q1:** _pending_
- **Q2:** _pending_

**Conclusion and limits:** _pending_

### Individual implementation commits - permanent GitHub links

| Contributor / GitHub account | Documented issue (C1, C2, ...) | What was refactored? | **Permanent commit link** | PR or GitHub Actions push-run link |
|---|---|---|---|---|
| Nidhal Karchoud / @yar01110 | C1 | _pending_ | _pending_ | _pending_ |

**Completed template location on `semester-investigation`:** https://github.com/yar01110/ultralytics/blob/semester-investigation/LAB6_ANALYSIS.md  
**Template/report commit link:** _pending_

**Evidence preservation note:** _pending_
