# Lab #6 - Where each code smell was found (tool evidence)

Companion to [`LAB6_ANALYSIS.md`](LAB6_ANALYSIS.md). Lists **every location the tools reported** for the four smell types selected from lecture slide 32, with links to the exact source lines and to the GitHub Actions runs that produced them.

- **Before** = baseline commit [`2ac6f4f0`](https://github.com/yar01110/ultralytics/commit/2ac6f4f07acb447f294593236fbff8f83ab51678) (YOLO source identical to the Lab #5 version). Source links below point to this commit.
- **After** = refactoring commit [`70ec9b89`](https://github.com/yar01110/ultralytics/commit/70ec9b894192c40b35300bb1daf8af52739b0289) (only `ultralytics/trackers/utils/kalman_filter.py` changed).
- Scope: `ultralytics/` package only, same tool versions and settings before and after (see [`.github/workflows/`](.github/workflows/)).

## Where to see the raw tool output on GitHub

| Smell | Tool | Before (2ac6f4f0) | After (70ec9b89) | Where in the run |
|---|---|---|---|---|
| Duplicated Code | jscpd 4.3.0 | [run](https://github.com/yar01110/ultralytics/actions/runs/44542809092) - [log](https://github.com/yar01110/ultralytics/actions/runs/44542809092/job/135625366912#step:4:1) | [run](https://github.com/yar01110/ultralytics/actions/runs/44543083668) - [log](https://github.com/yar01110/ultralytics/actions/runs/44543083668/job/135626331730#step:4:1) | **Summary** page: clone table; **log** step 4 "Analyze duplication": every clone with file and lines; also [Security -> Code scanning](https://github.com/yar01110/ultralytics/security/code-scanning) (tool `jscpd`) |
| Long Method | Ruff 0.14.4 (C901, PLR0912, PLR0915) | [run](https://github.com/yar01110/ultralytics/actions/runs/44542809091) - [log](https://github.com/yar01110/ultralytics/actions/runs/44542809091/job/135625366614#step:4:1) | [run](https://github.com/yar01110/ultralytics/actions/runs/44543083336) - [log](https://github.com/yar01110/ultralytics/actions/runs/44543083336/job/135626331088#step:4:1) | **Summary** page: rule counts + top 15 complexity; artifact `lab6-ruff-report` -> `ruff.json`: every finding |
| Long Parameter List | Ruff 0.14.4 (PLR0913) | same run as above | same run as above | same as above (rule `PLR0913`) |
| Shotgun Surgery | git history (no tool rule exists) | upstream commits below | - | manual inspection of commit diffs |

## Summary: before vs after for all four smells

| Smell (slide 32 group) | Before | After | Change | Why |
|---|---|---|---|---|
| Duplicated Code (Dispensables) | 35 clones, 378 dup. lines (0.82 %); `kalman_filter.py`: 4 clones / 90 lines | 31 clones, 292 dup. lines (0.63 %); `kalman_filter.py`: **0** | **-4 clones, -86 lines** | The 4 removed clones are exactly the Kalman copies (C1); the other 31 are untouched |
| Long Method (Bloaters) | C901 93, PLR0912 61, PLR0915 59 | C901 93, PLR0912 61, PLR0915 59 | none | Not refactored (C2 `Exporter.__call__` deferred); `kalman_filter.py` had no findings |
| Long Parameter List (Bloaters) | PLR0913 230 | PLR0913 230 | none | Not refactored; mostly optional settings (challenged warning) |
| Shotgun Surgery (Change preventers) | Kalman algebra in 2 classes; 3 upstream commits edited both | Kalman algebra in 1 class | **2 places -> 1 place** | Consequence of removing the duplication (C1) |

## 1. Duplicated Code (jscpd)

Before: **35 clones, 378 duplicated lines (0.82 %)**. After: **31 clones, 292 duplicated lines (0.63 %)**.

| # | Lines | First fragment | Second fragment | After refactoring |
|---|---|---|---|---|
| 1 | 29 | [`models/sam/sam3/encoder.py:195-223`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/sam3/encoder.py#L195-L223) | [`models/sam/sam3/encoder.py:138-167`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/sam3/encoder.py#L138-L167) | still present |
| 2 | 29 | [`trackers/utils/kalman_filter.py:378-406`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/utils/kalman_filter.py#L378-L406) | [`trackers/utils/kalman_filter.py:118-146`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/utils/kalman_filter.py#L118-L146) | **removed (C1)** |
| 3 | 28 | [`trackers/utils/kalman_filter.py:410-437`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/utils/kalman_filter.py#L410-L437) | [`trackers/utils/kalman_filter.py:150-177`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/utils/kalman_filter.py#L150-L177) | **removed (C1)** |
| 4 | 23 | [`trackers/utils/kalman_filter.py:447-469`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/utils/kalman_filter.py#L447-L469) | [`trackers/utils/kalman_filter.py:187-209`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/utils/kalman_filter.py#L187-L209) | **removed (C1)** |
| 5 | 21 | [`trackers/utils/gmc.py:328-348`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/utils/gmc.py#L328-L348) | [`trackers/utils/gmc.py:265-284`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/utils/gmc.py#L265-L284) | still present |
| 6 | 21 | [`models/sam/build.py:283-303`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/build.py#L283-L303) | [`models/sam/build_sam3.py:317-337`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/build_sam3.py#L317-L337) | still present |
| 7 | 17 | [`models/sam/modules/memory_attention.py:88-104`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/modules/memory_attention.py#L88-L104) | [`models/sam/sam3/encoder.py:58-73`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/sam3/encoder.py#L58-L73) | still present |
| 8 | 15 | [`models/sam/modules/tiny_encoder.py:735-749`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/modules/tiny_encoder.py#L735-L749) | [`models/sam/modules/tiny_encoder.py:321-335`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/modules/tiny_encoder.py#L321-L335) | still present |
| 9 | 13 | [`models/yolo/classify/train.py:74-86`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/yolo/classify/train.py#L74-L86) | [`models/yolo/detect/train.py:155-167`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/yolo/detect/train.py#L155-L167) | still present |
| 10 | 12 | [`models/yolo/detect/val.py:534-545`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/yolo/detect/val.py#L534-L545) | [`models/yolo/obb/val.py:238-245`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/yolo/obb/val.py#L238-L245) | still present |
| 11 | 12 | [`models/sam/modules/decoders.py:417-428`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/modules/decoders.py#L417-L428) | [`models/sam/modules/decoders.py:152-163`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/modules/decoders.py#L152-L163) | still present |
| 12 | 11 | [`models/sam/modules/decoders.py:248-258`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/modules/decoders.py#L248-L258) | [`models/sam/modules/decoders.py:59-69`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/modules/decoders.py#L59-L69) | still present |
| 13 | 11 | [`nn/text_model.py:322-332`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/nn/text_model.py#L322-L332) | [`nn/text_model.py:234-244`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/nn/text_model.py#L234-L244) | still present |
| 14 | 10 | [`models/yolo/depth/train.py:121-130`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/yolo/depth/train.py#L121-L130) | [`models/yolo/semantic/train.py:143-152`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/yolo/semantic/train.py#L143-L152) | still present |
| 15 | 10 | [`trackers/utils/kalman_filter.py:470-479`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/utils/kalman_filter.py#L470-L479) | [`trackers/utils/kalman_filter.py:210-219`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/utils/kalman_filter.py#L210-L219) | **removed (C1)** |
| 16 | 10 | [`trackers/byte_tracker.py:438-447`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/byte_tracker.py#L438-L447) | [`trackers/fast_tracker.py:205-214`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/fast_tracker.py#L205-L214) | still present |
| 17 | 9 | [`models/yolo/world/train.py:85-93`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/yolo/world/train.py#L85-L93) | [`models/yolo/yoloe/train.py:70-79`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/yolo/yoloe/train.py#L70-L79) | still present |
| 18 | 9 | [`models/yolo/detect/val.py:475-483`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/yolo/detect/val.py#L475-L483) | [`models/yolo/obb/val.py:170-180`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/yolo/obb/val.py#L170-L180) | still present |
| 19 | 9 | [`trackers/utils/gmc.py:304-312`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/utils/gmc.py#L304-L312) | [`trackers/utils/gmc.py:183-190`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/utils/gmc.py#L183-L190) | still present |
| 20 | 8 | [`models/yolo/pose/val.py:211-218`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/yolo/pose/val.py#L211-L218) | [`models/yolo/segment/val.py:203-210`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/yolo/segment/val.py#L203-L210) | still present |
| 21 | 8 | [`models/yolo/detect/val.py:197-204`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/yolo/detect/val.py#L197-L204) | [`models/yolo/obb/val.py:129-136`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/yolo/obb/val.py#L129-L136) | still present |
| 22 | 8 | [`models/yolo/detect/val.py:494-501`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/yolo/detect/val.py#L494-L501) | [`models/yolo/segment/val.py:203-210`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/yolo/segment/val.py#L203-L210) | still present |
| 23 | 8 | [`models/sam/sam3/encoder.py:142-149`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/sam3/encoder.py#L142-L149) | [`models/sam/sam3/encoder.py:84-91`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/sam3/encoder.py#L84-L91) | still present |
| 24 | 8 | [`models/sam/modules/decoders.py:263-270`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/modules/decoders.py#L263-L270) | [`models/sam/modules/decoders.py:69-76`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/modules/decoders.py#L69-L76) | still present |
| 25 | 8 | [`models/rtdetr/train.py:84-91`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/rtdetr/train.py#L84-L91) | [`models/rtdetr/val.py:103-110`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/rtdetr/val.py#L103-L110) | still present |
| 26 | 7 | [`models/yolo/detect/val.py:525-531`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/yolo/detect/val.py#L525-L531) | [`models/yolo/obb/val.py:198-204`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/yolo/obb/val.py#L198-L204) | still present |
| 27 | 7 | [`models/sam/modules/tiny_encoder.py:941-947`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/modules/tiny_encoder.py#L941-L947) | [`models/sam/sam3/vitdet.py:497-503`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/sam3/vitdet.py#L497-L503) | still present |
| 28 | 7 | [`trackers/byte_tracker.py:157-163`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/byte_tracker.py#L157-L163) | [`trackers/byte_tracker.py:127-133`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/byte_tracker.py#L127-L133) | still present |
| 29 | 7 | [`trackers/byte_tracker.py:451-457`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/byte_tracker.py#L451-L457) | [`trackers/fast_tracker.py:217-222`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/fast_tracker.py#L217-L222) | still present |
| 30 | 7 | [`trackers/bot_sort.py:110-116`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/bot_sort.py#L110-L116) | [`trackers/byte_tracker.py:91-97`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/byte_tracker.py#L91-L97) | still present |
| 31 | 7 | [`solutions/heatmap.py:108-114`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/solutions/heatmap.py#L108-L114) | [`solutions/object_counter.py:189-195`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/solutions/object_counter.py#L189-L195) | still present |
| 32 | 6 | [`models/sam/sam3/text_encoder_ve.py:90-95`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/sam3/text_encoder_ve.py#L90-L95) | [`models/sam/sam3/text_encoder_ve.py:23-28`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/sam3/text_encoder_ve.py#L23-L28) | still present |
| 33 | 6 | [`models/sam/modules/decoders.py:389-394`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/modules/decoders.py#L389-L394) | [`models/sam/modules/decoders.py:135-140`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/modules/decoders.py#L135-L140) | still present |
| 34 | 6 | [`models/sam/modules/decoders.py:401-406`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/modules/decoders.py#L401-L406) | [`models/sam/modules/decoders.py:142-147`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/modules/decoders.py#L142-L147) | still present |
| 35 | 6 | [`nn/backends/litert.py:109-114`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/nn/backends/litert.py#L109-L114) | [`nn/backends/tensorflow.py:116-122`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/nn/backends/tensorflow.py#L116-L122) | still present |

## 2. Long Method (Ruff C901 / PLR0912 / PLR0915)

Before: C901 **93**, PLR0912 **61**, PLR0915 **59**. After: C901 **93**, PLR0912 **61**, PLR0915 **59** (unchanged - none of these is in `kalman_filter.py`).

Top 15 by cyclomatic complexity (thresholds: CC > 10, branches > 12, statements > 50):

| # | Function | Location | CC | Branches | Statements | Length (lines) |
|---|---|---|---|---|---|---|
| 1 | `Exporter.__call__` | [`engine/exporter.py:649-1107`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/engine/exporter.py#L649-L1107) | **88** | 88 | 263 | 459 |
| 2 | `_convert_ndjson_to_yolo` | [`data/converter.py:942-1249`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/data/converter.py#L942-L1249) | **67** | 44 | 205 | 308 |
| 3 | `BaseTrainer._do_train` | [`engine/trainer.py:472-717`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/engine/trainer.py#L472-L717) | **42** | 43 | 167 | 246 |
| 4 | `parse_model` | [`nn/tasks.py:2049-2258`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/nn/tasks.py#L2049-L2258) | **41** | 41 | 111 | 210 |
| 5 | `check_cfg` | [`cfg/__init__.py:398-537`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/cfg/__init__.py#L398-L537) | **39** | 39 | 73 | 140 |
| 6 | `plot_images` | [`utils/plotting.py:881-1080`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/utils/plotting.py#L881-L1080) | **37** | 37 | 124 | 200 |
| 7 | `safe_download` | [`utils/downloads.py:274-492`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/utils/downloads.py#L274-L492) | **37** | 42 | 131 | 219 |
| 8 | `onnx2engine` | [`utils/export/engine.py:236-497`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/utils/export/engine.py#L236-L497) | **36** | 31 | 108 | 262 |
| 9 | `entrypoint` | [`cfg/__init__.py:1029-1205`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/cfg/__init__.py#L1029-L1205) | **34** | 37 | 100 | 177 |
| 10 | `guess_model_task` | [`nn/tasks.py:2299-2384`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/nn/tasks.py#L2299-L2384) | **30** | 21 | - | 86 |
| 11 | `BasePredictor.stream_inference` | [`engine/predictor.py:351-521`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/engine/predictor.py#L351-L521) | **29** | 29 | 103 | 171 |
| 12 | `benchmark` | [`utils/benchmarks.py:73-294`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/utils/benchmarks.py#L73-L294) | **27** | 27 | 117 | 222 |
| 13 | `TRACKTRACK.update` | [`trackers/track_tracker.py:456-593`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/track_tracker.py#L456-L593) | **27** | 28 | 88 | 138 |
| 14 | `check_det_dataset` | [`data/utils.py:723-841`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/data/utils.py#L723-L841) | **27** | 30 | 79 | 119 |
| 15 | `BaseValidator.__call__` | [`engine/validator.py:217-389`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/engine/validator.py#L217-L389) | **25** | 27 | 103 | 173 |

## 3. Long Parameter List (Ruff PLR0913, more than 5 arguments)

Before: **230** findings. After: **230** (unchanged).

Top 15 by number of parameters, with how many of them are optional (have a default value):

| # | Function | Location | Parameters | Optional (defaulted) | Required |
|---|---|---|---|---|---|
| 1 | `SAM3Model.__init__` | [`models/sam/modules/sam.py:1044`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/modules/sam.py#L1044) | **35** | 32 | 3 |
| 2 | `SAM2Model.__init__` | [`models/sam/modules/sam.py:171`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/modules/sam.py#L171) | **35** | 32 | 3 |
| 3 | `ViT.__init__` | [`models/sam/sam3/vitdet.py:322`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/sam3/vitdet.py#L322) | **31** | 31 | 0 |
| 4 | `SAM3VideoSemanticPredictor.__init__` | [`models/sam/predict.py:2544`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/predict.py#L2544) | **24** | 24 | 0 |
| 5 | `TransformerDecoder.__init__` | [`models/sam/sam3/decoder.py:183`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/sam3/decoder.py#L183) | **22** | 15 | 7 |
| 6 | `Block.__init__` | [`models/sam/sam3/vitdet.py:219`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/sam3/vitdet.py#L219) | **17** | 15 | 2 |
| 7 | `TextTransformer.__init__` | [`models/sam/sam3/text_encoder_ve.py:152`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/sam3/text_encoder_ve.py#L152) | **17** | 17 | 0 |
| 8 | `TransformerDecoder.forward` | [`models/sam/sam3/decoder.py:349`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/sam3/decoder.py#L349) | **17** | 15 | 2 |
| 9 | `Results.plot` | [`engine/results.py:522`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/engine/results.py#L522) | **17** | 17 | 0 |
| 10 | `SAM3SemanticModel.__init__` | [`models/sam/sam3/sam3_image.py:37`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/sam3/sam3_image.py#L37) | **16** | 13 | 3 |
| 11 | `RTDETRDecoder.__init__` | [`nn/modules/head.py:1578`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/nn/modules/head.py#L1578) | **15** | 15 | 0 |
| 12 | `ImageEncoderViT.__init__` | [`models/sam/modules/encoders.py:48`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/modules/encoders.py#L48) | **15** | 15 | 0 |
| 13 | `BaseDataset.__init__` | [`data/base.py:117`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/data/base.py#L117) | **15** | 14 | 1 |
| 14 | `non_max_suppression` | [`utils/nms.py:13`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/utils/nms.py#L13) | **14** | 13 | 1 |
| 15 | `TinyViT.__init__` | [`models/sam/modules/tiny_encoder.py:787`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/models/sam/modules/tiny_encoder.py#L787) | **14** | 14 | 0 |

Across all 230 PLR0913 findings, **124** functions need at most 2 required arguments; the rest of their parameters are optional settings.

## 4. Shotgun Surgery (git history - manual inspection)

No linter has a rule for Shotgun Surgery, so the evidence is the change history: one logical change that had to be applied in several places. In `kalman_filter.py`, the same edit was made separately in [`KalmanFilterXYAH`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/utils/kalman_filter.py#L57-L199) and its copy [`KalmanFilterXYWH`](https://github.com/yar01110/ultralytics/blob/2ac6f4f07acb447f294593236fbff8f83ab51678/ultralytics/trackers/utils/kalman_filter.py#L289-L485):

| Upstream commit | Date | Same edit applied in | Places edited |
|---|---|---|---|
| [`ea521665`](https://github.com/ultralytics/ultralytics/commit/ea5216656ea003a7b684986ebce03bf27e6663fb) Declare the Kalman filter state dtype as float64 | 2026-07-29 | `initiate` of both classes (float64 cast) | 2 |
| [`f4930e56`](https://github.com/ultralytics/ultralytics/commit/f4930e56d54b28f0710230b97363d3c147f484df) Replace selection-matrix matmuls with direct slicing | 2026-08-13 | `project` and `multi_predict` of both classes | 4 |
| [`2e0fd58a`](https://github.com/ultralytics/ultralytics/commit/2e0fd58a7a840f09a8b932d5b971cc5fe488a4b1) Deduplicate tracker Kalman update and box helpers (NSA-Kalman) | 2026-06-25 | `project` and `update` of both classes | 4 |

**After** the refactoring each of these edits would be made **once**, in `KalmanFilterXYAH`; `KalmanFilterXYWH` only overrides the 2-line `_box_std` hook. This is inferred from history, not measured going forward.

## How to read these results (limits)

- A tool finding is a **symptom**, not a confirmed smell. Long Method and Long Parameter List counts were not changed by this lab and were not claimed as fixed.
- jscpd matches token sequences: some clones (e.g. SAM `nn.Module` boilerplate) may be acceptable similarity rather than design debt; only the Kalman clones were inspected in depth and confirmed.
- Ruff's PLR0913 counts optional keyword settings like required arguments (see the "Optional" column), which is why it was challenged in `LAB6_ANALYSIS.md`.
- GitHub Actions logs and artifacts expire; the tables in this file preserve the essential results.
