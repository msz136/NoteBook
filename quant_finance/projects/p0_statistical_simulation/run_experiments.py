#!/usr/bin/env python3
"""Run the frozen P0 Monte Carlo protocol and write deterministic artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy import stats


ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def draw_standardized(name: str, rng: np.random.Generator, shape: tuple[int, ...]) -> np.ndarray:
    """Draw mean-zero, variance-one samples for the frozen distribution family."""
    if name == "normal":
        return rng.normal(size=shape)
    if name == "student_t_df3":
        # A t(3) variable has variance 3; divide by sqrt(3) to standardize variance.
        return rng.standard_t(df=3, size=shape) / math.sqrt(3.0)
    if name == "centered_lognormal":
        # For lognormal(0, 1), mean=exp(1/2), variance=(exp(1)-1)exp(1).
        raw = rng.lognormal(mean=0.0, sigma=1.0, size=shape)
        mean = math.exp(0.5)
        std = math.sqrt((math.e - 1.0) * math.e)
        return (raw - mean) / std
    raise ValueError(f"unsupported distribution: {name}")


def mc_se(probability: float, repetitions: int) -> float:
    return math.sqrt(probability * (1.0 - probability) / repetitions)


def run_lln_clt(config: dict[str, Any], rng: np.random.Generator) -> dict[str, Any]:
    repetitions = int(config["replications"])
    output: dict[str, Any] = {}
    for distribution in config["distributions"]:
        rows = []
        for n in config["sample_sizes"]:
            samples = draw_standardized(distribution, rng, (repetitions, int(n)))
            means = samples.mean(axis=1)
            z = math.sqrt(n) * means
            coverage = float(np.mean(np.abs(z) <= stats.norm.ppf(0.975)))
            ks = stats.kstest(z, "norm")
            rows.append(
                {
                    "n": int(n),
                    "mean_bias": float(means.mean()),
                    "mean_rmse": float(np.sqrt(np.mean(means**2))),
                    "z_mean": float(z.mean()),
                    "z_std": float(z.std(ddof=1)),
                    "normal_95_coverage": coverage,
                    "coverage_mc_se": mc_se(coverage, repetitions),
                    "ks_distance_to_normal": float(ks.statistic),
                }
            )
        output[distribution] = rows
    return output


def run_variance_bias(config: dict[str, Any], rng: np.random.Generator) -> list[dict[str, Any]]:
    repetitions = int(config["replications"])
    rows = []
    for n in config["variance_sample_sizes"]:
        samples = rng.normal(size=(repetitions, int(n)))
        mle = samples.var(axis=1, ddof=0)
        unbiased = samples.var(axis=1, ddof=1)
        rows.append(
            {
                "n": int(n),
                "ddof0_mean": float(mle.mean()),
                "ddof0_bias": float(mle.mean() - 1.0),
                "ddof1_mean": float(unbiased.mean()),
                "ddof1_bias": float(unbiased.mean() - 1.0),
            }
        )
    return rows


def run_ci_coverage(config: dict[str, Any], rng: np.random.Generator) -> list[dict[str, Any]]:
    repetitions = int(config["replications"])
    alpha = 1.0 - float(config["confidence_level"])
    zcrit = stats.norm.ppf(1.0 - alpha / 2.0)
    rows = []
    for n in config["ci_sample_sizes"]:
        samples = rng.normal(size=(repetitions, int(n)))
        means = samples.mean(axis=1)
        se = samples.std(axis=1, ddof=1) / math.sqrt(n)
        tcrit = stats.t.ppf(1.0 - alpha / 2.0, df=n - 1)
        z_cover = float(np.mean(np.abs(means) <= zcrit * se))
        t_cover = float(np.mean(np.abs(means) <= tcrit * se))
        rows.append(
            {
                "n": int(n),
                "z_interval_coverage": z_cover,
                "z_interval_mc_se": mc_se(z_cover, repetitions),
                "t_interval_coverage": t_cover,
                "t_interval_mc_se": mc_se(t_cover, repetitions),
            }
        )
    return rows


def run_bootstrap_median(config: dict[str, Any], rng: np.random.Generator) -> list[dict[str, Any]]:
    protocol = config["bootstrap"]
    outer = int(protocol["outer_replications"])
    resamples = int(protocol["resamples"])
    alpha = 1.0 - float(config["confidence_level"])
    true_median = math.log(2.0)
    zcrit = stats.norm.ppf(1.0 - alpha / 2.0)
    rows = []
    for n in protocol["sample_sizes"]:
        percentile_hits = 0
        asymptotic_hits = 0
        widths = []
        for _ in range(outer):
            sample = rng.exponential(scale=1.0, size=int(n))
            indices = rng.integers(0, int(n), size=(resamples, int(n)))
            bootstrap_medians = np.median(sample[indices], axis=1)
            lower, upper = np.quantile(bootstrap_medians, [alpha / 2.0, 1.0 - alpha / 2.0])
            percentile_hits += int(lower <= true_median <= upper)
            widths.append(float(upper - lower))

            # For Exp(1), asymptotic median SE is 1 / sqrt(n) because f(log 2)=1/2.
            median = float(np.median(sample))
            asymptotic_hits += int(abs(median - true_median) <= zcrit / math.sqrt(n))
        percentile = percentile_hits / outer
        asymptotic = asymptotic_hits / outer
        rows.append(
            {
                "n": int(n),
                "true_median": true_median,
                "percentile_coverage": percentile,
                "percentile_coverage_mc_se": mc_se(percentile, outer),
                "percentile_mean_width": float(np.mean(widths)),
                "asymptotic_coverage": asymptotic,
                "asymptotic_coverage_mc_se": mc_se(asymptotic, outer),
            }
        )
    return rows


def write_plot(summary: dict[str, Any], output: Path) -> None:
    plt.rcParams.update({"svg.hashsalt": "p0-v1", "font.size": 9})
    colors = {"normal": "#1a4a8c", "student_t_df3": "#b8390e", "centered_lognormal": "#6b5b8e"}
    fig, axes = plt.subplots(2, 2, figsize=(10, 7.2), constrained_layout=True)

    ax = axes[0, 0]
    for name, rows in summary["lln_clt"].items():
        ax.plot([r["n"] for r in rows], [r["mean_rmse"] for r in rows], marker="o", label=name, color=colors[name])
    ax.set(xscale="log", yscale="log", title="A. LLN: sample-mean RMSE", xlabel="sample size n", ylabel="RMSE")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7)

    ax = axes[0, 1]
    for name, rows in summary["lln_clt"].items():
        ax.plot([r["n"] for r in rows], [r["normal_95_coverage"] for r in rows], marker="o", label=name, color=colors[name])
    ax.axhline(0.95, color="#444", linestyle="--", linewidth=1)
    ax.set(xscale="log", ylim=(0.75, 1.0), title="B. CLT normal-interval coverage", xlabel="sample size n", ylabel="coverage")
    ax.grid(alpha=0.25)

    ax = axes[1, 0]
    rows = summary["variance_bias"]
    ax.plot([r["n"] for r in rows], [r["ddof0_bias"] for r in rows], marker="o", label="ddof=0", color="#b8390e")
    ax.plot([r["n"] for r in rows], [r["ddof1_bias"] for r in rows], marker="o", label="ddof=1", color="#1a4a8c")
    ax.axhline(0.0, color="#444", linestyle="--", linewidth=1)
    ax.set(title="C. Normal variance-estimator bias", xlabel="sample size n", ylabel="Monte Carlo bias")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)

    ax = axes[1, 1]
    rows = summary["bootstrap_median"]
    n = [r["n"] for r in rows]
    p = [r["percentile_coverage"] for r in rows]
    e = [1.96 * r["percentile_coverage_mc_se"] for r in rows]
    ax.errorbar(n, p, yerr=e, marker="o", capsize=3, label="percentile bootstrap", color="#1a4a8c")
    ax.plot(n, [r["asymptotic_coverage"] for r in rows], marker="s", label="asymptotic median", color="#b8390e")
    ax.axhline(0.95, color="#444", linestyle="--", linewidth=1)
    ax.set(ylim=(0.75, 1.0), title="D. Exp(1) median CI coverage", xlabel="sample size n", ylabel="coverage")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)

    fig.suptitle("P0 statistical simulation — frozen protocol p0-v1", fontsize=12, fontweight="bold")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, format="svg", metadata={"Date": None, "Creator": "quant_finance P0"})
    plt.close(fig)


def run(config_path: Path, output_dir: Path) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    rng = np.random.default_rng(int(config["seed"]))
    summary: dict[str, Any] = {
        "protocol": config,
        "provenance": {
            "script_sha256": sha256(Path(__file__)),
            "config_sha256": sha256(config_path),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "matplotlib": matplotlib.__version__,
            "rng": "numpy.random.default_rng / PCG64 default",
        },
    }
    summary["lln_clt"] = run_lln_clt(config, rng)
    summary["variance_bias"] = run_variance_bias(config, rng)
    summary["ci_coverage_normal"] = run_ci_coverage(config, rng)
    summary["bootstrap_median"] = run_bootstrap_median(config, rng)

    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "summary.json"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    write_plot(summary, output_dir / "summary.svg")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "config.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    summary = run(args.config.resolve(), args.output_dir.resolve())
    print(f"protocol={summary['protocol']['protocol_version']}")
    print(f"summary={args.output_dir.resolve() / 'summary.json'}")
    print(f"plot={args.output_dir.resolve() / 'summary.svg'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
