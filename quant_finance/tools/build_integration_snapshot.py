"""Build an aligned SPY/GLD strategy-integration snapshot.

All constituent rules use the same monthly adjusted-close panel, a lagged
12-month information window, zero cash return, and 10 bps target turnover
cost.  This is intentionally a small mechanism study, not an investable
multi-asset production backtest.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, stdev

import requests


END_MONTH = "2026-06"
START_MONTH = "2006-01"
LOOKBACK = 12
COST = 0.001
ASSETS = ["SPY", "GLD"]


def fetch_monthly(symbol: str) -> dict[str, float]:
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        f"{symbol}?period1=1072915200&period2=1785118518"
        "&interval=1mo&events=div%2Csplits&includeAdjustedClose=true"
    )
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    result = response.json()["chart"]["result"][0]
    stamps = result.get("timestamp", [])
    values = result["indicators"]["adjclose"][0]["adjclose"]
    return {
        datetime.fromtimestamp(stamp, tz=timezone.utc).strftime("%Y-%m"): float(value)
        for stamp, value in zip(stamps, values)
        if value is not None and datetime.fromtimestamp(stamp, tz=timezone.utc).strftime("%Y-%m") <= END_MONTH
    }


def metric(values: list[float], turnovers: list[float]) -> dict:
    wealth = 1.0
    peak = 1.0
    mdd = 0.0
    for value in values:
        wealth *= 1.0 + value
        peak = max(peak, wealth)
        mdd = min(mdd, wealth / peak - 1.0)
    sd = stdev(values)
    return {
        "months": len(values),
        "annualized_arithmetic_return": 12.0 * mean(values),
        "cagr": wealth ** (12.0 / len(values)) - 1.0,
        "annualized_volatility": math.sqrt(12.0) * sd,
        "sharpe_rf0": math.sqrt(12.0) * mean(values) / sd,
        "max_drawdown": mdd,
        "final_wealth_multiple": wealth,
        "annual_turnover": 12.0 * mean(turnovers),
        "total_cost": COST * sum(turnovers),
    }


def main() -> None:
    prices = {asset: fetch_monthly(asset) for asset in ASSETS}
    months = sorted(set(prices[ASSETS[0]]) & set(prices[ASSETS[1]]))
    months = [month for month in months if START_MONTH <= month <= END_MONTH]
    if len(months) < 150:
        raise RuntimeError(f"too few aligned months: {len(months)}")
    returns = {
        asset: [prices[asset][months[i]] / prices[asset][months[i - 1]] - 1.0 for i in range(1, len(months))]
        for asset in ASSETS
    }

    names = ["buy_hold_50_50", "trend_sma12", "inverse_vol_risk_parity", "vol_target_10pct"]
    series = {name: [] for name in names}
    turns = {name: [] for name in names}
    previous = {name: [0.0, 0.0] for name in names}

    for i in range(LOOKBACK + 1, len(months) - 1):
        # At index i, returns[i] are month i -> i+1. Signals use prices through month i.
        prior_returns = [returns[asset][i - LOOKBACK : i] for asset in ASSETS]
        vol = [max(stdev(values) * math.sqrt(12.0), 1e-8) for values in prior_returns]
        base = [0.5, 0.5]
        trend = [0.5 if prices[asset][months[i]] > mean([prices[asset][months[j]] for j in range(i - LOOKBACK + 1, i + 1)]) else 0.0 for asset in ASSETS]
        inv = [1.0 / value for value in vol]
        inv_sum = sum(inv)
        inv = [value / inv_sum for value in inv]
        cov = sum(a * b for a, b in zip(prior_returns[0], prior_returns[1])) / (LOOKBACK - 1)
        _ = cov  # retained as a reminder that inverse-vol is not exact ERC
        base_vol = math.sqrt(sum((weight * value) ** 2 for weight, value in zip(base, vol)))
        scale = min(1.5, 0.10 / max(base_vol, 1e-8))
        vt = [scale * value for value in base]
        targets = {
            "buy_hold_50_50": base,
            "trend_sma12": trend,
            "inverse_vol_risk_parity": inv,
            "vol_target_10pct": vt,
        }
        next_returns = [returns[asset][i] for asset in ASSETS]
        for name, target in targets.items():
            turnover = sum(abs(a - b) for a, b in zip(target, previous[name]))
            gross = sum(weight * value for weight, value in zip(target, next_returns))
            series[name].append(gross - COST * turnover)
            turns[name].append(turnover)
            previous[name] = target

    # Strategy overlay weights are fixed and applied after each constituent
    # has paid its own rebalance cost; no additional overlay turnover is added.
    series["equal_strategy_ensemble"] = [mean(values) for values in zip(*(series[name] for name in names))]
    turns["equal_strategy_ensemble"] = [0.0] * len(series["equal_strategy_ensemble"])
    series["defensive_trend_vol_ensemble"] = [0.5 * a + 0.5 * b for a, b in zip(series["trend_sma12"], series["vol_target_10pct"])]
    turns["defensive_trend_vol_ensemble"] = [0.0] * len(series["defensive_trend_vol_ensemble"])

    stats = {name: metric(values, turns[name]) for name, values in series.items()}
    matrix = {}
    for left in stats:
        matrix[left] = {}
        for right in stats:
            x, y = series[left], series[right]
            mx, my = mean(x), mean(y)
            sx, sy = stdev(x), stdev(y)
            matrix[left][right] = sum((a - mx) * (b - my) for a, b in zip(x, y)) / ((len(x) - 1) * sx * sy)

    output = {
        "snapshot_date_utc": "2026-07-27",
        "source": "Yahoo Finance chart API adjusted close",
        "source_type": "secondary_data_proxy/local-evidence",
        "symbols": ASSETS,
        "sample": {"start": months[LOOKBACK + 1], "end": months[-1], "frequency": "monthly", "months": len(series["buy_hold_50_50"])},
        "protocol": {
            "lookback_months": LOOKBACK,
            "signal_timing": "all signals use data through month t and apply to t+1 return",
            "transaction_cost": "10 bps times one-way absolute target-weight turnover for each constituent",
            "cash_return": 0.0,
            "ensemble_overlay": "equal-weight constituent net returns; no additional overlay turnover",
            "constituents": names,
        },
        "strategy_stats_net_10bps": stats,
        "return_correlation": matrix,
        "evidence_boundary": [
            "SPY and GLD are ETF proxies; no taxes, FX conversion, financing, bid-ask spread or market impact are modeled.",
            "The integration uses a common two-asset monthly panel, but the sample is descriptive and not an untouched out-of-sample selection test.",
            "Ensemble returns average constituent net returns; a production implementation must model overlay turnover and capital allocation explicitly.",
            "Inverse-volatility is only an approximation to exact equal risk contribution when correlation differs from zero.",
        ],
    }
    path = Path(__file__).resolve().parents[1] / "data" / "classic_strategy_integration_snapshot.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote={path}")
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
