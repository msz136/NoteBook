#!/usr/bin/env python3
"""Small, deterministic M03 estimator comparison using a synthetic panel."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def ols(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    return np.linalg.lstsq(x, y, rcond=None)[0]


def gaussian_mle(y: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, float]:
    beta = ols(y, x)
    sigma2 = float(np.mean((y - x @ beta) ** 2))
    return beta, sigma2


def exactly_identified_gmm(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    # E[x (y - x'b)] = 0; with full-rank X this is the OLS normal equation.
    return np.linalg.solve(x.T @ x, x.T @ y)


def bootstrap_ols(y: np.ndarray, x: np.ndarray, reps: int = 400, seed: int = 20260722) -> dict:
    rng = np.random.default_rng(seed)
    n = len(y)
    estimates = np.empty((reps, x.shape[1]))
    for i in range(reps):
        idx = rng.integers(0, n, size=n)
        estimates[i] = ols(y[idx], x[idx])
    return {
        "reps": reps,
        "seed": seed,
        "mean": estimates.mean(axis=0).tolist(),
        "ci_percentile_95": np.quantile(estimates, [0.025, 0.975], axis=0).T.tolist(),
    }


def main() -> int:
    rng = np.random.default_rng(314159)
    n = 240
    x1 = rng.normal(size=n)
    x = np.column_stack([np.ones(n), x1])
    hetero_scale = 0.35 + 0.65 * np.abs(x1)
    y = 0.7 + 1.8 * x1 + rng.normal(size=n) * hetero_scale
    beta_ols = ols(y, x)
    beta_mle, sigma2 = gaussian_mle(y, x)
    beta_gmm = exactly_identified_gmm(y, x)
    result = {
        "n": n,
        "true_beta": [0.7, 1.8],
        "ols_beta": beta_ols.tolist(),
        "mle_beta": beta_mle.tolist(),
        "mle_sigma2": sigma2,
        "gmm_beta": beta_gmm.tolist(),
        "max_ols_mle_abs_diff": float(np.max(np.abs(beta_ols - beta_mle))),
        "max_ols_gmm_abs_diff": float(np.max(np.abs(beta_ols - beta_gmm))),
        "bootstrap": bootstrap_ols(y, x),
        "robust_se_note": "Heteroskedasticity is injected; conventional homoskedastic SE is not treated as reliable.",
    }
    out = Path(__file__).resolve().parents[1] / "data" / "m03_estimator_comparison.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
