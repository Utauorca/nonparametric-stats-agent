# 無母數方法詳解（教材版）

> 本檔內容萃取自本專案的 `slides.qmd`，底本為
> Hollander, Wolfe & Chicken (2015), *Nonparametric Statistical Methods* (3rd ed.)。
> 回答時可引用此處的假設、統計量、ties 處理與判斷規則作為依據。

---

## 1. 單樣本 / 配對位置問題 — Wilcoxon 符號等級檢定 (signed-rank)

**資料與假設.** 對 $n$ 個受試者取配對 $(X_i, Y_i)$，化為差值 $Z_i = Y_i - X_i$。
- A1：$Z_1,\ldots,Z_n$ 互相獨立。
- A2：每個 $Z_i$ 來自連續母體，且**對共同中位數 $\theta$ 對稱**：$F_i(\theta+t)+F_i(\theta-t)=1$。
  （$\theta$ = treatment effect；純單樣本時 $Z_i$ 即原始觀測值，檢定中位數是否等於 $\theta_0$。）

**假設檢定.** $H_0:\theta=0$；對立：$H_1:\theta>0$、$H_2:\theta<0$、$H_3:\theta\neq 0$。

**統計量.** 對 $|Z_i|$ 由小到大排名得 $R_i$，令 $\psi_i=1$ 若 $Z_i>0$ 否則 $0$：
$$T^{+}=\sum_{i=1}^{n}\psi_i R_i \quad(\text{正差的等級和,兼含符號與大小}).$$

**Ties.** 差值為 0 → 剔除並縮減 $n$；$|Z|$ 相同 → 取平均等級（檢定變近似）。
有 ties 時 $E_0(T^+)$ 不變，變異數縮小：
$$\operatorname{Var}_0(T^{+})=\tfrac{1}{24}\big[n(n+1)(2n+1)-\tfrac12\sum_j t_j(t_j-1)(t_j+1)\big].$$

**判斷（精確）.** $t_\alpha$ 為上 $\alpha$ 臨界值（R：`qsignrank`/`psignrank`）。
| 對立 | 拒絕 $H_0$ 若 |
|---|---|
| $H_1:\theta>0$ | $T^{+}\ge t_\alpha$ |
| $H_2:\theta<0$ | $T^{+}\le \tfrac{n(n+1)}{2}-t_\alpha$ |
| $H_3:\theta\neq0$ | $T^{+}\ge t_{\alpha/2}$ 或 $\le \tfrac{n(n+1)}{2}-t_{\alpha/2}$ |

**大樣本近似.** $E_0(T^+)=\tfrac{n(n+1)}{4}$，$\operatorname{Var}_0(T^+)=\tfrac{n(n+1)(2n+1)}{24}$，
$T^{*}=\dfrac{T^{+}-E_0}{\sqrt{\operatorname{Var}_0}}\xrightarrow{d}N(0,1)$。

**R.** `wilcox.test(post, pre, paired = TRUE, alternative = "less")`
（等價：`wilcox.test(post - pre, alternative = "less")`）。

---

## 2. 兩樣本位置問題 — Wilcoxon 等級和 / Mann–Whitney U

**資料與假設.** $X_1,\ldots,X_m$、$Y_1,\ldots,Y_n$，各自 i.i.d.、兩組互相獨立、連續母體。
位置移動模型 $G(t)=F(t-\Delta)$：兩分布**形狀相同、只差平移 $\Delta$**。

**假設檢定.** $H_0:\Delta=0$（即 $F=G$）；對立 $H_1:\Delta>0$、$H_2:\Delta<0$、$H_3:\Delta\neq0$。

**統計量.** 合併排名；$S_j$ = $Y_j$ 的聯合排名。
$$W=\sum_{j=1}^{n}S_j \quad(\text{第二組 }Y\text{ 的等級和}).$$
等價形式：Mann–Whitney 計數 $U=\sum_i\sum_j \mathbb{1}(X_i<Y_j)$，與 $W=U+\tfrac{n(n+1)}{2}$。

**Ties.** 取平均等級，檢定變近似；$E_0(W)$ 不變，變異數縮小：
$$\operatorname{Var}_0(W)=\tfrac{mn}{12}\big[m+n+1-\tfrac{\sum_j(t_j-1)t_j(t_j+1)}{(m+n)(m+n-1)}\big].$$

**判斷（精確）.** $w_\alpha$ 上 $\alpha$ 臨界值（R：`qwilcox`）。
| 對立 | 拒絕 $H_0$ 若 |
|---|---|
| $H_1:\Delta>0$ | $W\ge w_\alpha$ |
| $H_2:\Delta<0$ | $W\le n(m+n+1)-w_\alpha$ |
| $H_3:\Delta\neq0$ | $W\ge w_{\alpha/2}$ 或 $\le n(m+n+1)-w_{\alpha/2}$ |

**大樣本近似.** $E_0(W)=\tfrac{n(m+n+1)}{2}$，$\operatorname{Var}_0(W)=\tfrac{mn(m+n+1)}{12}$，標準化後 $\to N(0,1)$。

**R.** `wilcox.test(treatment, control)`（雙尾，小樣本自動用精確分布）。

**重要解讀界線.** 要把結果講成「中位數差異」需兩組**形狀相近**；否則只能解讀為隨機優勢 $P(X<Y)$。

---

## 3. 兩樣本散布問題 — Ansari–Bradley 檢定（scale）

**資料與假設.** 同兩樣本 i.i.d. + 互相獨立 + 連續；**額外要求 A3：兩母體中位數相等** $\theta_1=\theta_2$
（讓檢定只反映散布差異）。位置-尺度模型 $F(t)=H(\tfrac{t-\theta_1}{\eta_1})$、$G(t)=H(\tfrac{t-\theta_2}{\eta_2})$。

**假設檢定.** 尺度比 $\gamma=\eta_1/\eta_2$（若變異數存在，$\gamma^2=\operatorname{var}(X)/\operatorname{var}(Y)$）。
$H_0:\gamma^2=1$；對立 $H_1:\gamma^2>1$、$H_2:\gamma^2<1$、$H_3:\gamma^2\neq1$。

**統計量.** 合併排序後**由兩端往中間給分**：最小與最大給 1、次小與次大給 2…
令 $R_j$ 為 $Y_j$ 的分數，$C=\sum_{j=1}^n R_j$。
（概念：較集中的樣本落在中央＝高分，較分散的落在兩端＝低分。）

**Ties.** 取平均分數，檢定變近似（變異數公式隨 $N$ 奇偶不同，見 slides）。

**判斷（精確）.** $c_\alpha$ 上 $\alpha$ 臨界值。大樣本近似的 $E_0(C)$、$\operatorname{Var}_0(C)$ **依 $N$ 奇偶而異**：
- $N$ 偶：$E_0(C)=\tfrac{n(N+2)}{4}$，$\operatorname{Var}_0(C)=\tfrac{mn(N+2)(N-2)}{48(N-1)}$。
- $N$ 奇：$E_0(C)=\tfrac{n(N+1)^2}{4N}$，$\operatorname{Var}_0(C)=\tfrac{mn(N+1)(3+N^2)}{48N^2}$。

**R.** `ansari.test(y, x)`（`alternative` 可指定單尾）。

---

## 4. 兩分布一般差異 — Kolmogorov–Smirnov 雙樣本檢定 (Smirnov)

**假設.** 兩獨立樣本、連續母體，分布函數 $F$、$G$。

**假設檢定.** $H_0:F(t)=G(t)\ \forall t$ vs $H_1:F(t)\neq G(t)$ 至少一個 $t$（偵測**任何**差異，天生雙尾）。

**統計量.** 經驗分布 $F_m,G_n$，取最大垂直落差：
$$J=\tfrac{mn}{d}\max_t|F_m(t)-G_n(t)|,\quad d=\gcd(m,n).$$
最大值只需在 $N=m+n$ 個資料點檢查。

**判斷.** $J\ge j_\alpha$ 時拒絕。大樣本：以 $D=\max_t|F_m-G_n|$，$\sqrt{mn/N}\,D$ 比對 Kolmogorov 臨界值。

**R.** `ks.test(x, y)`。

---

## 5. 單因子配置（$k$ 組獨立）— Kruskal–Wallis

**假設.** $N=\sum n_j$ 個觀測分 $k$ 組；互相獨立；各組 i.i.d. 連續；位置模型 $F_j(t)=F(t-\tau_j)$。
（即 rank 版 one-way ANOVA：$X_{ij}=\theta+\tau_j+e_{ij}$。）

**假設檢定.** $H_0:\tau_1=\cdots=\tau_k$ vs $H_1$ 至少兩者不等。

**統計量.** **合併全部 $N$ 個觀測排名**，$R_j$ = 第 $j$ 組等級和，$\bar R_{\cdot j}=R_j/n_j$：
$$H=\tfrac{12}{N(N+1)}\sum_j n_j\big(\bar R_{\cdot j}-\tfrac{N+1}{2}\big)^2=\tfrac{12}{N(N+1)}\sum_j \tfrac{R_j^2}{n_j}-3(N+1).$$
$H$ 大則拒絕（$k=2$ 時退化成雙尾 Wilcoxon rank-sum）。

**Ties.** 取平均等級後除以收縮因子校正：
$$H'=\dfrac{H}{1-\dfrac{\sum_j(t_j^3-t_j)}{N^3-N}}.$$

**判斷.** 精確：$H\ge h_\alpha$（R：`cKW`）。大樣本：$H\xrightarrow{d}\chi^2_{k-1}$，$H\ge\chi^2_{k-1,\alpha}$ 拒絕。

**事後（顯著後）.** Dunn's test + 多重比較校正（Bonferroni/Holm）。

**R.** `kruskal.test(value ~ group)`。

---

## 6. 雙因子配置（$k$ 組相依 / RCBD）— Friedman 檢定

**假設.** 隨機完全區集設計：$n$ 個 block、每 block 有 $k$ 個 treatment 各一觀測。
互相獨立、連續；加法模型 $F_{ij}(u)=F(u-\beta_i-\tau_j)$（$\beta_i$ = block 效果，$\tau_j$ = treatment 效果）。
（即 rank 版 two-way / repeated-measures ANOVA。）

**假設檢定.** $H_0:\tau_1=\cdots=\tau_k$ vs $H_1$ 至少兩者不等。

**統計量.** **在每個 block 內各自排名** $1\ldots k$（這樣消掉 block 效果 $\beta_i$），$R_j$ = treatment $j$ 的等級和：
$$S=\tfrac{12n}{k(k+1)}\sum_j\big(\bar R_{\cdot j}-\tfrac{k+1}{2}\big)^2=\tfrac{12}{nk(k+1)}\sum_j R_j^2-3n(k+1).$$
$S$ 大則拒絕（$k=2$ 時退化成符號檢定）。

> **與 Kruskal–Wallis 的關鍵差異**：KW 把全部觀測**聯合排名**；Friedman **在每個 block 內排名**。

**Ties.** block 內取平均等級，並用 tie-corrected $S$（分母扣 $\tfrac{1}{k-1}\sum_i\sum_j(t_{ij}^3-t_{ij})$）。

**判斷.** 精確：$S\ge s_\alpha$。大樣本：$S\xrightarrow{d}\chi^2_{k-1}$。

**事後（顯著後）.** Nemenyi test。

**R.** `friedman.test(times)`（`times` 為 block×treatment 矩陣）。

---

> 以下第 7–20 節萃取自本人報告 `nonparametric-midterm-report_1.qmd`（基本概念、類別資料檢定、單樣本檢定）。
> 寫法以 R 套件的實際算法為準；回答與計算時，函式與參數設定應與此處一致。

## 7. 基本概念 — 有母數 vs 無母數

| | 有母數方法 | 無母數方法 |
|:---|:---|:---|
| 分配假設 | 資料假設特定分配 | 不假設特定分配，或僅要求連續、對稱等較弱條件 |
| 推論對象 | 分配的參數，如 $\mu$、$\sigma^2$ | 分位數、比例，或整個分配的形狀 |
| 使用的資訊 | 觀測值的實際數值 | 符號、排序或各類別數量 |
| 對離群值 | 敏感 | 較穩健 |
| 小樣本 | 須依賴分配假設成立 | 部分檢定可計算 exact p-value |
| 假設成立時的檢定力 | 較高 | 較低 |

---

## 8. 配對二元資料 — McNemar Test

**目的.** 同一批受試者在兩個時間點（或兩種條件）下，二元屬性的比例是否改變；即**改變方向是否對稱**。

**資料與假設.**
- $n'$ 組配對 $(X_i, Y_i)$，來自同一受試者或配對單位。
- $X_i, Y_i \in \{S, F\}$（nominal、僅兩類）。
- 各配對互相獨立；$P(X_i=S,Y_i=F)-P(X_i=F,Y_i=S)$ 對所有 $i$ 同號（同正、同負或同為零）。

整理成 $2\times2$ 表（$X$ 為 row、$Y$ 為 column）：$a=(S,S)$、$b=(S,F)$、$c=(F,S)$、$d=(F,F)$。
**只用 $b$ 與 $c$**；$a$、$d$ 不提供改變方向的資訊。

**假設檢定.** 雙尾 $H_0: P(X_i=S,Y_i=F)=P(X_i=F,Y_i=S)$ vs $H_a: \ne$；
單尾分別為 $<$（由 $S$ 轉 $F$ 的機率較小）、$>$（較大）。

**統計量.** $T=b$，$n=b+c$；$H_0$ 下 $T\sim\text{Bin}(n,\tfrac12)$。

**判斷（精確）.** 左尾 $P(T\le b)$；右尾 $P(T\ge b)$；雙尾 $2\min\{P(T\le b),P(T\ge b)\}$。

**大樣本近似.** $Z=\dfrac{b-c}{\sqrt{b+c}}\approx N(0,1)$。`mcnemar.test()` 用平方形式並**預設 continuity correction**：
$\chi^2=\dfrac{(|b-c|-1)^2}{b+c}\approx\chi^2_1$；`correct = FALSE` 得 $(b-c)^2/(b+c)=Z^2$。校正使 p-value 略保守。

**R.**
- 精確：`binom.test(b, b + c, p = 0.5)`
- 近似：`mcnemar.test(tab)`（只提供雙尾）；`mcnemar.test(tab, correct = FALSE)`
- 單尾：改用 `binom.test(b, b + c, p = 0.5, alternative = "less" / "greater")`

拒絕 $H_0$ 後，依 $b$ 與 $c$ 的大小判斷改變方向。

---

## 9. $k$ 個相關樣本的二元反應 — Cochran's Q Test

**目的.** 同一批受試者在 $k$ 種 treatment 下，產生二元反應的機率是否相同。為 McNemar test 的推廣：$k=2$ 時兩者檢驗同一件事；$k\ge3$ 時無法直接用 McNemar。

**資料與假設.**
- Complete block design：每位受試者接受全部 $k$ 種 treatment，每個組合恰一個觀測值；受試者即 block。
- 反應為二元（coded 0/1），所有受試者的二類標準相同。
- $n$ 位受試者為隨機樣本、互相獨立。

資料為 $n\times k$ 的 0/1 矩陣（row = 受試者、column = treatment），$R_i$ = row 總和、$C_j$ = column 總和、$N=\sum R_i=\sum C_j$。
$R_i=0$ 或 $R_i=k$ 的受試者對統計量沒有貢獻（同 McNemar 的 $a$、$d$）。

**假設檢定.** $H_0: p_1=\cdots=p_k$（對每位受試者皆成立）vs $H_a$：某兩種 treatment $p_\ell\ne p_m$。

**統計量.**
$$T=k(k-1)\frac{\sum_{j}\left(C_j-\tfrac{N}{k}\right)^2}{\sum_{i}R_i(k-R_i)}=\frac{k(k-1)\sum_j C_j^2-(k-1)N^2}{kN-\sum_i R_i^2}.$$
兩式代數等價。分子衡量 column 總和偏離 $N/k$ 的程度，分母為各受試者內部變異總和。

**判斷.** 精確分配在 $n$ 稍大時不可行，實務用大樣本近似：$T\approx\chi^2_{k-1}$，p-value $=P(\chi^2_{k-1}\ge T_{\text{obs}})$。

**R.** 手刻上式後以 `pchisq(Q, df = k - 1, lower.tail = FALSE)` 計算；
套件驗算 `DescTools::CochranQTest(y ~ treatment | id, data = d_long)`（long format，`處理 | 受試者`）。

---

## 10. 兩類別變數是否獨立 — Chi-squared Test for Independence

**目的.** 單一隨機樣本、每個觀測值依兩個準則分類，檢驗兩類別變數是否互相獨立。

**資料與假設.**
- **單一隨機樣本**：總數 $n$ 在抽樣前決定；各 row、column 總和皆為抽樣後的隨機量。
- 兩變數皆為類別變數（$r$ 類、$c$ 類），類別互斥且窮盡。
- 各觀測值互相獨立。
- 各格期望次數 $E_{ij}>5$；不滿足可合併部分 row 或 column。

ordinal 類別也可用，但不利用順序資訊。數值變數先切區間再建表時，邊際總和是事先選定的（等筆數切分），並非隨機量。

**假設檢定.** $H_0: P(\text{row } i\text{ and column } j)=P(\text{row } i)P(\text{column } j)$ for all $i,j$ vs $H_a$：for some $i,j$ 不等。**僅有雙尾形式**。

**統計量.** $E_{ij}=\dfrac{R_iC_j}{n}$，
$$T=\sum_i\sum_j\frac{(O_{ij}-E_{ij})^2}{E_{ij}}=\sum_i\sum_j\frac{O_{ij}^2}{E_{ij}}-n.$$
計算後檢查各 $E_{ij}$ 是否夠大。

**判斷.** 精確分配與 multinomial 有關、計算困難，採大樣本近似 $T\approx\chi^2_{(r-1)(c-1)}$，p-value $=P(\chi^2_{(r-1)(c-1)}\ge T_{\text{obs}})$；或 $T>\chi^2_{1-\alpha,(r-1)(c-1)}$ 拒絕。

**R.** `Xsq <- chisq.test(M)`；期望次數 `Xsq$expected`，檢查 `min(Xsq$expected)`。

---

## 11. $r$ 個母體分布是否相同 — Chi-squared Test for Homogeneity

**目的.** 自 $r$ 個母體各抽一組樣本、分類到 $c$ 類，檢驗各母體落入同一類別的機率是否一致。

**與 Independence 的差別在抽樣設計**（統計量、期望次數公式、自由度完全相同；同一張表數值結果相同，但結論不同）：

| | Independence | Homogeneity |
|:---|:---|:---|
| 母體數 | 1 個 | $r$ 個 |
| 事先固定的量 | 總樣本數 $n$ | 各母體樣本數 $n_1,\ldots,n_r$ |
| 隨機的量 | 所有 row 與 column 總和 | 僅 column 總和 $C_j$ |
| $H_0$ | 兩變數互相獨立 | $r$ 個母體的分布相同 |

**資料與假設.**
- 各母體分別抽樣，$n_i$ 為抽樣前決定的常數。
- 分類變數為類別變數（$c$ 類），每個觀測值恰落入一類。
- 樣本之間、樣本內各觀測值皆互相獨立。
- 各格 $E_{ij}>5$；不滿足可合併類別。

**假設檢定.** $H_0: p_{1j}=\cdots=p_{rj}$ 對所有 $j$ vs $H_a$：某個 $j$ 與某一組 $i,k$ 使 $p_{ij}\ne p_{kj}$。

**統計量.** $E_{ij}=\dfrac{n_iC_j}{n}$（$C_j/n$ 為共同機率的估計），$T=\sum_i\sum_j\dfrac{(O_{ij}-E_{ij})^2}{E_{ij}}$。
$r=c=2$ 時可化簡為 $T=\dfrac{n(O_{11}O_{22}-O_{12}O_{21})^2}{C_1C_2\,n_1n_2}$。

**判斷.** $T\approx\chi^2_{(r-1)(c-1)}$，p-value $=P(\chi^2_{(r-1)(c-1)}\ge T_{\text{obs}})$。

**R.**
- 任意 $r\times c$：`chisq.test(M)`
- $c=2$：`prop.test(successes, n_i)`（另列各母體樣本比例）
- $r>2$ 時兩者統計量相同；$r=2$ 時 `prop.test()` 預設 continuity correction，`chisq.test()` 對 $2\times2$ 表亦然。

---

## 12. 單一比例 — Binomial Test

**目的.** 檢定事件發生機率 $p$ 是否等於（或大於、小於）$p_0$。

**資料與假設.** 每筆資料只有成功／失敗兩種結果；互相獨立；成功機率皆為 $p$；樣本數 $n$ 固定。

**假設檢定.** 左尾 $H_0:p\ge p_0$ vs $p<p_0$；右尾 $H_0:p\le p_0$ vs $p>p_0$；雙尾 $H_0:p=p_0$ vs $p\ne p_0$。

**統計量.** $S$ = 成功次數；$H_0$ 下（取 $p=p_0$）$Y\sim\text{Bin}(n,p_0)$，$s_{\text{obs}}$ 為觀察值。

**判斷（p-value，依 `binom.test()` 算法）.**

| 類型 | p-value |
|---|---|
| 左尾 | $P(Y\le s_{\text{obs}})$ |
| 右尾 | $P(Y\ge s_{\text{obs}})$ |
| 雙尾 | $\sum_{k:\,P(Y=k)\le P(Y=s_{\text{obs}})}P(Y=k)$（**不是**兩倍較小尾機率） |

**臨界值做法.** 左尾找 $r$ 使 $P(Y\le r)\approx\alpha$，$s_{\text{obs}}\le r$ 拒絕；右尾找 $r$ 使 $P(Y\ge r)\approx\alpha$，$s_{\text{obs}}\ge r$ 拒絕；
雙尾取 $r_1$、$r_2$ 使兩側各 $\approx\alpha/2$。$S$ 離散，取「不超過 $\alpha$（或 $\alpha/2$）的最大尾機率」，實際顯著水準比 $\alpha$ 小。

**大樣本近似.** $np_0>5$ 且 $n(1-p_0)>5$ 時，$s_{\text{critical}}=np_0+z\sqrt{np_0(1-p_0)}$：
左尾 $z=z_\alpha$、右尾 $z=z_{1-\alpha}$、雙尾分別用 $z_{\alpha/2}$ 與 $z_{1-\alpha/2}$ 算上下界。

**R.** `binom.test(s_obs, n, p = p0, alternative = ...)`；
手算雙尾：`d <- dbinom(0:n, n, p0); sum(d[d <= dbinom(s_obs, n, p0)])`；
臨界值：`max(k[pbinom(k, n, p0) <= 0.025])`、`min(k[1 - pbinom(k - 1, n, p0) <= 0.025])`。

---

## 13. 母體分位數 — Quantile Test

**目的.** 檢定母體 $p$ 分位數 $Q_p$ 是否等於（或大於、小於）$x_0$。$p=0.5$ 時即 sign test。

**資料與假設.** $X_1,\ldots,X_n$ 為同一母體的隨機樣本、互相獨立；尺度為 ordinal / interval / ratio（只需能和 $x_0$ 比大小）。

**假設檢定.**

| 類型 | $H_0$ | $H_a$ |
|---|---|---|
| 左尾 | $Q_p\ge x_0$，即 $P(X<x_0)\le p$ | $Q_p<x_0$，即 $P(X<x_0)>p$ |
| 右尾 | $Q_p\le x_0$，即 $P(X\le x_0)\ge p$ | $Q_p>x_0$，即 $P(X\le x_0)<p$ |
| 雙尾 | $Q_p=x_0$，即 $P(X\le x_0)\ge p$ 且 $P(X<x_0)\le p$ | $Q_p\ne x_0$ |

**統計量.** $T_1$ = $\le x_0$ 的個數；$T_2$ = $<x_0$ 的個數（無觀測值等於 $x_0$ 時 $T_1=T_2$）。
邊界 $Q_p=x_0$ 下兩者皆 $\sim\text{Bin}(n,p)$ ⇒ 本質上是對計數做 binomial test。
左尾用 $T_2$（偏大拒絕）；右尾用 $T_1$（偏小拒絕）；雙尾同時用 $T_1$ 偏小或 $T_2$ 偏大。

**判斷.**

| 類型 | p-value | R |
|---|---|---|
| 左尾 | $P(T_2\ge t_2)$ | `binom.test(t2, n, p, alternative = "greater")` |
| 右尾 | $P(T_1\le t_1)$ | `binom.test(t1, n, p, alternative = "less")` |
| 雙尾 | $\min\{1,\,2\min\{P(T_1\le t_1),P(T_2\ge t_2)\}\}$ | `pbinom(t1, n, p)` 與 `1 - pbinom(t2 - 1, n, p)` |

> `alternative` 是針對「計數代表的比例」設定方向：左尾 $Q_p<x_0$ ⇔ $P(X<x_0)>p$，所以用 `"greater"`；右尾用 `"less"`。

**臨界值.** 左尾：最小 $r$ 使 $P(T_2>r)\le\alpha$，$t_2>r$ 拒絕；右尾：最大 $r$ 使 $P(T_1\le r)\le\alpha$，$t_1\le r$ 拒絕；
雙尾：最大 $r_1$ 使 $P(T_1\le r_1)\le\alpha/2$、最小 $r_2$ 使 $P(T_2>r_2)\le\alpha/2$，$t_1\le r_1$ 或 $t_2>r_2$ 拒絕。

**R.** 沒有專門函數；先算 `t2 <- sum(x < x0)`、`t1 <- sum(x <= x0)`，再依上表。

---

## 14. 配對資料何者較大 — Sign Test

**目的.** 檢定配對資料中哪個變數傾向較大（配對差中位數是否為 0）；把一方換成固定值 $x_0$ 即可檢定單一母體中位數。
Sign test = $p=0.5$ 的 binomial test = $p=0.5$ 的 quantile test。

**資料與假設.** 配對 $(X_i,Y_i)$，$i=1,\ldots,n'$，各配對互相獨立；尺度為 ordinal / interval / ratio。

**假設檢定.** $P(+)=P(X_i<Y_i)$、$P(-)=P(X_i>Y_i)$。
左尾 $H_0:P(+)\ge P(-)$；右尾 $H_0:P(+)\le P(-)$；雙尾 $H_0:P(+)=P(-)$。

**統計量.** $X_i<Y_i$ 記「+」、$X_i>Y_i$ 記「−」、$X_i=Y_i$ 為 tie。
**Ties 排除**：$n=n'-(\text{tie 數})$。$T$ = 「+」的個數；$H_0$ 邊界下 $T\sim\text{Bin}(n,\tfrac12)$。

**判斷.** $p=0.5$ 時二項分配對稱，「兩倍較小尾機率」與 `binom.test()` 雙尾算法相同。

| 類型 | p-value | R |
|---|---|---|
| 左尾 | $P(T\le t_{\text{obs}})$ | `binom.test(t, n, 0.5, alternative = "less")` |
| 右尾 | $P(T\ge t_{\text{obs}})$ | `binom.test(t, n, 0.5, alternative = "greater")` |
| 雙尾 | $2\min\{P(T\le t),P(T\ge t)\}$ | `binom.test(t, n, 0.5)` |

**臨界值.** $r$ = 滿足 $P(T\le r)\le\alpha$ 的最大值（雙尾用 $\alpha/2$）；左尾 $t\le r$、右尾 $t\ge n-r$、雙尾 $t\le r$ 或 $t\ge n-r$。

**大樣本近似.** $n>25$ 時 $r=\tfrac12\left(n+\Phi^{-1}(\alpha)\sqrt n\right)$（雙尾代 $\alpha/2$）。

**R.** `d <- y - x; n <- sum(d != 0); t <- sum(d > 0); binom.test(t, n, 0.5)`。

---

## 15. 序列型態是否隨機 — One-Sample Runs Test（Wald–Wolfowitz）

**目的.** 檢定依發生順序記錄的觀測值是否由隨機過程產生；依據為 run（相同符號連續出現的片段）的個數。

**資料與假設.** 序列順序有意義；每個觀測值可歸為兩種互斥符號之一（連續資料可先依中位數等基準二分）；關心型態是否隨機，而非位置。

**假設檢定.** $H_0$：符號出現的型態由隨機過程決定。
左尾 $H_a$：run 數過少（同類符號聚集，常見於趨勢或分段集中）；右尾 $H_a$：run 數過多（過度交替）；雙尾 $H_a$：型態非隨機。

**統計量.** $n_1$ = $S$ 個數、$n_2$ = $F$ 個數、$n=n_1+n_2$；$U$ = run 總數。$k$ = 兩種符號中較少的 run 數：
$$P(U=2k)=\frac{2\binom{n_1-1}{k-1}\binom{n_2-1}{k-1}}{\binom{n}{n_1}},\qquad
P(U=2k+1)=\frac{\binom{n_1-1}{k}\binom{n_2-1}{k-1}+\binom{n_1-1}{k-1}\binom{n_2-1}{k}}{\binom{n}{n_1}}.$$
$E(U)=\dfrac{2n_1n_2}{n}+1$。

**判斷.** 左尾 $P(U\le u_{\text{obs}})$；右尾 $P(U\ge u_{\text{obs}})$；雙尾 $\min\{1,2\min\{P(U\le u),P(U\ge u)\}\}$。

**大樣本近似.** $n_1$ 或 $n_2>20$ 時
$$Z=\frac{U-(2n_1n_2/n+1)}{\sqrt{2n_1n_2(2n_1n_2-n)/[n^2(n-1)]}}\ \dot\sim\ N(0,1).$$

**R.** `DescTools::RunsTest(x)`：
- 數值向量**自動以中位數二分**；邏輯或二分向量直接使用。
- `alternative` 預設 `"two.sided"`；樣本總數 $\le30$ 預設精確，超過改常態近似（可用 `exact` 指定）。
- 常態近似**預設 continuity correction**（`correct = TRUE`，分子加減 0.5）；要對應上式需設 `correct = FALSE`。

手算 run 數：`s <- ifelse(x > median(x), "S", "F"); length(rle(s)$lengths)`。

---

## 16. 序列是否有趨勢 — Cox and Stuart Test

**目的.** 檢定依時間或次序排列的序列是否存在上升／下降趨勢。作法：後半段與前半段配對後做 sign test（統計量與程序同 sign test，只差在配對方式）。

**資料與假設.** 序列順序有意義；尺度為 ordinal / interval / ratio；關心整體是否朝單一方向變動，而非幅度或函數形式。

**配對.** 序列 $X_1,\ldots,X_{n'}$，令 $c=n'/2$（$n'$ 偶）或 $(n'+1)/2$（$n'$ 奇），
配對 $(X_1,X_{1+c}),(X_2,X_{2+c}),\ldots,(X_{n'-c},X_{n'})$；$n'$ 為奇數時正中間的觀測值不參與。

**統計量.** $X_i<X_{i+c}$ 記「+」、$>$ 記「−」、$=$ 為 tie（**排除**）；$n$ = 排除 tie 後的配對數；
$T$ = 「+」的個數（偏大 ⇒ 上升趨勢、偏小 ⇒ 下降趨勢）；$H_0$ 邊界下 $T\sim\text{Bin}(n,\tfrac12)$。

**假設檢定.** 左尾：$H_0$ 無下降趨勢 vs 有下降趨勢；右尾：$H_0$ 無上升趨勢 vs 有上升趨勢；雙尾：$H_0$ 無趨勢 vs 有上升或下降趨勢。

**判斷.** 同 sign test：左尾 `binom.test(t, n, 0.5, alternative = "less")`；右尾 `"greater"`；雙尾 `binom.test(t, n, 0.5)`。

**R.** `randtests::cox.stuart.test(x)`（配對、排除 tie 與檢定合一，結果應與 `binom.test()` 相同）。

---

## 17. 是否來自指定分配（分組）— Chi-squared Goodness-of-Fit Test

**目的.** 檢定樣本是否來自某個指定分配（敘述整個分配，而非單一參數）。把資料分類，比較觀測次數與期望次數。

**資料與假設.** 觀測值可歸入 $k$ 個互斥類別；連續型分配先把值域切成區間；樣本數需夠大使卡方近似成立。

**假設檢定.** $H_0$：樣本來自指定分配 vs $H_a$：不來自該分配。

**統計量.** $E_i=np_i$（$p_i$ 為 $H_0$ 下落入第 $i$ 類的機率）。
**本報告規則：$E_i<1$ 時與相鄰類別合併**，直到所有 $E_i\ge1$。
$$T=\sum_{i=1}^k\frac{(O_i-E_i)^2}{E_i}=\sum_{i=1}^k\frac{O_i^2}{E_i}-n.$$

**判斷.** $T\approx\chi^2_{\text{df}}$，**只在右尾拒絕**：p-value $=P(\chi^2_{\text{df}}>t_{\text{obs}})$。
df $=k-1$；若有 $g$ 個參數由資料估計，df $=k-g-1$。

**R.** 參數全部已知：`chisq.test(O, p = p_vec)`（df 固定為 $k-1$）；
有估計參數時需自行計算：`pchisq(t_obs, df = k - g - 1, lower.tail = FALSE)`。

---

## 18. 是否來自指定連續分配（參數已知）— Kolmogorov One-Sample Test

**目的.** 檢定樣本是否來自某個**參數完全已知**的連續分配；直接比較 EDF 與指定 CDF 的最大垂直距離，不需分組。

**資料與假設.** 指定分配為連續型、參數完全已知；尺度為 ordinal / interval / ratio；觀測值互相獨立。
**參數若由資料估計，此檢定會變保守，應改用 Lilliefors（第 19 節）。**

**假設檢定.** $F$ 為真實 CDF、$F_o$ 為指定 CDF。
單尾 $H_0:F(x)\ge F_o(x)\ \forall x$；單尾 $H_0:F(x)\le F_o(x)\ \forall x$；雙尾 $H_0:F(x)=F_o(x)\ \forall x$。

**統計量.** EDF $S(x)=\#\{X_i\le x\}/n$。
$$D^+=\sup_x\big(F_o(x)-S(x)\big),\quad D^-=\sup_x\big(S(x)-F_o(x)\big),\quad D=\sup_x|F_o(x)-S(x)|=\max(D^+,D^-).$$
三者依序對應上面三種檢定。手算（排序後 $i=1..n$）：`D_plus <- max(Fo - (i - 1)/n)`、`D_minus <- max(i/n - Fo)`。

**判斷.** 三種檢定的**拒絕域皆在右尾**：統計量大於對應（單尾／雙尾）的 $(1-\alpha)$ 分位數時拒絕。

**Ties.** 有重複值時 EDF 一次跳多階，精確分配不成立，`ks.test()` 會警告；p-value 偏大、檢定較保守。

**R.** `ks.test(x, "p分配名稱", 參數)`，例如 `ks.test(x, "punif")`；`alternative` 指定單尾或雙尾。
$n<100$ 且無重複值時預設精確 p-value，否則用漸近近似。

---

## 19. 是否來自某分配族（參數估計）— Lilliefors Test

**目的.** 檢定樣本是否來自某**分配族**（參數未知、由資料估計）。沿用 Kolmogorov 統計量形式，但改用適合「參數由資料估計」的臨界值（估出的分配本來就貼近樣本，距離偏小）。涵蓋常態與指數兩版本。

**資料與假設.** 檢定對象是整個分配族（例如「是常態」而非 $N(0,16)$）；參數未知、由樣本估計；連續型、觀測值互相獨立。
**參數完全已知時應改用 Kolmogorov 檢定**，其檢定力較佳。

**常態版本.**
- $H_0$：樣本來自常態分配族 vs $H_a$：不來自。
- 標準化 $Z_i=(X_i-\bar X)/S$（$S$ 為分母 $n-1$ 的樣本標準差）。
- $D_1=\sup_z|\Phi(z)-S(z)|$（$S$ 為 $Z_i$ 的 EDF），**右尾**拒絕。
- 標準化方式依哪些參數未知而異：$\mu$ 未知、$\sigma^2$ 已知 → $(X_i-\bar X)/\sigma$；$\mu$ 已知、$\sigma^2$ 未知 → $(X_i-\mu)/S$；兩者皆未知 → $(X_i-\bar X)/S$（最常見）。
- R：`nortest::lillie.test(x)`（對應兩者皆未知）。

**指數版本.**
- $H_0$：$F_o(x)=1-e^{-x/\theta}$，$x>0$，$\theta$ 未知 vs $H_a$：不來自指數分配族。
- 標準化 $Z_i=X_i/\bar X$；$D_2=\sup_{z>0}|F(z)-S(z)|$，$F(z)=1-e^{-z}$。**右尾**拒絕。
- $D_2$ 虛無分配無解析式；Durbin (1975) Table 3 列 $\sqrt n\,D_2$ 的分位數 $w_{1-\alpha}$，$d_2>w_{1-\alpha}/\sqrt n$ 拒絕；$n>100$ 以 $n=100$ 的分位數代入。
- R：`KScorrect::LcKS(x, cdf = "pexp", nreps = 4999)`（Monte Carlo p-value；先 `set.seed()`），回傳 `D.obs` 與 `p.value`。

---

## 20. 常態性 — Shapiro–Wilk Test

**目的.** 檢定樣本是否來自常態分配（平均數與變異數未知）。比較兩種離散程度估計：順序統計量的線性組合（常態下最有效率）vs 一般平方和；常態時兩者接近、$W$ 接近 1。
相同顯著水準下，對常態性的檢定力優於 Kolmogorov–Smirnov 與 Lilliefors。

**資料與假設.** 常態、平均數與變異數未知；連續型、觀測值互相獨立；手算需 $n\le50$（表列範圍），用軟體則無此限制。

**假設檢定.** $H_0$：$F(x)$ 為常態分配（參數未知）vs $H_a$：非常態。

**統計量.** $D=\sum(X_i-\bar X)^2$；排序 $X_{[1]}\le\cdots\le X_{[n]}$，
$$W=\frac{1}{D}\left[\sum_{i=1}^{k}a_i\big(X_{[n-i+1]}-X_{[i]}\big)\right]^2,$$
$n$ 偶 $k=n/2$；$n$ 奇 $k=(n-1)/2$，正中間 $X_{[k+1]}$ 不參與。$a_i$ 查 Shapiro & Wilk (1965) Table 5（$n=2..50$）。

**判斷.** $W\le1$，越接近 1 越符合常態；**拒絕域在左尾**：$W<W_\alpha$（Table 6）時拒絕。

**R.** `shapiro.test(x)`：Royston 近似演算法，可處理 $3\le n\le5000$，直接回傳 $W$ 與 p-value。
