"""agent 可以呼叫的工具 (function calling)。

安全設計：
- 所有檔案存取都被限制在「專案資料夾」內，模型無法讀寫專案以外的東西。
- run_python 在本機子行程執行，有 60 秒逾時上限。
- run_r 以 Rscript 在本機子行程執行 R 程式，同樣有 60 秒逾時上限。

這些函式會被當成工具傳給 Gemini；模型需要時會「要求」呼叫，
實際執行的是這裡的 Python 程式（不是模型自己）。函式的 docstring 與型別註記
會自動變成模型看到的工具說明，所以寫清楚很重要。
"""

import glob
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# 專案根目錄（本檔案的上一層）。所有檔案操作都不得超出這裡。
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _safe_path(path: str) -> Path:
    """把相對路徑轉成絕對路徑，並確認它沒有跑出專案資料夾。"""
    p = (PROJECT_ROOT / path).resolve()
    if PROJECT_ROOT not in p.parents and p != PROJECT_ROOT:
        raise ValueError(f"路徑超出專案資料夾，拒絕存取：{path}")
    return p


def read_file(path: str) -> str:
    """讀取專案資料夾內的檔案並回傳內容，例如讀取 CSV 資料檔。

    Args:
        path: 相對於專案根目錄的檔案路徑，例如 "data/sample_two_groups.csv"。
    """
    try:
        text = _safe_path(path).read_text(encoding="utf-8")
        if len(text) > 20000:
            text = text[:20000] + "\n...（檔案過長，已截斷）"
        return text
    except Exception as e:  # 回傳錯誤字串，讓模型知道並調整
        return f"讀取失敗：{e}"


def write_file(path: str, content: str) -> str:
    """把文字內容寫入專案資料夾內的檔案，例如存下分析報告或程式碼。

    Args:
        path: 相對於專案根目錄的檔案路徑，例如 "outputs/report.md"。
        content: 要寫入的文字內容。
    """
    try:
        p = _safe_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"已寫入 {path}（{len(content)} 字元）"
    except Exception as e:
        return f"寫入失敗：{e}"


def run_python(code: str) -> str:
    """在本機執行一段 Python 程式並回傳 stdout / stderr。

    環境已安裝 numpy、pandas、scipy。這是「真正計算數字」的工具：
    需要算檢定統計量、p 值、效果量，或用 pandas 讀取分析資料時，一律用這個工具，
    不要用心算或憑空給數字。工作目錄就是專案根目錄，可直接讀 data/ 底下的檔案。

    Args:
        code: 要執行的 Python 原始碼。請用 print() 把結果印出來才看得到。
    """
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        parts = []
        if result.stdout.strip():
            parts.append("[stdout]\n" + result.stdout.strip())
        if result.stderr.strip():
            parts.append("[stderr]\n" + result.stderr.strip())
        return "\n".join(parts) or "（程式沒有任何輸出，記得用 print()）"
    except subprocess.TimeoutExpired:
        return "執行逾時（超過 60 秒）"
    except Exception as e:
        return f"執行失敗：{e}"


def _find_rscript() -> str | None:
    """依序從 .env 的 RSCRIPT_PATH、PATH、預設安裝位置找 Rscript.exe。"""
    env_path = os.getenv("RSCRIPT_PATH")
    if env_path and Path(env_path).exists():
        return env_path
    found = shutil.which("Rscript")
    if found:
        return found
    candidates = sorted(glob.glob(r"C:\Program Files\R\R-*\bin\Rscript.exe"))
    return candidates[-1] if candidates else None


def run_r(code: str) -> str:
    """在本機用 Rscript 執行一段 R 程式並回傳 stdout / stderr。

    使用者的報告以 R 撰寫；需要算檢定統計量、p 值時優先用這個工具，
    函式與參數要和報告一致（例如 binom.test、mcnemar.test、DescTools::RunsTest）。
    工作目錄就是專案根目錄，可直接讀 data/ 底下的檔案。

    Args:
        code: 要執行的 R 原始碼。請用 print() 或 cat() 把結果印出來。
    """
    rscript = _find_rscript()
    if rscript is None:
        return "找不到 Rscript。請確認已安裝 R，或在 .env 設定 RSCRIPT_PATH。"

    with tempfile.NamedTemporaryFile(
        "w", suffix=".R", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        script_path = f.name

    try:
        result = subprocess.run(
            [rscript, script_path],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        parts = []
        if result.stdout.strip():
            parts.append("[stdout]\n" + result.stdout.strip())
        if result.stderr.strip():
            parts.append("[stderr]\n" + result.stderr.strip())
        return "\n".join(parts) or "（程式沒有任何輸出，記得用 print() 或 cat()）"
    except subprocess.TimeoutExpired:
        return "執行逾時（超過 60 秒）"
    except Exception as e:
        return f"執行失敗：{e}"
    finally:
        os.remove(script_path)
