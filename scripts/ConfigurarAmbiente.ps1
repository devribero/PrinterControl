<#
    ConfigurarAmbiente.ps1

    Assistente interativo para gerar o backend\.env. Feito para uso manual,
    nao para automacao: cada pergunta explica em portugues simples o que o
    campo faz, valida a resposta na hora e mostra um resumo antes de gravar.

    USO
    ----
        pwsh .\scripts\ConfigurarAmbiente.ps1

    O script pergunta se voce esta configurando development, demo ou
    production e segue caminhos diferentes:
      - development/demo: preenche valores padrao seguros, so pede
        confirmacao.
      - production: pergunta cada campo obrigatorio, um de cada vez, com
        validacao (SECRET_KEY, CORS_ORIGINS, PRINT_SERVER_MODE, etc).

    Sempre faz backup do .env anterior (backend\.env.bak-AAAAMMDD-HHmmss)
    antes de sobrescrever, e no final oferece reiniciar o backend pela
    tarefa agendada (scripts\Servico-PrinterControl.ps1).
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$RaizProjeto = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$BackendDir  = Join-Path $RaizProjeto "backend"
$EnvPath     = Join-Path $BackendDir ".env"

function Titulo($Texto) {
    Write-Host ""
    Write-Host "=== $Texto ===" -ForegroundColor Cyan
}

function Info($Texto) {
    Write-Host $Texto -ForegroundColor Gray
}

function Aviso($Texto) {
    Write-Host $Texto -ForegroundColor Yellow
}

function Erro($Texto) {
    Write-Host $Texto -ForegroundColor Red
}

function Ok($Texto) {
    Write-Host $Texto -ForegroundColor Green
}

function Perguntar-SimNao($Pergunta, [bool]$PadraoSim = $true) {
    $sufixo = if ($PadraoSim) { "[S/n]" } else { "[s/N]" }
    while ($true) {
        $resp = Read-Host "$Pergunta $sufixo"
        if ([string]::IsNullOrWhiteSpace($resp)) { return $PadraoSim }
        switch ($resp.Trim().ToLower()) {
            "s" { return $true }
            "sim" { return $true }
            "y" { return $true }
            "n" { return $false }
            "nao" { return $false }
            "não" { return $false }
            default { Aviso "Responda com s ou n." }
        }
    }
}

function Gerar-SecretKey {
    # 48 bytes aleatorios, url-safe, sem depender do python estar no PATH.
    $bytes = New-Object byte[] 48
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    $b64 = [Convert]::ToBase64String($bytes)
    return $b64.Replace("+", "-").Replace("/", "_").Replace("=", "")
}

function Perguntar-Campo {
    param(
        [string]$Pergunta,
        [string]$Explicacao,
        [string]$Padrao = "",
        [scriptblock]$Validador = $null,
        [switch]$PermitirVazio
    )

    if ($Explicacao) { Info $Explicacao }
    while ($true) {
        $rotulo = if ($Padrao) { "$Pergunta [$Padrao]" } else { $Pergunta }
        $valor = Read-Host $rotulo
        if ([string]::IsNullOrWhiteSpace($valor)) {
            if ($Padrao) { $valor = $Padrao }
            elseif ($PermitirVazio) { return "" }
            else { Aviso "Este campo nao pode ficar vazio."; continue }
        }
        if ($Validador) {
            $resultado = & $Validador $valor
            if ($resultado -is [string] -and $resultado) {
                Aviso $resultado
                continue
            }
        }
        return $valor
    }
}

# ---------------------------------------------------------------------------
# 1. Escolher o ambiente
# ---------------------------------------------------------------------------

Titulo "Configurar backend\.env"
Info "Este assistente monta o arquivo backend\.env do zero, perguntando"
Info "cada configuracao em linguagem simples. Nada e gravado ate voce"
Info "confirmar o resumo no final."

Write-Host ""
Write-Host "Qual ambiente voce esta configurando?"
Write-Host "  1) development  - sua propria maquina, para programar/testar"
Write-Host "  2) demo         - instancia de demonstracao, dados ficticios"
Write-Host "  3) production   - frota real, atendendo usuarios de verdade"
Write-Host ""

$ambiente = $null
while (-not $ambiente) {
    $escolha = Read-Host "Digite 1, 2 ou 3"
    switch ($escolha.Trim()) {
        "1" { $ambiente = "development" }
        "2" { $ambiente = "demo" }
        "3" { $ambiente = "production" }
        default { Aviso "Digite 1, 2 ou 3." }
    }
}

Ok "Ambiente escolhido: $ambiente"

# Valores que serao gravados, na mesma ordem do backend\.env.example.
$valores = [ordered]@{
    DATABASE_URL                 = "sqlite:///./printer_control.db"
    ENVIRONMENT                  = $ambiente
    SECRET_KEY                   = ""
    ALLOW_MOCK_COLLECT           = "false"
    COLLECTION_ENABLED           = "false"
    COLLECTION_INTERVAL_MINUTES  = "5"
    COLLECTION_MODE              = "real"
    COLLECTION_SCENARIO          = "online_mono"
    COLLECTION_MAX_WORKERS       = "4"
    PRINT_SERVER_MODE            = "mock"
    PRINT_SERVER_HOST            = "elgjunprt"
    PRINT_SERVER_TIMEOUT_SECONDS = "30"
    SNMP_COMMUNITY                = "public"
    SNMP_TIMEOUT                  = "1.5"
    SNMP_RETRIES                  = "1"
    WEBHOOK_URL                   = ""
    WEBHOOK_TIMEOUT_SECONDS        = "5"
    CORS_ORIGINS                   = ""
    LOG_LEVEL                      = "INFO"
    LOG_FILE                       = "logs/printercontrol.log"
    LOG_MAX_BYTES                  = "5242880"
    LOG_BACKUP_COUNT                = "10"
    LOGIN_MAX_ATTEMPTS               = "5"
    LOGIN_WINDOW_SECONDS              = "900"
    TRUST_PROXY_HEADERS               = "false"
}

# ---------------------------------------------------------------------------
# 2. Caminho development / demo — preenche padrao, so confirma
# ---------------------------------------------------------------------------

if ($ambiente -ne "production") {
    Titulo "Valores padrao para '$ambiente'"

    if ($ambiente -eq "development") {
        $valores.ALLOW_MOCK_COLLECT = "true"
        $valores.COLLECTION_MODE = "mock"
        $valores.PRINT_SERVER_MODE = "mock"
        $valores.COLLECTION_ENABLED = "true"
        $valores.SECRET_KEY = "dev-secret-key-change-in-production"
        Info "Em development a coleta e simulada (mock), sem tocar em"
        Info "impressoras ou Print Server reais. E seguro rodar sem risco de"
        Info "misturar dados ficticios com uma frota de verdade."
    } else {
        # demo
        $valores.ALLOW_MOCK_COLLECT = "true"
        $valores.COLLECTION_MODE = "mock"
        $valores.PRINT_SERVER_MODE = "mock"
        $valores.COLLECTION_ENABLED = "true"
        $valores.SECRET_KEY = Gerar-SecretKey
        Info "Em demo os dados tambem sao simulados, mas a interface avisa"
        Info "isso para quem estiver vendo o painel. A chave de seguranca e"
        Info "gerada automaticamente (nao precisa ser guardada com cuidado"
        Info "extra, pois esta instancia nao tem dados reais)."
    }

    Write-Host ""
    Write-Host "Resumo dos valores que serao usados:" -ForegroundColor Cyan
    foreach ($chave in $valores.Keys) {
        if ($chave -eq "SECRET_KEY") {
            Write-Host "  $chave = (gerada / valor de desenvolvimento, oculta aqui)"
        } else {
            Write-Host "  $chave = $($valores[$chave])"
        }
    }

    if (-not (Perguntar-SimNao "Confirma esses valores?" $true)) {
        Erro "Cancelado. Nada foi gravado."
        exit 1
    }
}

# ---------------------------------------------------------------------------
# 3. Caminho production — pergunta campo a campo, com validacao
# ---------------------------------------------------------------------------

if ($ambiente -eq "production") {
    Titulo "Configuracao de PRODUCAO"
    Aviso "Esta instancia vai atender usuarios reais. O backend recusa subir"
    Aviso "se algum destes campos estiver incoerente com producao — o"
    Aviso "assistente valida tudo antes de gravar para voce nao descobrir"
    Aviso "o erro so quando o servico cair."

    # --- SECRET_KEY ---
    Titulo "Chave de seguranca (SECRET_KEY)"
    Info "E a chave usada para assinar o login de cada usuario (o token que"
    Info "prova que alguem esta autenticado). Precisa ter pelo menos 32"
    Info "caracteres e ser unica desta instancia — nunca reaproveite a de"
    Info "outro ambiente."
    if (Perguntar-SimNao "Quer que eu gere uma chave aleatoria segura agora?" $true) {
        $valores.SECRET_KEY = Gerar-SecretKey
        Ok "Chave gerada. Ela sera mostrada no resumo antes de gravar."
    } else {
        $valores.SECRET_KEY = Perguntar-Campo `
            -Pergunta "Cole a SECRET_KEY" `
            -Explicacao "Minimo 32 caracteres." `
            -Validador {
                param($v)
                if ($v -eq "dev-secret-key-change-in-production") {
                    return "Essa e a chave padrao de desenvolvimento — nao pode ser usada em producao."
                }
                if ($v.Length -lt 32) {
                    return "Muito curta ($($v.Length) caracteres). Use pelo menos 32."
                }
                return $null
            }
    }

    # --- CORS_ORIGINS ---
    Titulo "Endereco do painel (CORS_ORIGINS)"
    Info "E o endereco (URL) onde o painel web fica hospedado — por exemplo"
    Info "o dominio da Vercel. O backend so aceita pedidos vindos desse"
    Info "endereco; qualquer outro site e bloqueado por seguranca."
    Info "Precisa comecar com https:// e nao pode ser localhost."
    $valores.CORS_ORIGINS = Perguntar-Campo `
        -Pergunta "Endereco do painel" `
        -Padrao "https://printercontrol.vercel.app" `
        -Validador {
            param($v)
            if (-not $v.StartsWith("https://")) {
                return "Precisa comecar com https:// (o token de login trafega no pedido; sem HTTPS ele ficaria exposto)."
            }
            if ($v -match "localhost|127\.0\.0\.1") {
                return "Endereco local nao e permitido em producao — isso indica um .env de desenvolvimento copiado por engano."
            }
            return $null
        }

    # --- PRINT_SERVER_MODE / HOST ---
    Titulo "Servidor de impressao (Print Server)"
    Info "Em producao a coleta PRECISA vir de impressoras reais — se ficar"
    Info "em modo simulado, o proximo sincronismo vai apagar a frota real e"
    Info "colocar uma fila inventada no lugar. Por isso este campo e fixo"
    Info "em 'real' para producao."
    $valores.PRINT_SERVER_MODE = "real"
    Ok "PRINT_SERVER_MODE = real (fixo, nao pode ser mock em producao)"

    $valores.PRINT_SERVER_HOST = Perguntar-Campo `
        -Pergunta "Nome (ou IP) do servidor de impressao" `
        -Explicacao "E a maquina Windows que realmente gerencia as impressoras (Print Server)." `
        -Padrao "elgjunprt"

    $valores.PRINT_SERVER_TIMEOUT_SECONDS = Perguntar-Campo `
        -Pergunta "Tempo limite para responder, em segundos" `
        -Padrao "30" `
        -Validador {
            param($v)
            $n = 0
            if (-not [int]::TryParse($v, [ref]$n) -or $n -le 0) { return "Digite um numero inteiro maior que zero." }
            return $null
        }

    # --- ALLOW_MOCK_COLLECT / COLLECTION_MODE ---
    Titulo "Coleta simulada"
    Info "Em producao isso precisa ficar DESLIGADO — senao a API pode"
    Info "gravar leituras inventadas no banco como se fossem reais."
    $valores.ALLOW_MOCK_COLLECT = "false"
    $valores.COLLECTION_MODE = "real"
    Ok "ALLOW_MOCK_COLLECT = false / COLLECTION_MODE = real (fixos em producao)"

    $valores.COLLECTION_ENABLED = if (Perguntar-SimNao "Ligar a coleta automatica agendada?" $true) { "true" } else { "false" }

    $valores.COLLECTION_INTERVAL_MINUTES = Perguntar-Campo `
        -Pergunta "De quantos em quantos minutos coletar" `
        -Padrao "5" `
        -Validador {
            param($v)
            $n = 0
            if (-not [int]::TryParse($v, [ref]$n) -or $n -le 0) { return "Digite um numero inteiro maior que zero." }
            return $null
        }

    # --- TRUST_PROXY_HEADERS ---
    Titulo "Cloudflare Tunnel"
    Info "Se o backend so recebe trafego atraves do Cloudflare Tunnel (o"
    Info "caminho recomendado — a porta 8000 nunca fica exposta direto na"
    Info "internet), o backend pode confiar no cabecalho que o tunel envia"
    Info "com o IP real de quem acessou. Se voce NAO usa o tunel, deixe"
    Info "desligado."
    $valores.TRUST_PROXY_HEADERS = if (Perguntar-SimNao "O backend fica atras do Cloudflare Tunnel?" $true) { "true" } else { "false" }

    # --- WEBHOOK_URL (opcional) ---
    Titulo "Aviso automatico de toner critico (opcional)"
    Info "Se voce tem um webhook do Teams/Power Automate para avisar quando"
    Info "uma impressora fica com toner critico, cole o endereco aqui."
    Info "Pode deixar em branco e configurar depois."
    $valores.WEBHOOK_URL = Perguntar-Campo `
        -Pergunta "URL do webhook (ou Enter para pular)" `
        -PermitirVazio

    # --- Resumo final ---
    Titulo "Resumo — confira antes de gravar"
    foreach ($chave in $valores.Keys) {
        if ($chave -eq "SECRET_KEY") {
            Write-Host "  SECRET_KEY = $($valores.SECRET_KEY)" -ForegroundColor DarkYellow
        } else {
            Write-Host "  $chave = $($valores[$chave])"
        }
    }
    Write-Host ""
    Aviso "A SECRET_KEY acima e mostrada uma vez. Guarde-a em um lugar"
    Aviso "seguro (gerenciador de senhas) — se for perdida, todos os logins"
    Aviso "ativos precisarao ser refeitos."

    if (-not (Perguntar-SimNao "Gravar backend\.env com esses valores?" $true)) {
        Erro "Cancelado. Nada foi gravado."
        exit 1
    }
}

# ---------------------------------------------------------------------------
# 4. Backup do .env anterior
# ---------------------------------------------------------------------------

if (Test-Path $EnvPath) {
    $carimbo = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupPath = Join-Path $BackendDir ".env.bak-$carimbo"
    Copy-Item -Path $EnvPath -Destination $backupPath
    Ok "Backup do .env anterior salvo em: backend\.env.bak-$carimbo"
}

# ---------------------------------------------------------------------------
# 5. Gravar o novo .env
# ---------------------------------------------------------------------------

$linhas = New-Object System.Collections.Generic.List[string]
$linhas.Add("DATABASE_URL=$($valores.DATABASE_URL)")
$linhas.Add("SECRET_KEY=$($valores.SECRET_KEY)")
$linhas.Add("ALLOW_MOCK_COLLECT=$($valores.ALLOW_MOCK_COLLECT)")
$linhas.Add("ENVIRONMENT=$($valores.ENVIRONMENT)")
$linhas.Add("")
$linhas.Add("COLLECTION_ENABLED=$($valores.COLLECTION_ENABLED)")
$linhas.Add("COLLECTION_INTERVAL_MINUTES=$($valores.COLLECTION_INTERVAL_MINUTES)")
$linhas.Add("COLLECTION_MODE=$($valores.COLLECTION_MODE)")
$linhas.Add("COLLECTION_SCENARIO=$($valores.COLLECTION_SCENARIO)")
$linhas.Add("COLLECTION_MAX_WORKERS=$($valores.COLLECTION_MAX_WORKERS)")
$linhas.Add("")
$linhas.Add("PRINT_SERVER_MODE=$($valores.PRINT_SERVER_MODE)")
$linhas.Add("PRINT_SERVER_HOST=$($valores.PRINT_SERVER_HOST)")
$linhas.Add("PRINT_SERVER_TIMEOUT_SECONDS=$($valores.PRINT_SERVER_TIMEOUT_SECONDS)")
$linhas.Add("")
$linhas.Add("SNMP_COMMUNITY=$($valores.SNMP_COMMUNITY)")
$linhas.Add("SNMP_TIMEOUT=$($valores.SNMP_TIMEOUT)")
$linhas.Add("SNMP_RETRIES=$($valores.SNMP_RETRIES)")
$linhas.Add("")
$linhas.Add("WEBHOOK_URL=$($valores.WEBHOOK_URL)")
$linhas.Add("WEBHOOK_TIMEOUT_SECONDS=$($valores.WEBHOOK_TIMEOUT_SECONDS)")
$linhas.Add("")
if ($valores.CORS_ORIGINS) {
    $linhas.Add("CORS_ORIGINS=$($valores.CORS_ORIGINS)")
    $linhas.Add("")
}
$linhas.Add("LOG_LEVEL=$($valores.LOG_LEVEL)")
$linhas.Add("LOG_FILE=$($valores.LOG_FILE)")
$linhas.Add("LOG_MAX_BYTES=$($valores.LOG_MAX_BYTES)")
$linhas.Add("LOG_BACKUP_COUNT=$($valores.LOG_BACKUP_COUNT)")
$linhas.Add("")
$linhas.Add("LOGIN_MAX_ATTEMPTS=$($valores.LOGIN_MAX_ATTEMPTS)")
$linhas.Add("LOGIN_WINDOW_SECONDS=$($valores.LOGIN_WINDOW_SECONDS)")
$linhas.Add("TRUST_PROXY_HEADERS=$($valores.TRUST_PROXY_HEADERS)")

$conteudo = ($linhas -join "`n") + "`n"
$utf8SemBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($EnvPath, $conteudo, $utf8SemBom)

Ok "backend\.env gravado com sucesso."

# ---------------------------------------------------------------------------
# 6. Reiniciar o backend (opcional)
# ---------------------------------------------------------------------------

Titulo "Reiniciar o backend"
$scriptServico = Join-Path $PSScriptRoot "Servico-PrinterControl.ps1"
if (Test-Path $scriptServico) {
    if (Perguntar-SimNao "Quer reiniciar o backend agora pela tarefa agendada?" $true) {
        try {
            & $scriptServico -Acao parar
        } catch {
            Aviso "Nao foi possivel parar (talvez ja estivesse parada): $($_.Exception.Message)"
        }
        & $scriptServico -Acao iniciar
    } else {
        Info "Ok. Para reiniciar depois, rode:"
        Info "  pwsh .\scripts\Servico-PrinterControl.ps1 -Acao parar"
        Info "  pwsh .\scripts\Servico-PrinterControl.ps1 -Acao iniciar"
    }
} else {
    Aviso "scripts\Servico-PrinterControl.ps1 nao encontrado — reinicie o backend manualmente."
}

Ok "Concluido."
