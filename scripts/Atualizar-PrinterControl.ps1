<#
    Atualizar-PrinterControl.ps1

    Baixa a versao mais recente do repositorio (branch main) direto do
    GitHub e sobrescreve so os arquivos do codigo — sem precisar instalar
    Git. Pensado para maquinas de dominio onde instalar ferramentas nao e
    uma opcao.

    O QUE E PRESERVADO
    -------------------
    backend\.env, .env.local, qualquer *.db (+ -shm/-wal/-journal), venv\,
    node_modules\, .next\ e logs\ nunca sao tocados. A copia e so por cima
    (overwrite) — nunca um "mirror" que apaga o que nao existe na origem,
    porque isso apagaria configuracao e banco de dados locais.

    USO
    ----
        # de dentro da pasta do projeto (a que tem backend\ e src\)
        powershell -ExecutionPolicy Bypass -File .\scripts\Atualizar-PrinterControl.ps1

    Depois de atualizar, se backend\requirements.txt ou package.json
    mudaram desde a ultima vez, rode tambem:
        pip install -r backend\requirements.txt
        npm install
#>

[CmdletBinding()]
param(
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"

$Destino = (Get-Item "$PSScriptRoot\..").FullName
$ZipUrl = "https://github.com/devribero/PrinterControl/archive/refs/heads/$Branch.zip"
$Temp = Join-Path $env:TEMP "printercontrol-update-$(Get-Random)"
$ZipPath = Join-Path $Temp "codigo.zip"

New-Item -ItemType Directory -Path $Temp | Out-Null

try {
    Write-Host "Baixando '$Branch' do GitHub..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $ZipUrl -OutFile $ZipPath

    Write-Host "Extraindo..." -ForegroundColor Cyan
    Expand-Archive -Path $ZipPath -DestinationPath $Temp -Force

    $Origem = Get-ChildItem $Temp -Directory | Where-Object { $_.Name -like "PrinterControl-*" } | Select-Object -First 1
    if (-not $Origem) {
        throw "Nao encontrei a pasta extraida dentro de $Temp — o ZIP baixado pode estar corrompido."
    }

    Write-Host "Copiando arquivos por cima de $Destino (nada local e apagado)..." -ForegroundColor Cyan

    robocopy $Origem.FullName $Destino /E `
        /XD ".git" "venv" "node_modules" ".next" "logs" `
        /XF ".env" ".env.local" "*.db" "*.db-shm" "*.db-wal" "*.db-journal" `
        /NFL /NDL /NJH /NP | Out-Null

    Write-Host "Pronto! Codigo atualizado para a ultima versao de '$Branch'." -ForegroundColor Green
    Write-Host "Se backend\requirements.txt ou package.json mudaram, rode tambem:" -ForegroundColor Yellow
    Write-Host "  pip install -r backend\requirements.txt"
    Write-Host "  npm install"
}
finally {
    if (Test-Path $Temp) { Remove-Item $Temp -Recurse -Force }
}
