# Lab #6 (Software Quality and Metrics) - characterization test for the Kalman filter refactoring.
#
# The golden file tests/lab6_kalman_golden.npz was generated from the PRE-refactoring baseline revision with:
#     python tests/test_lab6_kalman.py --regenerate
# The test then requires every public Kalman filter method to return bit-identical arrays (same values, same dtype)
# for a fixed set of seeded inputs. This establishes numerical equivalence for these inputs only; it is not a proof of
# behavior preservation for every possible input.

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

from ultralytics.trackers.utils.kalman_filter import KalmanFilterXYAH, KalmanFilterXYWH

GOLDEN = Path(__file__).parent / "lab6_kalman_golden.npz"
FILTERS = {"xyah": KalmanFilterXYAH, "xywh": KalmanFilterXYWH}


def _boxes(kind: str, rng: np.random.Generator, n: int) -> np.ndarray:
    """Return n plausible (x, y, a, h) or (x, y, w, h) measurements."""
    xy = rng.uniform(0, 640, size=(n, 2))
    third = rng.uniform(0.2, 3.0, size=(n, 1)) if kind == "xyah" else rng.uniform(4, 300, size=(n, 1))
    h = rng.uniform(4, 300, size=(n, 1))
    return np.hstack([xy, third, h])


def compute_outputs() -> dict[str, np.ndarray]:
    """Run every public Kalman filter method on seeded inputs and collect the results."""
    out = {}
    for kind, cls in FILTERS.items():
        kf = cls()
        rng = np.random.default_rng(2026)
        boxes = _boxes(kind, rng, 6)
        means, covs = [], []
        for i, box in enumerate(boxes):
            mean, cov = kf.initiate(box)
            out[f"{kind}_initiate_mean_{i}"], out[f"{kind}_initiate_cov_{i}"] = mean, cov
            mean, cov = kf.predict(mean, cov)
            out[f"{kind}_predict_mean_{i}"], out[f"{kind}_predict_cov_{i}"] = mean, cov
            for tag, conf in (("noconf", None), ("conf", 0.83)):
                pm, pc = kf.project(mean, cov, confidence=conf)
                out[f"{kind}_project_{tag}_mean_{i}"], out[f"{kind}_project_{tag}_cov_{i}"] = pm, pc
            measurement = box + rng.normal(0, 2, size=4)
            for tag, conf in (("noconf", None), ("conf", 0.31)):
                um, uc = kf.update(mean, cov, measurement, confidence=conf)
                out[f"{kind}_update_{tag}_mean_{i}"], out[f"{kind}_update_{tag}_cov_{i}"] = um, uc
            means.append(mean)
            covs.append(cov)

        # Vectorized prediction over all tracks, as used by the trackers' multi_predict loops.
        mm, mc = kf.multi_predict(np.asarray(means), np.asarray(covs))
        out[f"{kind}_multi_predict_mean"], out[f"{kind}_multi_predict_cov"] = mm, mc

        # Gating distance with both metrics and both position modes.
        mean, cov = means[0], covs[0]
        candidates = _boxes(kind, rng, 5)
        for metric in ("maha", "gaussian"):
            for only_position in (False, True):
                out[f"{kind}_gating_{metric}_{only_position}"] = kf.gating_distance(
                    mean, cov, candidates, only_position=only_position, metric=metric
                )

        # Non-float64 state (callers may pass float32); locks in the resulting dtype and values.
        mean32 = np.asarray(means[1], dtype=np.float32)
        out[f"{kind}_predict_f32_mean"], out[f"{kind}_predict_f32_cov"] = kf.predict(mean32, covs[1])
        out[f"{kind}_multi_predict_f32_mean"], out[f"{kind}_multi_predict_f32_cov"] = kf.multi_predict(
            np.asarray(means, dtype=np.float32), np.asarray(covs)
        )
    return {k: np.asarray(v) for k, v in out.items()}


def test_golden_file_present():
    """The golden master must exist; it is generated once from the baseline revision."""
    assert GOLDEN.is_file(), f"missing {GOLDEN}; generate it on the baseline revision"


@pytest.mark.parametrize("kind", sorted(FILTERS))
def test_kalman_outputs_match_baseline(kind):
    """Every Kalman filter output is bit-identical (value and dtype) to the pre-refactoring baseline."""
    golden = np.load(GOLDEN)
    actual = compute_outputs()
    keys = sorted(k for k in golden.files if k.startswith(kind))
    assert keys, "golden file has no entries for this filter"
    assert sorted(k for k in actual if k.startswith(kind)) == keys
    for key in keys:
        assert actual[key].dtype == golden[key].dtype, f"{key}: dtype {actual[key].dtype} != {golden[key].dtype}"
        np.testing.assert_array_equal(actual[key], golden[key], err_msg=key)


if __name__ == "__main__" and "--regenerate" in sys.argv:
    np.savez(GOLDEN, **compute_outputs())
    print(f"wrote {GOLDEN} ({len(np.load(GOLDEN).files)} arrays)")
