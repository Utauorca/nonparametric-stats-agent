"""無母數檢定計算腳本。

用 scipy 實際計算常見無母數檢定的統計量、p 值與效果量，
避免模型心算或憑空給數字。資料從 CSV 讀入 (long 格式: 一欄值、一欄組別)。

範例:
    # 兩獨立樣本 Mann-Whitney U
    python run_test.py mannwhitney --csv data.csv --value score --group grp

    # 配對 Wilcoxon signed-rank (寬格式: 兩欄為前後測)
    python run_test.py wilcoxon --csv data.csv --col-a pre --col-b post

    # 多組 Kruskal-Wallis
    python run_test.py kruskal --csv data.csv --value score --group grp
"""
import argparse
import sys

import numpy as np
import pandas as pd
from scipy import stats


def _groups(df, value, group):
    """把 long 格式拆成各組的數值陣列 list。"""
    return [g[value].to_numpy() for _, g in df.groupby(group)]


def mannwhitney(df, args):
    a, b = _groups(df, args.value, args.group)
    res = stats.mannwhitneyu(a, b, alternative="two-sided")
    n1, n2 = len(a), len(b)
    rank_biserial = 1 - (2 * res.statistic) / (n1 * n2)
    return {
        "test": "Mann-Whitney U",
        "U": float(res.statistic),
        "p_value": float(res.pvalue),
        "rank_biserial_r": float(rank_biserial),
        "n": [n1, n2],
        "note": "要解讀成中位數差，需兩組分布形狀相近；否則僅為隨機優勢。",
    }


def wilcoxon(df, args):
    a = df[args.col_a].to_numpy()
    b = df[args.col_b].to_numpy()
    res = stats.wilcoxon(a, b)
    diff = a - b
    return {
        "test": "Wilcoxon signed-rank",
        "W": float(res.statistic),
        "p_value": float(res.pvalue),
        "median_diff": float(np.median(diff)),
        "n": int(len(diff)),
        "note": "假設配對差值分布對稱。",
    }


def kruskal(df, args):
    groups = _groups(df, args.value, args.group)
    res = stats.kruskal(*groups)
    n = sum(len(g) for g in groups)
    k = len(groups)
    epsilon_sq = (res.statistic - k + 1) / (n - k)
    return {
        "test": "Kruskal-Wallis",
        "H": float(res.statistic),
        "p_value": float(res.pvalue),
        "epsilon_squared": float(epsilon_sq),
        "k_groups": k,
        "note": "顯著後做 Dunn's test 事後比較並校正多重檢定。",
    }


DISPATCH = {"mannwhitney": mannwhitney, "wilcoxon": wilcoxon, "kruskal": kruskal}


def main():
    p = argparse.ArgumentParser(description="無母數檢定計算")
    p.add_argument("test", choices=DISPATCH.keys())
    p.add_argument("--csv", required=True)
    p.add_argument("--value", help="數值欄名 (long 格式)")
    p.add_argument("--group", help="組別欄名 (long 格式)")
    p.add_argument("--col-a", help="配對第一欄 (wilcoxon)")
    p.add_argument("--col-b", help="配對第二欄 (wilcoxon)")
    args = p.parse_args()

    df = pd.read_csv(args.csv)
    result = DISPATCH[args.test](df, args)

    print(f"\n=== {result['test']} ===")
    for key, val in result.items():
        if key == "test":
            continue
        print(f"{key:>18}: {val}")
    print()


if __name__ == "__main__":
    sys.exit(main())
