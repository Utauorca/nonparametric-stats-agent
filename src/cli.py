"""終端機互動介面：跟無母數統計專家對話，回覆以 Markdown 渲染。

執行方式（在專案根目錄）：
    python -m src.cli
"""

from rich.console import Console
from rich.markdown import Markdown

from .agent import NonparametricAgent, AgentError

console = Console()


def main() -> None:
    console.rule("[bold]無母數統計專家 Agent[/]")

    # 建立 agent（會依 .env 的 LLM_PROVIDER 選 Gemini 或 Claude）
    try:
        agent = NonparametricAgent()
    except AgentError as e:
        console.print(f"[red]啟動失敗：{e}[/]")
        return

    console.print(f"[dim]目前使用：{agent.provider} / {agent.model}[/]")
    console.print("輸入問題開始諮詢。指令：[cyan]/reset[/] 重新開始、[cyan]/exit[/] 離開")

    while True:
        try:
            user_input = input("\n你> ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n再見！")
            break

        if not user_input:
            continue
        if user_input in ("/exit", "/quit"):
            console.print("再見！")
            break
        if user_input == "/reset":
            agent.reset()
            console.print("[dim]（已清空對話，開始新的諮詢）[/]")
            continue

        # 收整段回覆時顯示轉圈提示，讓使用者知道它在思考／跑工具
        try:
            with console.status("[bold cyan]專家思考中…[/]", spinner="dots"):
                answer = agent.ask(user_input)
        except AgentError as e:  # 額度／忙碌／金鑰等 → 友善提示，程式繼續
            console.print(f"[yellow]⚠️ {e}[/]")
            continue
        except Exception as e:  # 其他非預期錯誤：印簡短訊息，不讓程式崩潰
            console.print(f"[red]⚠️ 發生錯誤：{type(e).__name__}: {e}[/]")
            continue

        # 收完後一次把 Markdown 渲染成有格式的樣子
        if answer.strip():
            console.print("\n[bold green]專家 ▸[/]")
            console.print(Markdown(answer))


if __name__ == "__main__":
    main()
