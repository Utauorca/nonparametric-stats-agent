"""無母數統計專家 agent 的核心邏輯（可切換 Gemini / Claude）。

設計：
- 對外只有一個 NonparametricAgent；它依 .env 的 LLM_PROVIDER 選擇後端。
- 兩個後端 (_GeminiBackend / _ClaudeBackend) 共用同一組工具 (tools.py) 與系統提示 (prompts.py)。
- 介面層 (cli.py) 完全不用知道用的是哪一家。

要新增第三家 LLM，只要再寫一個後端類別、在 NonparametricAgent 裡多一個分支即可，
prompts.py、tools.py、cli.py 都不用動。
"""

import os

from dotenv import load_dotenv

from .prompts import SYSTEM_PROMPT
from . import tools

# 從 .env 讀取設定（LLM_PROVIDER、各家的 API key 與模型）
load_dotenv()


class AgentError(RuntimeError):
    """對使用者友善的錯誤（額度、忙碌、金鑰、未安裝套件等）。cli 會顯示成一行提示。"""


# 三個工具的分派表 —— 兩家後端共用同一組 tools.py 函式
_TOOL_DISPATCH = {
    "read_file": tools.read_file,
    "write_file": tools.write_file,
    "run_python": tools.run_python,
}


# ============================================================
# Gemini 後端
# ============================================================
class _GeminiBackend:
    """用 google-genai。工具走 automatic function calling（SDK 自動執行）。"""

    def __init__(self, model: str):
        try:
            from google import genai
        except ImportError as e:
            raise AgentError("未安裝 google-genai，請執行：pip install google-genai") from e
        if not os.getenv("GEMINI_API_KEY"):
            raise AgentError("找不到 GEMINI_API_KEY，請在 .env 填入你的 Gemini 金鑰。")
        self._genai = genai
        self.model = model
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.chat = self._new_chat()

    def _new_chat(self):
        from google.genai import types

        return self.client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=[tools.read_file, tools.write_file, tools.run_python],
            ),
        )

    def ask(self, user_message: str) -> str:
        from google.genai import errors

        try:
            chunks: list[str] = []
            for chunk in self.chat.send_message_stream(user_message):
                text = _text_from_gemini_chunk(chunk)
                if text:
                    chunks.append(text)
            return "".join(chunks)
        except errors.APIError as e:
            raise AgentError(_gemini_error_hint(e)) from e

    def reset(self) -> None:
        self.chat = self._new_chat()


def _text_from_gemini_chunk(chunk) -> str:
    """從串流片段取純文字，忽略 function_call 等非文字部分（避免 SDK warning）。"""
    if not chunk.candidates:
        return ""
    content = chunk.candidates[0].content
    if not content or not content.parts:
        return ""
    return "".join(p.text for p in content.parts if getattr(p, "text", None))


def _gemini_error_hint(e) -> str:
    code = getattr(e, "code", None)
    if code == 429:
        return "額度暫時用盡或請求太頻繁 (429)。等 30–60 秒再試，或在 .env 換 GEMINI_MODEL（額度分開算）。"
    if code == 503:
        return "模型當下太忙 (503)。稍等幾秒再送一次即可。"
    return f"Gemini API 錯誤 ({code})：{getattr(e, 'message', e)}"


# ============================================================
# Claude 後端
# ============================================================
# Claude 需要明確的工具 JSON schema（Gemini 是從函式簽名自動產生）
_CLAUDE_TOOLS = [
    {
        "name": "read_file",
        "description": "讀取專案資料夾內的檔案並回傳內容，例如讀取 CSV 資料檔。",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "相對於專案根目錄的路徑，例如 data/sample.csv"}
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "把文字內容寫入專案資料夾內的檔案，例如存下報告或程式碼。",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "相對於專案根目錄的路徑"},
                "content": {"type": "string", "description": "要寫入的文字內容"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "run_python",
        "description": (
            "在本機執行 Python（已裝 numpy/pandas/scipy），用來實際計算統計量與 p 值。"
            "工作目錄為專案根目錄；請用 print() 把結果印出來。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {"code": {"type": "string", "description": "要執行的 Python 原始碼"}},
            "required": ["code"],
        },
    },
]


class _ClaudeBackend:
    """用 anthropic SDK。手動 tool-use 迴圈：呼叫工具 → 回結果 → 直到不再要求工具。"""

    def __init__(self, model: str):
        try:
            import anthropic
        except ImportError as e:
            raise AgentError("未安裝 anthropic，請執行：pip install anthropic") from e
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise AgentError("找不到 ANTHROPIC_API_KEY，請在 .env 填入你的 Claude 金鑰。")
        self._anthropic = anthropic
        self.model = model
        self.client = anthropic.Anthropic()
        self.messages: list[dict] = []

    def ask(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})
        try:
            while True:
                resp = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=SYSTEM_PROMPT,
                    tools=_CLAUDE_TOOLS,
                    messages=self.messages,
                )
                # 一定要把完整 content 存回歷史（含 tool_use 區塊）
                self.messages.append({"role": "assistant", "content": resp.content})

                if resp.stop_reason != "tool_use":
                    return "".join(b.text for b in resp.content if b.type == "text")

                # 執行 Claude 要求的每個工具，把結果一起回傳
                results = []
                for b in resp.content:
                    if b.type == "tool_use":
                        fn = _TOOL_DISPATCH.get(b.name)
                        out = fn(**b.input) if fn else f"未知工具：{b.name}"
                        results.append(
                            {"type": "tool_result", "tool_use_id": b.id, "content": out}
                        )
                self.messages.append({"role": "user", "content": results})
        except self._anthropic.APIError as e:
            raise AgentError(_claude_error_hint(e)) from e

    def reset(self) -> None:
        self.messages = []


def _claude_error_hint(e) -> str:
    code = getattr(e, "status_code", None)
    if code == 429:
        return "額度或速率限制 (429)。等一下再試，或在 .env 改 ANTHROPIC_MODEL。"
    if code == 529:
        return "Claude 服務忙碌中 (529)。稍等幾秒再送一次。"
    if code == 401:
        return "金鑰無效 (401)。請檢查 .env 的 ANTHROPIC_API_KEY。"
    return f"Claude API 錯誤 ({code})：{getattr(e, 'message', e)}"


# ============================================================
# 對外的統一介面
# ============================================================
class NonparametricAgent:
    """依 .env 的 LLM_PROVIDER 選用 Gemini 或 Claude；對外介面完全一致。"""

    def __init__(self):
        provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
        if provider == "gemini":
            self._backend = _GeminiBackend(os.getenv("GEMINI_MODEL", "gemini-3.8-flash"))
        elif provider == "claude":
            self._backend = _ClaudeBackend(os.getenv("ANTHROPIC_MODEL", "claude-opus-4-8"))
        else:
            raise AgentError(
                f"未知的 LLM_PROVIDER：'{provider}'（請在 .env 設成 gemini 或 claude）"
            )
        self.provider = provider
        self.model = self._backend.model

    def ask(self, user_message: str) -> str:
        return self._backend.ask(user_message)

    def reset(self) -> None:
        self._backend.reset()
