#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Horizontal (x) vs Vertical (y) propagation by country
- BIS/UN 멀티레이어 시뮬레이터의 핵심만 추려서,
  모든 분기에 대해 국가별 수평/수직 기여도를 누적 집계 후
  산점도(국가 라벨 포함)로 저장/표시.
- 필요한 외부 함수: load_dataset_bis, load_dataset_un, initialise_risk_vector
"""

from __future__ import annotations
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text


from BIS_UN_debtrank_0513copyBISonly import (
    load_dataset_bis, load_dataset_un, initialise_risk_vector
)

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["axes.unicode_minus"] = False


def propagate_multilayer(
    W_bis: np.ndarray,
    W_un: np.ndarray,
    h0_bis: np.ndarray,
    h0_un: np.ndarray,
    vertical_alpha: float = 0.05,
    vertical_threshold: float = 0.5,
    max_iter: int = 30,
    eps: float = 1e-3,
):

    h_prev_bis = np.zeros_like(h0_bis)
    h_prev_un  = np.zeros_like(h0_un)
    h_bis = h0_bis.copy();  h_un = h0_un.copy()
    H_bis = h0_bis.copy();  H_un = h0_un.copy()

    history_bis, history_un = [], []

    horiz_bis = np.zeros_like(h0_bis)
    horiz_un  = np.zeros_like(h0_un)
    vert_to_bis = np.zeros_like(h0_bis)
    vert_to_un  = np.zeros_like(h0_un)

    for _ in range(max_iter):
        delta_bis = np.maximum(0, h_bis - h_prev_bis)
        new_h_bis = (W_bis @ delta_bis).clip(0, 1)
        H_bis = np.minimum(H_bis + new_h_bis, 1.0)

        mask_bis = H_bis >= vertical_threshold
        new_h_un_from_bis = np.minimum(vertical_alpha * H_bis * mask_bis.astype(float), 1 - H_un)
        horiz_bis += new_h_bis
        vert_to_un += new_h_un_from_bis
        history_bis.append(H_bis.copy())

        delta_un = np.maximum(0, h_un - h_prev_un)
        pure_un_horiz = (W_un @ delta_un).clip(0, 1)
        new_h_un = np.minimum(pure_un_horiz + new_h_un_from_bis, 1.0)
        H_un = np.minimum(H_un + new_h_un, 1.0)

        mask_un = H_un >= vertical_threshold
        new_h_bis_from_un = np.minimum(vertical_alpha * H_un * mask_un.astype(float), 1 - H_bis)

        new_h_bis = np.minimum(new_h_bis + new_h_bis_from_un, 1.0)
        H_bis = np.minimum(H_bis + new_h_bis_from_un, 1.0)

        horiz_un  += pure_un_horiz
        vert_to_bis += new_h_bis_from_un
        history_un.append(H_un.copy())

        if np.all(new_h_bis < eps) and np.all(new_h_un < eps):
            break

        h_prev_bis, h_bis = h_bis, new_h_bis
        h_prev_un,  h_un  = h_un,  new_h_un

    contrib = {
        "horiz_bis": horiz_bis, "horiz_un": horiz_un,
        "vert_to_bis": vert_to_bis, "vert_to_un": vert_to_un
    }
    return history_bis, history_un, contrib


def main(
    base_dir: Path,
    default_file: Path,
    out_dir: Path,
    vertical_alpha: float,
    vertical_threshold: float,
    max_iter: int,
):
    out_dir.mkdir(parents=True, exist_ok=True)

    WM_bis, countries_bis, name_map_bis, _, periods_bis = load_dataset_bis(base_dir)
    WM_un,  countries_un,  name_map_un,  _, periods_un  = load_dataset_un(base_dir)
    iso2_to_name = name_map_bis
    name_to_iso3 = {v: k for k, v in name_map_un.items()}
    countries = [iso for iso, name in iso2_to_name.items() if name in name_to_iso3]

    periods_bis_ts = pd.PeriodIndex(periods_bis, freq="Q").to_timestamp()
    common_periods = sorted(set(periods_bis_ts) & set(periods_un))

    bis_str_to_mat = WM_bis
    WM_bis_ts = {}
    for ts in common_periods:
        WM_bis_ts[ts] = bis_str_to_mat[f"{ts.year}-Q{ts.quarter}"]

    WM_un_aligned = {}
    for p in common_periods:
        orig = WM_un[p]
        N = len(countries)
        mat = np.zeros((N, N))
        for i, iso2_i in enumerate(countries):
            iso3_i = name_to_iso3[iso2_to_name[iso2_i]]
            idx_i3 = countries_un.index(iso3_i)
            for j, iso2_j in enumerate(countries):
                iso3_j = name_to_iso3[iso2_to_name[iso2_j]]
                idx_j3 = countries_un.index(iso3_j)
                mat[j, i] = orig[idx_j3, idx_i3]
        WM_un_aligned[p] = mat

    default_df = pd.read_excel(default_file)
    default_df["Year_Quarter"] = pd.PeriodIndex(default_df["Year_Quarter"], freq="Q").to_timestamp()

    N = len(countries)
    sum_horiz = np.zeros(N)
    sum_vert  = np.zeros(N)

    for per in common_periods:
        h0_bis = initialise_risk_vector(countries_bis, name_map_bis, default_df, per)
        h0_un  = initialise_risk_vector(countries_un,  name_map_un,  default_df, per)

        _, _, contrib = propagate_multilayer(
            WM_bis_ts[per], WM_un_aligned[per], h0_bis, h0_un,
            vertical_alpha=vertical_alpha,
            vertical_threshold=vertical_threshold,
            max_iter=max_iter
        )

        sum_horiz += (contrib["horiz_bis"] + contrib["horiz_un"])
        sum_vert  += (contrib["vert_to_bis"] + contrib["vert_to_un"])

    out_csv = out_dir / "horizontal_vs_vertical_by_country.csv"
    pd.DataFrame({
        "ISO2": countries,
        "Horizontal_total": sum_horiz,
        "Vertical_total": sum_vert
    }).to_csv(out_csv, index=False)
    print(f"💾 saved: {out_csv}")

    fig, ax = plt.subplots(figsize=(10, 7))  
    
    x, y = sum_horiz, sum_vert
    sc = ax.scatter(x, y, s=150, alpha=0.75, edgecolor="black", c="tab:blue")
    
    texts = []
    for i, iso in enumerate(countries):
        texts.append(ax.annotate(iso, (x[i], y[i]), ha='center', va='bottom', fontsize=14))
    
    adjust_text(texts,
                force_points=(10, 10),  
                force_text=(10, 10),    
                expand_points=(1.5, 1.5), 
                arrowprops=dict(arrowstyle="-", color='gray', lw=0.5))

    ax.set_xlabel("Horizontal propagation", fontsize=20)
    ax.set_ylabel("Vertical contagion", fontsize=20)
    ax.set_title("Horizontal vs Vertical Contagion by Country", fontsize=27)
    ax.tick_params(axis="both", which="major", labelsize=14)

    ax.grid(alpha=0.3)
    ax.set_ylim(0, 12)

    import matplotlib.ticker as ticker
    ax.yaxis.set_major_locator(ticker.MultipleLocator(2.5))
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

    plt.tight_layout()

    out_png = out_dir / "scatter_horizontal_vs_vertical_by_country.png"
    plt.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.show()
    print(f"📈 saved: {out_png}")


def parse_args():
    p = argparse.ArgumentParser(description="Horizontal vs Vertical scatter (country-level)")
    p.add_argument("--base-dir", default="./", type=Path)
    p.add_argument("--default-file", default="./default/Default_Probabilities_5Years_Bond.xlsx", type=Path)
    p.add_argument("--out-dir", default="./output_scatter", type=Path)
    p.add_argument("--vertical-alpha", type=float, default=0.05)
    p.add_argument("--vertical-threshold", type=float, default=0.5)
    p.add_argument("--max-iter", type=int, default=20)
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(
        base_dir=args.base_dir,
        default_file=args.default_file,
        out_dir=args.out_dir,
        vertical_alpha=args.vertical_alpha,
        vertical_threshold=args.vertical_threshold,
        max_iter=args.max_iter,
    )



