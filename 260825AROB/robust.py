

from __future__ import annotations
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import spearmanr, kendalltau

try:
    matplotlib.use("MacOSX")
except Exception:
    try:
        matplotlib.use("TkAgg")
    except Exception:
        pass
plt.ion()  


BASE = Path("./output")
FILES = {
    "BIS": {
        "0.3": BASE / "multilayer_results_BIS_0.3.xlsx",
        "0.5": BASE / "multilayer_results_BIS.xlsx",
        "0.8": BASE / "multilayer_results_BIS_0.8.xlsx",
    },
    "UN": {
        "0.3": BASE / "multilayer_results_UN_0.3.xlsx",
        "0.5": BASE / "multilayer_results_UN.xlsx",
        "0.8": BASE / "multilayer_results_UN_0.8.xlsx",
    },
}
OUTDIR = BASE / "sensitivity"
OUTDIR.mkdir(parents=True, exist_ok=True)

PAIRS = [("0.3","0.5"), ("0.8","0.5"), ("0.3","0.8")]
TOPK_LIST = [3, 5, 10]
RISK_FLAG_THRESHOLD = 0.5 

def _assert_files_exist():
    missing = []
    for layer, d in FILES.items():
        for th, p in d.items():
            if not p.exists():
                missing.append((layer, th, str(p)))
    if missing:
        msg = ["[ERROR] 다음 파일이 없음:"]
        for layer, th, p in missing:
            msg.append(f"- {layer} {th}: {p}")
        raise FileNotFoundError("\n".join(msg))

def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def load_final_vectors_by_period(path: Path) -> dict[str, pd.Series]:
    xl = pd.ExcelFile(path)
    out = {}
    for sheet in xl.sheet_names:
        df = _clean_df(xl.parse(sheet))
        final = df.tail(1).T.squeeze()
        final.name = sheet
        out[sheet] = final
    return out 

def align_periods(d_a: dict, d_b: dict) -> list[str]:
    return sorted(set(d_a.keys()) & set(d_b.keys()))

def align_countries(s_a: pd.Series, s_b: pd.Series) -> tuple[pd.Series, pd.Series]:
    common = sorted(set(s_a.index) & set(s_b.index))
    return s_a.loc[common], s_b.loc[common]

def topk_overlap(a: pd.Series, b: pd.Series, k: int) -> float:
    top_a = set(a.sort_values(ascending=False).head(k).index)
    top_b = set(b.sort_values(ascending=False).head(k).index)
    inter = len(top_a & top_b)
    union = len(top_a | top_b)
    return inter / union if union > 0 else np.nan

def mean_abs_rank_shift(a: pd.Series, b: pd.Series) -> float:
    r1 = a.rank(ascending=False, method="average")
    r2 = b.rank(ascending=False, method="average")
    r1, r2 = align_countries(r1, r2)
    return float((r1 - r2).abs().mean())

def flagged_count(a: pd.Series, thr: float = RISK_FLAG_THRESHOLD) -> int:
    return int((a >= thr).sum())

def pair_metrics(a: pd.Series, b: pd.Series) -> dict:
    a, b = align_countries(a, b)
    rho, _ = spearmanr(a, b, nan_policy="omit")
    tau, _ = kendalltau(a, b)
    mars = mean_abs_rank_shift(a, b)
    delta_mean = float(b.mean() - a.mean())
    delta_std = float(b.std(ddof=1) - a.std(ddof=1))
    cascade_a = flagged_count(a)
    cascade_b = flagged_count(b)
    res = {
        "spearman_rho": rho,
        "kendall_tau": tau,
        "mean_abs_rank_shift": mars,
        "delta_mean": delta_mean,
        "delta_std": delta_std,
        "flagged_count_a": cascade_a,
        "flagged_count_b": cascade_b,
        "flagged_count_delta": cascade_b - cascade_a,
    }
    for k in TOPK_LIST:
        res[f"top{k}_overlap"] = topk_overlap(a, b, k)
    return res

def collect_metrics(layer: str):
    S03 = load_final_vectors_by_period(FILES[layer]["0.3"])
    S05 = load_final_vectors_by_period(FILES[layer]["0.5"])
    S08 = load_final_vectors_by_period(FILES[layer]["0.8"])
    periods = sorted(set(S03.keys()) & set(S05.keys()) & set(S08.keys()))

    rows = []
    for per in periods:
        finals = {"0.3": S03[per], "0.5": S05[per], "0.8": S08[per]}
        for (a, b) in PAIRS:
            m = pair_metrics(finals[a], finals[b])
            m.update({"layer": layer, "period": per, "pair": f"{a}_vs_{b}"})
            rows.append(m)
    per_period_df = pd.DataFrame(rows).sort_values(["period", "pair"])

    summary = (
        per_period_df
        .groupby(["layer", "pair"], as_index=False)
        .agg({c: "mean" for c in per_period_df.columns if c not in ["layer", "period", "pair"]})
    )
    return periods, S03, S05, S08, per_period_df, summary

def save_tables(layer: str, per_period_df: pd.DataFrame, summary: pd.DataFrame):
    per_period_df.to_csv(OUTDIR / f"per_period_metrics_{layer}.csv", index=False)
    summary.to_csv(OUTDIR / f"summary_metrics_{layer}.csv", index=False)

def _save_and_show(fig: plt.Figure, out_path: Path, dpi: int = 200):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.show()  
    plt.pause(0.001)  
    plt.close(fig)

def plot_scatter_latest(layer: str, periods: list[str], S03, S05, S08):
    latest = periods[-1]
    a03, a05 = align_countries(S03[latest], S05[latest])
    a08, _   = align_countries(S08[latest], S05[latest])

    def _scatter(x, y, title, fname):
        fig = plt.figure(figsize=(6.6, 6.6))
        ax = fig.add_subplot(111)
        ax.scatter(x, y, s=40, alpha=0.85, edgecolor="k")
        xymin = float(min(x.min(), y.min()))
        xymax = float(max(x.max(), y.max()))
        ax.plot([xymin, xymax], [xymin, xymax], ls="--", lw=1, c="gray")
        for c in x.index:
            ax.text(x[c], y[c], c, fontsize=8, ha="center", va="bottom")
        ax.set_xlabel("Risk (first in pair)")
        ax.set_ylabel("Risk (second in pair)")
        ax.set_title(title)
        ax.grid(alpha=0.3)
        _save_and_show(fig, OUTDIR / fname)

    _scatter(a03, a05, f"{layer} latest {latest}: 0.3 vs 0.5", f"scatter_latest_{layer}_03_05.png")
    _scatter(a08, a05, f"{layer} latest {latest}: 0.8 vs 0.5", f"scatter_latest_{layer}_08_05.png")
    _scatter(a03, a08, f"{layer} latest {latest}: 0.3 vs 0.8", f"scatter_latest_{layer}_03_08.png")

def plot_rank_shift_heatmap(layer: str, periods: list[str], S03, S08):
    all_countries = sorted(set().union(*[S03[p].index for p in periods]) &
                           set().union(*[S08[p].index for p in periods]))
    accum = {c: [] for c in all_countries}
    for per in periods:
        a, b = align_countries(S03[per], S08[per])
        r1 = a.rank(ascending=False, method="average")
        r2 = b.rank(ascending=False, method="average")
        for c in r1.index:
            accum[c].append(abs(r1[c] - r2[c]))
    avg_shift = pd.Series({c: np.nanmean(accum[c]) for c in accum}).sort_values(ascending=False)

    fig = plt.figure(figsize=(10.5, 6.0))
    ax = fig.add_subplot(111)
    avg_shift.plot(kind="bar", ax=ax)
    ax.set_ylabel("Avg |Δ Rank| (0.3 vs 0.8)")
    ax.set_title(f"{layer}: Average absolute rank shift across periods")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    _save_and_show(fig, OUTDIR / f"rank_shift_heatmap_{layer}.png")

def plot_topk_overlap(layer: str, per_period_df: pd.DataFrame):
    df = (
        per_period_df[per_period_df["layer"] == layer]
        .groupby("pair", as_index=False)[[f"top{k}_overlap" for k in TOPK_LIST]].mean()
    )
    x = np.arange(len(TOPK_LIST))
    width = 0.25

    fig = plt.figure(figsize=(8.4, 5.0))
    ax = fig.add_subplot(111)
    for i, pair in enumerate(["0.3_vs_0.5", "0.8_vs_0.5", "0.3_vs_0.8"]):
        vals = df[df["pair"] == pair][[f"top{k}_overlap" for k in TOPK_LIST]].values.flatten()
        ax.bar(x + i * width, vals, width=width, label=pair)
    ax.set_xticks(x + width)
    ax.set_xticklabels([f"Top-{k}" for k in TOPK_LIST])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Jaccard overlap")
    ax.set_title(f"{layer}: mean Top-k overlap across periods")
    ax.legend()
    fig.tight_layout()
    _save_and_show(fig, OUTDIR / f"topk_overlap_{layer}.png")

def export_pdf():
    pdf_path = OUTDIR / "sensitivity_report.pdf"
    with PdfPages(pdf_path) as pdf:
        for img in sorted(OUTDIR.glob("*.png")):
            fig = plt.figure()
            plt.imshow(plt.imread(img))
            plt.axis("off")
            plt.title(img.name)
            pdf.savefig(fig)
            plt.close(fig)
    print(f"\n[OK] PDF exported: {pdf_path}")
    try:
        if os.name == "nt":
            os.system(f'start "" "{pdf_path}"')
        elif os.name == "posix":
            # 맥/리눅스
            if "darwin" in os.sys.platform.lower():
                os.system(f'open "{pdf_path}"')
            else:
                os.system(f'xdg-open "{pdf_path}"')
    except Exception:
        pass

def main():
    _assert_files_exist()

    for layer in ["BIS", "UN"]:
        periods, S03, S05, S08, per_period_df, summary = collect_metrics(layer)

        save_tables(layer, per_period_df, summary)
        print(f"\n===== {layer} / per-period metrics (head) =====")
        print(per_period_df.head(10).to_string(index=False))
        print(f"\n===== {layer} / summary metrics =====")
        print(summary.to_string(index=False))
        plot_scatter_latest(layer, periods, S03, S05, S08)
        plot_rank_shift_heatmap(layer, periods, S03, S08)
        plot_topk_overlap(layer, per_period_df)

    export_pdf()
    print(f"\n[OK] Saved sensitivity tables and figures into {OUTDIR}\n")

if __name__ == "__main__":
    main()



import pandas as pd
from pathlib import Path

base = Path("./output/sensitivity")
bis = pd.read_csv(base / "summary_metrics_BIS.csv")
un  = pd.read_csv(base / "summary_metrics_UN.csv")

cols = [
    "layer","pair","spearman_rho","kendall_tau",
    "mean_abs_rank_shift","top3_overlap","top5_overlap","top10_overlap",
    "flagged_count_delta"
]

df = pd.concat([bis[cols], un[cols]], axis=0).reset_index(drop=True)

df = df.round({
    "spearman_rho": 4,
    "kendall_tau": 4,
    "mean_abs_rank_shift": 3,
    "top3_overlap": 3,
    "top5_overlap": 3,
    "top10_overlap": 3
})

df.to_excel("summary_table_for_paper.xlsx", index=False)
print("\n[OK] summary_table_for_paper.xlsx 생성 완료.\n")
print(df)