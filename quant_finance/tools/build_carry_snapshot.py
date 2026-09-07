"""Build a transparent carry/term-structure proxy snapshot.

The Yahoo continuous futures series do not expose an auditable contract-roll
calendar.  We therefore call the signal a futures-minus-ETF basis/roll proxy,
not a pure roll yield.  The script intentionally keeps the protocol simple
and records the evidence boundary in the resulting JSON.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, stdev

import requests


END_MONTH = "2026-06"
START_MONTH = "2007-01"
ANNUAL = 12
COST = 0.001  # 10 bps per one-way absolute target-weight turnover

ASSETS = {
    "gold": {"futures": "GC=F", "etf": "GLD", "label": "黄金"},
    "oil": {"futures": "CL=F", "etf": "USO", "label": "原油"},
    "bond": {"futures": "ZB=F", "etf": "TLT", "label": "长期美债"},
    "euro": {"futures": "6E=F", "etf": "UUP", "label": "美元 ETF（反向欧元代理）"},
}


def fetch_monthly(symbol: str) -> dict[str, float]:
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        f"{symbol}?period1=1072915200&period2=1785118518"
        "&interval=1mo&events=div%2Csplits&includeAdjustedClose=true"
    )
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    result = response.json()["chart"]["result"][0]
    timestamps = result.get("timestamp", [])
    quote = result["indicators"]["quote"][0]
    raw = quote.get("close", [])
    adjusted = result.get("indicators", {}).get("adjclose", [{}])[0].get("adjclose", raw)
    values = adjusted if symbol not in {"GC=F", "CL=F", "ZB=F", "6E=F"} else raw
    output = {}
    for stamp, value in zip(timestamps, values):
        if value is None:
            continue
        month = datetime.fromtimestamp(stamp, tz=timezone.utc).strftime("%Y-%m")
        if month <= END_MONTH:
            output[month] = float(value)
    return output


def returns(prices: dict[str, float], months: list[str]) -> list[float]:
    return [prices[months[i]] / prices[months[i - 1]] - 1.0 for i in range(1, len(months))]


def metric_block(values: list[float], turnovers: list[float] | None = None) -> dict:
    n = len(values)
    wealth = 1.0
    peak = 1.0
    mdd = 0.0
    for value in values:
        wealth *= 1.0 + value
        peak = max(peak, wealth)
        mdd = min(mdd, wealth / peak - 1.0)
    sd = stdev(values) if n > 1 else 0.0
    result = {
        "months": n,
        "annualized_arithmetic_return": ANNUAL * mean(values),
        "cagr": wealth ** (ANNUAL / n) - 1.0 if n else None,
        "annualized_volatility": math.sqrt(ANNUAL) * sd,
        "sharpe_rf0": math.sqrt(ANNUAL) * mean(values) / sd if sd else None,
        "max_drawdown": mdd,
        "final_wealth_multiple": wealth,
    }
    if turnovers is not None:
        result["annual_turnover"] = ANNUAL * mean(turnovers)
        result["total_cost"] = COST * sum(turnovers)
    return result


def main() -> None:
    prices: dict[str, dict[str, float]] = {}
    for asset, spec in ASSETS.items():
        prices[f"{asset}_futures"] = fetch_monthly(spec["futures"])
        prices[f"{asset}_etf"] = fetch_monthly(spec["etf"])

    available = [set(series) for series in prices.values()]
    months = sorted(set.intersection(*available))
    months = [month for month in months if START_MONTH <= month <= END_MONTH]
    if len(months) < 120:
        raise RuntimeError(f"too few common months: {len(months)}")

    fut_returns = {}
    etf_returns = {}
    carry_spreads = {}
    for asset in ASSETS:
        fut_returns[asset] = returns(prices[f"{asset}_futures"], months)
        etf_returns[asset] = returns(prices[f"{asset}_etf"], months)
        carry_spreads[asset] = [
            fut - etf for fut, etf in zip(fut_returns[asset], etf_returns[asset])
        ]

    spread_stats = {}
    for asset, values in carry_spreads.items():
        sd = stdev(values)
        spread_stats[asset] = {
            "label": ASSETS[asset]["label"],
            "mean_monthly_basis_roll_proxy": mean(values),
            "annualized_basis_roll_proxy": ANNUAL * mean(values),
            "annualized_volatility": math.sqrt(ANNUAL) * sd,
            "t_stat_iid_descriptive": mean(values) / (sd / math.sqrt(len(values))),
            "positive_month_fraction": sum(value > 0 for value in values) / len(values),
        }

    # Signals at month t use the previous three complete monthly spread values;
    # target weights are applied to ETF return in month t+1.
    strategy_values = {"equal_weight_4_etf": [], "top2_relative_carry": [], "top2_positive_carry": []}
    strategy_turnover = {name: [] for name in strategy_values}
    previous = {name: [0.0] * len(ASSETS) for name in strategy_values}
    asset_names = list(ASSETS)
    for i in range(3, len(months) - 1):
        signal = {asset: mean(carry_spreads[asset][i - 3 : i]) for asset in asset_names}
        ranked = sorted(asset_names, key=lambda asset: signal[asset], reverse=True)
        positive = [asset for asset in ranked if signal[asset] > 0]
        targets = {
            "equal_weight_4_etf": [0.25] * len(asset_names),
            "top2_relative_carry": [0.5 if asset in ranked[:2] else 0.0 for asset in asset_names],
            "top2_positive_carry": [1.0 / len(positive) if asset in positive[:2] else 0.0 for asset in asset_names] if positive else [0.0] * len(asset_names),
        }
        next_returns = [etf_returns[asset][i] for asset in asset_names]
        for name, target in targets.items():
            turnover = sum(abs(a - b) for a, b in zip(target, previous[name]))
            gross = sum(weight * value for weight, value in zip(target, next_returns))
            strategy_values[name].append(gross - COST * turnover)
            strategy_turnover[name].append(turnover)
            previous[name] = target

    strategy_stats = {
        name: metric_block(values, strategy_turnover[name])
        for name, values in strategy_values.items()
    }

    output = {
        "snapshot_date_utc": "2026-07-27",
        "source": "Yahoo Finance chart API",
        "source_type": "secondary_data_proxy",
        "symbols": ASSETS,
        "data_window": {"start": months[0], "end": months[-1], "frequency": "monthly", "common_months": len(months)},
        "protocol": {
            "basis_roll_proxy": "continuous-front-futures monthly close return minus ETF adjusted-close return",
            "lookback_months": 3,
            "signal_timing": "signal at t uses t-3:t-1; target applies to ETF return at t+1",
            "ranking": "top two assets by relative three-month proxy; positive-only variant goes to cash if no positive score",
            "transaction_cost": "10 bps times one-way absolute target-weight turnover",
            "cash_return": 0.0,
            "annualization_factor": 12,
        },
        "basis_roll_proxy_stats": spread_stats,
        "strategy_stats_net_10bps": strategy_stats,
        "evidence_boundary": [
            "Continuous Yahoo futures symbols do not provide a verified contract-level roll calendar, collateral yield, margin, or financing rate.",
            "The futures-minus-ETF differential is a basis/roll proxy that also contains spot-tracking, ETF fee, collateral and data-construction differences; it is not pure carry.",
            "ETF returns are used for the strategy leg, so the ranking experiment is a carry-proxy allocation test, not a futures total-return backtest.",
            "The four-asset sample is descriptive, uses a secondary provider, zero cash return and 10 bps linear costs; it does not establish expected future returns.",
        ],
    }
    path = Path(__file__).resolve().parents[1] / "data" / "classic_strategy_carry_snapshot.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote={path}")
    print(json.dumps(strategy_stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
