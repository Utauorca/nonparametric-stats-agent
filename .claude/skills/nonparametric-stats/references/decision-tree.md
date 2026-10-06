# 無母數方法選擇決策樹

```mermaid
flowchart TD
    Start([研究問題是什麼?]) --> Goal{目的}

    Goal -->|比較組間位置/中位數| G1{資料尺度?}
    Goal -->|比較組間散布/變異| S1[Ansari-Bradley 檢定<br/>需兩組中位數相等]
    Goal -->|比較兩分布是否有任何差異| D1[Kolmogorov-Smirnov 雙樣本]
    Goal -->|衡量關聯/相關| C1{資料尺度?}
    Goal -->|檢定適合度/單樣本分布| D2[KS 單樣本<br/>Anderson-Darling]
    Goal -->|檢定隨機性| R1[Runs test 連檢定]

    G1 -->|名目 nominal| GN[卡方 / Fisher 精確檢定]
    G1 -->|次序或連續但非常態| G2{幾組?}

    G2 -->|1 組 或 配對| P1{差值分布對稱?}
    P1 -->|是, 假設成立| P1a[Wilcoxon 符號等級檢定 signed-rank]
    P1 -->|否 / 只關心中位數| P1b[符號檢定 sign test]

    G2 -->|2 組 獨立| T2{分布形狀相近?}
    T2 -->|是| T2a[Mann-Whitney U, 可解讀為中位數差]
    T2 -->|否| T2b[Mann-Whitney U 僅解讀為隨機優勢<br/>或用 permutation test]

    G2 -->|>2 組 獨立| K1[Kruskal-Wallis]
    K1 -->|顯著| K2[事後: Dunn's test + 多重比較校正]

    G2 -->|>2 組 相依/重複測量| F1[Friedman 檢定]
    F1 -->|顯著| F2[事後: Nemenyi test]

    C1 -->|次序 或 單調非線性| C2[Spearman ρ / Kendall τ]

    P1a --> Eff[報告效果量+信賴區間]
    P1b --> Eff
    T2a --> Eff
    T2b --> Eff
    K2 --> Eff
    F2 --> Eff
    C2 --> Eff
```

## 節點判斷規則

| 判斷點 | 問法 | 分支 |
|---|---|---|
| 目的 | 想回答什麼問題? | 比較 / 相關 / 適合度 / 隨機性 |
| 資料尺度 | 反應變數是什麼尺度? | 名目→卡方類；次序或連續非常態→無母數等級法 |
| 樣本結構 | 幾組?組間獨立還是同一批受試者? | 1/配對、2 獨立、>2 獨立、>2 相依 |
| 形狀假設 | 兩組分布形狀是否相近? | 相近→可談中位數差；不相近→只能談隨機優勢 |
| 對稱假設 | 配對差值分布是否對稱? | 對稱→signed-rank；不確定→sign test |

## 方法對照（母數 ↔ 無母數）

| 情境 | 母數方法 | 無母數對應 |
|---|---|---|
| 單樣本/配對 | paired t-test | Wilcoxon signed-rank / sign test |
| 兩獨立樣本(位置) | independent t-test | Mann-Whitney U |
| 兩獨立樣本(散布) | F-test / Levene | Ansari-Bradley |
| 多組獨立 | one-way ANOVA | Kruskal-Wallis |
| 多組相依 | repeated-measures ANOVA | Friedman |
| 相關 | Pearson r | Spearman ρ / Kendall τ |

> 每個方法的完整假設、統計量、ties 處理、判斷規則與 R code 見 `textbook-methods.md`。
