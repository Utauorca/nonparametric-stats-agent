@echo off
REM 無母數統計 Agent：一鍵安裝 + 啟動。
REM 第一次點兩下會自動建立虛擬環境、安裝套件、建立 .env；之後點兩下即直接啟動。
chcp 950 >nul
pushd "%~dp0"
set PYTHONUTF8=1

REM --- 1. 尋找 Python ---
set "PYCMD=python"
where python >nul 2>nul
if errorlevel 1 (
  set "PYCMD=py"
  where py >nul 2>nul
  if errorlevel 1 (
    echo [錯誤] 找不到 Python，請先安裝 Python 3.10 以上：
    echo        https://www.python.org/downloads/
    echo        安裝時記得勾選 "Add Python to PATH"。
    pause
    popd
    exit /b 1
  )
)

REM --- 2. 沒有虛擬環境就自動建立並安裝套件（只在第一次） ---
if not exist ".venv\Scripts\python.exe" (
  echo [設定] 第一次執行：建立虛擬環境中...
  %PYCMD% -m venv .venv
  if errorlevel 1 (
    echo [錯誤] 建立虛擬環境失敗。
    pause
    popd
    exit /b 1
  )
  echo [設定] 安裝套件中（第一次會花幾分鐘，請稍候）...
  ".venv\Scripts\python.exe" -m pip install --upgrade pip >nul
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 (
    echo [錯誤] 套件安裝失敗，請檢查網路連線或 requirements.txt。
    pause
    popd
    exit /b 1
  )
  echo [設定] 套件安裝完成。
)

REM --- 3. 沒有 .env 就從範本複製，並請使用者填金鑰後再啟動 ---
if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo.
  echo [設定] 已為你建立 .env 檔。請在打開的記事本中選一家 LLM 並填入金鑰：
  echo        - 用 Gemini：LLM_PROVIDER=gemini，填 GEMINI_API_KEY
  echo          ^(免費額度申請：https://aistudio.google.com/apikey^)
  echo        - 用 Claude：LLM_PROVIDER=claude，填 ANTHROPIC_API_KEY
  echo.
  echo        填好、存檔、關閉記事本後，再點兩下 run.bat 就會開始對話。
  echo.
  pause
  notepad ".env"
  popd
  exit /b 0
)

REM --- 4. 一切就緒，啟動 agent ---
".venv\Scripts\python.exe" -m src.cli
echo.
pause >nul
popd