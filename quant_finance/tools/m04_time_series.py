#!/usr/bin/env python3
"""Deterministic, dependency-light M04 time-series smoke experiment."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

def ar1_fit(y: np.ndarray) -> tuple[float, float]:
    x = np.column_stack([np.ones(len(y)-1), y[:-1]])
    beta = np.linalg.lstsq(x, y[1:], rcond=None)[0]
    return float(beta[0]), float(beta[1])

def rolling_ar1(y: np.ndarray, train: int) -> tuple[np.ndarray, np.ndarray]:
    pred, actual = [], []
    for t in range(train, len(y)):
        a, phi = ar1_fit(y[:t])
        pred.append(a + phi * y[t-1]); actual.append(y[t])
    return np.asarray(pred), np.asarray(actual)

def var1_fit(y: np.ndarray) -> np.ndarray:
    x = np.column_stack([np.ones(len(y)-1), y[:-1]])
    return np.linalg.lstsq(x, y[1:], rcond=None)[0]

def ewma_variance(r: np.ndarray, lam: float = 0.94) -> np.ndarray:
    out = np.empty(len(r)); out[0] = r[0] ** 2
    for t in range(1, len(r)):
        out[t] = lam * out[t-1] + (1-lam) * r[t-1] ** 2
    return out

def local_level_filter(y: np.ndarray, q: float = 0.02, r: float = 0.08) -> np.ndarray:
    level, variance = y[0], 1.0; out = [level]
    for obs in y[1:]:
        pred_var = variance + q
        gain = pred_var / (pred_var + r)
        level = level + gain * (obs - level)
        variance = (1-gain) * pred_var
        out.append(level)
    return np.asarray(out)

def main() -> int:
    rng = np.random.default_rng(20260722)
    n = 260
    y = np.zeros(n); z = np.zeros(n)
    shocks = rng.normal(size=(n, 2))
    for t in range(1, n):
        y[t] = 0.15 + 0.72*y[t-1] + 0.12*z[t-1] + shocks[t,0]*0.35
        z[t] = -0.05 + 0.18*y[t-1] + 0.58*z[t-1] + shocks[t,1]*0.30
    pred, actual = rolling_ar1(y, train=160)
    var_beta = var1_fit(np.column_stack([y, z]))
    ewma = ewma_variance(np.diff(y))
    filtered = local_level_filter(y)
    result = {
        "n": n, "train": 160,
        "ar1_rolling_rmse": float(np.sqrt(np.mean((pred-actual)**2))),
        "var1_coefficients": var_beta.tolist(),
        "ewma_lambda": 0.94,
        "ewma_last_variance": float(ewma[-1]),
        "local_level_last": float(filtered[-1]),
        "split_rule": "all observations before t train the forecast at t; no random shuffle",
    }
    out = Path(__file__).resolve().parents[1] / 'data' / 'm04_time_series_results.json'
    out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2)); return 0

if __name__ == '__main__': raise SystemExit(main())
