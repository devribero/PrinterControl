@echo off
REM Iniciar-Sistema.bat
REM
REM Sobe o backend (FastAPI/uvicorn, usando o venv de backend\venv) e o
REM frontend (Next.js, "npm run dev") cada um na sua propria janela, para
REM dar duplo-clique e testar o sistema completo sem digitar nada.
REM
REM So para DESENVOLVIMENTO/TESTE local. Producao de verdade usa o servico
REM do Windows (scripts\Servico-PrinterControl.ps1) — ver docs\OPERATIONS.md.

setlocal
set "ROOT=%~dp0"

if not exist "%ROOT%backend\venv\Scripts\activate.bat" (
    echo [ERRO] Nao encontrei o venv em backend\venv
    echo Crie o venv antes: cd backend ^&^& python -m venv venv ^&^& venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo Iniciando PrinterControl...
echo.

start "PrinterControl - Backend" cmd /k "cd /d "%ROOT%backend" && call venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

start "PrinterControl - Frontend" cmd /k "cd /d "%ROOT%" && npm run dev"

echo Backend e frontend abrindo em janelas separadas.
echo   Backend:  http://127.0.0.1:8000
echo   Frontend: http://localhost:3000
echo.
echo Para parar, feche as duas janelas (ou Ctrl+C em cada uma).
pause
