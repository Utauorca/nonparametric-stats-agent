# 無母數統計專家 Agent (Nonparametric Statistics Agent)

一個**無母數統計對話式 AI 顧問**，**同時支援 Google Gemini 與 Anthropic Claude**（在 `.env` 用 `LLM_PROVIDER` 切換，各自填自己的金鑰）。它能協助你判斷該用哪一種
無母數方法、說明假設與限制、正確解讀 p 值與效果量，並給出可直接執行的 Python / R 程式碼。

涵蓋方法：符號檢定、Wilcoxon signed-rank、Mann-Whitney U、Kruskal-Wallis、Friedman、
Spearman / Kendall 相關、Kolmogorov-Smirnov、permutation / bootstrap 等。

---

## 給使用者：怎麼用（clone 後在本機跑）

### 1. 取得程式碼
```bash
git clone https://github.com/<你的帳號>/nonparametric-stats-agent.git
cd nonparametric-stats-agent
```

### 2. 建立虛擬環境並安裝套件
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. 選一家 LLM 並填入金鑰
```bash
cp .env.example .env      # Windows 用 copy .env.example .env
```
打開 `.env`，用 `LLM_PROVIDER` 選一家，填對應的金鑰（**一把金鑰只能用它自己那家**）：

- **用 Gemini**：`LLM_PROVIDER=gemini`，填 `GEMINI_API_KEY`
  （申請：<https://aistudio.google.com/apikey>，有免費額度）
- **用 Claude**：`LLM_PROVIDER=claude`，填 `ANTHROPIC_API_KEY`
  （申請：<https://console.anthropic.com/>）
> ⚠️ `.env` 已列入 `.gitignore`，**不會**被上傳到 GitHub。永遠不要把 key 寫進程式碼或 commit 出去。

### 4. 開始對話
Windows 最簡單：對 `run.bat` **點兩下**（會自動用 venv 啟動並修正中文編碼）。

或用終端機：
```bash
python -m src.cli
```
輸入問題即可，例如：
> 我有兩組獨立樣本、每組 15 筆、資料不常態，想比較中位數差異，該用什麼檢定？

指令：`/reset` 重新開始一段諮詢、`/exit` 離開。

---

## 專案結構與各檔案的邏輯

```
nonparametric-stats-agent/
├── README.md            ← 說明文件（你正在看）
├── requirements.txt     ← 需要安裝的 Python 套件
├── .env.example         ← API key 範本；使用者複製成 .env 填自己的 key
├── .gitignore           ← 確保 .env 等機密不上傳
├── data/
│   └── sample_two_groups.csv  ← 測試資料：A 組 n=15、B 組 n=10（long 格式）
└── src/
    ├── __init__.py      ← 讓 src 成為一個 Python 套件
    ├── prompts.py       ← 系統提示：定義 agent 的「專業與人格」，改行為改這裡
    ├── tools.py         ← 工具：read_file / run_python / write_file（限定專案資料夾內）
    ├── agent.py         ← 核心邏輯：依 LLM_PROVIDER 切換 Gemini/Claude 後端、管理對話、掛上工具
    └── cli.py           ← 終端機介面：讀取輸入、印出回覆、處理指令
```

### 工具能力 (function calling)
| 工具 | 作用 | 安全限制 |
|---|---|---|
| `read_file` | 讀取專案內檔案（例如 CSV 資料） | 只能讀專案資料夾內 |
| `run_python` | 用 numpy/pandas/scipy 實際計算 | 本機執行、60 秒逾時、工作目錄為專案根目錄 |
| `write_file` | 寫入報告 / 程式碼 | 只能寫專案資料夾內 |

**設計原則：邏輯與介面分離。**
- `agent.py` 的 `NonparametricAgent` 不管介面，只負責「記住對話 + 呼叫模型」。
  由於 Anthropic API 是無狀態的，每次請求都要把完整對話歷史送回去，這個類別替你維護那份歷史。
- `cli.py` 只是其中一種介面。之後若想改成 Streamlit 網頁或接成別人的套件，
  只要 `from src.agent import NonparametricAgent` 再包一層即可，核心不用改。
- `prompts.py` 把「專業知識與回答規則」抽出來。要擴充涵蓋的檢定或調整回答風格，改這一個檔案就好。

---

## 給開發者：如何當函式庫使用

```python
from src.agent import NonparametricAgent

agent = NonparametricAgent()
answer = agent.ask("Kruskal-Wallis 顯著之後，事後檢定該怎麼做？")
print(answer)        # 也會即時串流印出
```

---

## 常見問題

- **要花錢嗎？** 看你選哪家。**Gemini** 的 flash 模型（預設 `gemini-3.8-flash`）在**免費層**即可跑；
  pro 級免費層額度為 0，需付費。**Claude** 依 token 計費（新帳號通常有免費 credit）。
  模型可在 `.env` 用 `GEMINI_MODEL` / `ANTHROPIC_MODEL` 切換。
- **一把金鑰能用另一家嗎？** 不行。API 金鑰綁定各自的供應商 —— Gemini 金鑰只能叫 Gemini，
  Claude 金鑰只能叫 Claude。本專案是讓你**用 `LLM_PROVIDER` 選一家、填那家的金鑰**。
- **它會自己跑我的資料嗎？** 會。已接上工具 (function calling)：它能 `read_file` 讀取
  `data/` 底下的 CSV、用 `run_python` 實際以 scipy 計算、再用 `write_file` 存下報告。
  所有檔案存取都被限制在專案資料夾內；`run_python` 在你本機執行、有 60 秒逾時。

## Claude Agent Skill（另一種用法）

除了上面的獨立 Python agent，本 repo 也附了一份 **Claude Agent Skill**，位於
`.claude/skills/nonparametric-stats/`。用 Claude Code / Claude 開啟本 repo 時會**自動載入**，
讓 Claude 在你問無母數問題時依決策樹判斷方法、說明假設、並給效果量。

```
.claude/skills/nonparametric-stats/
├── SKILL.md                      # 主檔：觸發條件(frontmatter) + 回答流程
├── references/
│   ├── decision-tree.md          # 方法選擇決策樹(mermaid 流程圖)
│   ├── methods.md                # 各檢定速查
│   └── textbook-methods.md       # 完整版：假設/公式/ties/判斷規則/R code
└── scripts/
    └── run_test.py               # 用 scipy 實算 Mann-Whitney / Wilcoxon / Kruskal
```

Skill 與 Python agent 共享同一套專業知識，只是掛載方式不同：Skill 掛在 Claude Code 上，
Python agent 則是可獨立執行的程式。

## 延伸方向（選做）
- ✅ ~~加 tool use 讓 agent 直接算檢定~~（已完成，見上表）
- ✅ ~~做成 Claude Agent Skill~~（已完成，見上節）
- 換成 **Streamlit** 網頁介面，支援上傳 CSV。
- 加入 **RAG**：把無母數統計教科書或講義做成知識庫，讓回答有出處。

## 授權
建議加一個 `LICENSE` 檔（例如 MIT）再公開。
