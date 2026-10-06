# 無母數檢定速查

每個方法列出：虛無假設、檢定統計量、ties 處理、效果量、scipy 函式。

## 符號檢定 (Sign test)
- H0：中位數 = 指定值（或配對差中位數 = 0）。
- 統計量：正差個數，服從 Binomial(n, 0.5)。
- Ties（差值=0）：通常剔除後再算。
- 效果量：可報成功比例與其信賴區間。
- scipy：`scipy.stats.binomtest`。

## Wilcoxon 符號等級檢定 (signed-rank)
- H0：配對差值分布對稱中心為 0。**假設差值分布對稱**。
- 統計量：W = 正等級和（或 min(W+, W-)）。
- Ties：等級取平均；差值=0 多半剔除。
- 效果量：matched-pairs rank-biserial；位置估計用 Hodges-Lehmann（配對差中位數）。
- scipy：`scipy.stats.wilcoxon`。

## Mann-Whitney U / Wilcoxon rank-sum
- H0：兩組來自同分布（P(X>Y)=0.5）。**要解讀成中位數差需兩組形狀相近**。
- 統計量：U。
- Ties：等級取平均，建議用常態近似校正。
- 效果量：rank-biserial r = 1 - 2U/(n1·n2)；位置差用 Hodges-Lehmann。
- scipy：`scipy.stats.mannwhitneyu`。

## Kruskal-Wallis
- H0：k 組來自同分布。
- 統計量：H，近似 χ²(k-1)。
- Ties：有 ties 校正因子。
- 事後：Dunn's test + Bonferroni / Holm 校正（`scikit-posthocs`）。
- 效果量：epsilon² 或 eta²_H。
- scipy：`scipy.stats.kruskal`。

## Friedman
- H0：k 個相依條件分布相同。
- 統計量：χ²_r，近似 χ²(k-1)。
- 事後：Nemenyi（`scikit-posthocs`）。
- 效果量：Kendall's W（一致性係數）。
- scipy：`scipy.stats.friedmanchisquare`。

## 相關
- Spearman ρ：等級的 Pearson 相關；`scipy.stats.spearmanr`。
- Kendall τ：一致/不一致對的比例；小樣本或 ties 多時較穩健；`scipy.stats.kendalltau`。

## 分布 / 適合度
- Kolmogorov-Smirnov：`scipy.stats.ks_1samp` / `ks_2samp`。
- Anderson-Darling：尾端較敏感；`scipy.stats.anderson` / `anderson_ksamp`。

## 隨機性
- Runs test（連檢定）：檢定序列是否隨機；`statsmodels.sandbox.stats.runs.runstest_1samp`。

## 重抽樣
- Permutation test：`scipy.stats.permutation_test`，少假設、適合小樣本。
- Bootstrap 信賴區間：`scipy.stats.bootstrap`。
