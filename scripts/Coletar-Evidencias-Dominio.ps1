<#
    Coletar-Evidencias-Dominio.ps1

    Coleta as evidencias do Bloco 0 (Reconhecimento) de
    docs\TESTES_MAQUINA_DOMINIO.md numa maquina do dominio.

    SOMENTE LEITURA. Este script NAO altera GPO, ACL, firewall, contas,
    registro, .env, banco de dados nem qualquer configuracao. Ele so
    consulta e grava arquivos de texto numa pasta de saida.

    Nao instala nada, nao abre porta, nao envia nada para fora da
    maquina. Toda gravacao acontece dentro da pasta -Saida.

    USO
    ----
        powershell -ExecutionPolicy Bypass -File .\scripts\Coletar-Evidencias-Dominio.ps1

        # escolhendo a pasta e o print server
        .\scripts\Coletar-Evidencias-Dominio.ps1 -Saida "D:\evid" -PrintServer "elgjunprt"

        # inclui um teste de RPC real contra o print server (leitura)
        .\scripts\Coletar-Evidencias-Dominio.ps1 -TestarPrintServer

    O QUE ELE RESPONDE
    -------------------
    GP-01 gpresult          GP-02 variaveis de ambiente
    AD-01 identidade        AD-05 relogio vs DC
    IF-05 disco do banco    SE-02 firewall e perfil de rede
    RE-01 DNS do servidor   GP-04 ExecutionPolicy e logging
    GP-05 UAC               GP-06 redirecionamento de pastas
    SE-01 segredo em Main.ps1 (so confirma presenca, nunca imprime o valor)

    Com -TestarPrintServer, tambem:
    SE-06 stdout puro do PowerShell   SV-01/SV-02 Get-Printer/Get-PrinterPort
    AD-04 Kerberos vs NTLM (klist)

    Ao final, gera RESUMO.txt com um veredito por item.
#>

[CmdletBinding()]
param(
    [string]$Saida = "",

    # Host do print server. Vazio = tenta ler PRINT_SERVER_HOST do backend\.env,
    # e cai em "elgjunprt" (o default historico de config.py) se nao achar.
    [string]$PrintServer = "",

    # Dispara Get-Printer/Get-PrinterPort contra o print server. E leitura,
    # mas toca a rede e o servidor - por isso e opt-in.
    [switch]$TestarPrintServer
)

$ErrorActionPreference = "Continue"
$ProgressPreference    = "SilentlyContinue"

# ---------------------------------------------------------------------------
#  Preparacao
# ---------------------------------------------------------------------------

$RaizProjeto = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if ([string]::IsNullOrWhiteSpace($Saida)) {
    $carimbo = Get-Date -Format "yyyyMMdd-HHmm"
    $Saida = Join-Path ([Environment]::GetFolderPath('Desktop')) "evidencias-printercontrol-$carimbo"
}
if (-not (Test-Path $Saida)) { New-Item -ItemType Directory -Path $Saida -Force | Out-Null }

$Veredito = [System.Collections.Generic.List[string]]::new()

function Passo {
    param([string]$Id, [string]$Titulo, [string]$Arquivo, [scriptblock]$Bloco)

    Write-Host ("  {0,-7} {1}" -f $Id, $Titulo) -ForegroundColor Gray
    $destino = Join-Path $Saida $Arquivo
    try {
        $conteudo = & $Bloco 2>&1 | Out-String
        Set-Content -LiteralPath $destino -Value $conteudo -Encoding UTF8
        return $conteudo
    }
    catch {
        $msg = "ERRO ao coletar: $($_.Exception.Message)"
        Set-Content -LiteralPath $destino -Value $msg -Encoding UTF8
        Write-Host "          $msg" -ForegroundColor Red
        return $msg
    }
}

function Registrar {
    param([string]$Id, [string]$Situacao, [string]$Detalhe)
    $Veredito.Add(("{0,-7} {1,-10} {2}" -f $Id, $Situacao, $Detalhe))
}

Write-Host ""
Write-Host "=== Coleta de evidencias - maquina do dominio ===" -ForegroundColor Cyan
Write-Host "Somente leitura. Nada e alterado nesta maquina." -ForegroundColor DarkGray
Write-Host "Saida: $Saida"
Write-Host ""

# ---------------------------------------------------------------------------
#  Descobrir o print server configurado (leitura do .env, sem alterar)
# ---------------------------------------------------------------------------

if ([string]::IsNullOrWhiteSpace($PrintServer)) {
    $envPath = Join-Path $RaizProjeto "backend\.env"
    if (Test-Path $envPath) {
        $linha = Select-String -Path $envPath -Pattern '^\s*PRINT_SERVER_HOST\s*=\s*(.+)\s*$' |
                 Select-Object -First 1
        if ($linha) { $PrintServer = $linha.Matches[0].Groups[1].Value.Trim().Trim('"') }
    }
}
if ([string]::IsNullOrWhiteSpace($PrintServer)) { $PrintServer = "elgjunprt" }
Write-Host "Print server considerado: $PrintServer" -ForegroundColor DarkGray
Write-Host ""

# ---------------------------------------------------------------------------
#  AD-01 - identidade
# ---------------------------------------------------------------------------

Write-Host "Identidade e dominio" -ForegroundColor White
$identidade = Passo "AD-01" "Identidade do usuario e grupos" "AD-01-identidade.txt" {
    "=== whoami ==============================================="
    whoami
    ""
    "=== whoami /fqdn ========================================="
    whoami /fqdn
    ""
    "=== whoami /groups ======================================="
    whoami /groups
    ""
    "=== WindowsIdentity ======================================"
    [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    ""
    "=== Variaveis de identidade =============================="
    "COMPUTERNAME  = $env:COMPUTERNAME"
    "USERDOMAIN    = $env:USERDOMAIN"
    "USERDNSDOMAIN = $env:USERDNSDOMAIN"
    "LOGONSERVER   = $env:LOGONSERVER"
    "USERNAME      = $env:USERNAME"
    ""
    "=== Maquina ingressada no dominio? ======================="
    try {
        $cs = Get-CimInstance Win32_ComputerSystem
        "PartOfDomain = $($cs.PartOfDomain)"
        "Domain       = $($cs.Domain)"
        "Workgroup    = $($cs.Workgroup)"
    } catch { "Nao foi possivel consultar Win32_ComputerSystem: $($_.Exception.Message)" }
    ""
    "=== Administrador local? ================================="
    $ehAdmin = ([Security.Principal.WindowsPrincipal] `
        [Security.Principal.WindowsIdentity]::GetCurrent()
    ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    "Sessao elevada = $ehAdmin"
}

if ($identidade -match 'PartOfDomain\s*=\s*True') {
    Registrar "AD-01" "OK" "Maquina ingressada no dominio."
} else {
    Registrar "AD-01" "ATENCAO" "Maquina NAO parece estar no dominio - o resto da bateria perde o sentido."
}

# ---------------------------------------------------------------------------
#  AD-05 - relogio (deriva > 5 min derruba Kerberos e, com ele, todo o Bloco 1)
# ---------------------------------------------------------------------------

$tempo = Passo "AD-05" "Sincronizacao de relogio contra o DC" "AD-05-tempo.txt" {
    "=== w32tm /query /status ================================="
    w32tm /query /status
    ""
    "=== w32tm /query /source ================================="
    w32tm /query /source
    ""
    "=== Relogio local ========================================"
    "Local (Get-Date) = $(Get-Date -Format 'o')"
    "UTC              = $([datetime]::UtcNow.ToString('o'))"
    "Fuso             = $((Get-TimeZone).Id) / $((Get-TimeZone).DisplayName)"
}

if ($tempo -match 'Phase Offset:\s*([-0-9\.]+)s') {
    $offset = [double]$Matches[1]
    if ([math]::Abs($offset) -lt 300) {
        Registrar "AD-05" "OK" ("Deriva de {0:N3}s - dentro dos 5 min do Kerberos." -f $offset)
    } else {
        Registrar "AD-05" "FALHA" ("Deriva de {0:N1}s - acima de 5 min. Kerberos vai recusar; o Bloco 1 dara falso negativo." -f $offset)
    }
} else {
    Registrar "AD-05" "VERIFICAR" "Nao consegui ler o Phase Offset - confira AD-05-tempo.txt a mao."
}

# ---------------------------------------------------------------------------
#  GP-01 - gpresult
# ---------------------------------------------------------------------------

Write-Host "Politicas de dominio" -ForegroundColor White
$gpoHtml = Join-Path $Saida "GP-01-gpo.html"
Write-Host "  GP-01   Relatorio de politicas aplicadas (pode demorar ~30s)" -ForegroundColor Gray
try {
    gpresult /h $gpoHtml /f 2>&1 | Out-Null
    if (Test-Path $gpoHtml) {
        Registrar "GP-01" "OK" "GP-01-gpo.html gerado. Leia as secoes Impressoras, PowerShell e Variaveis de ambiente."
    } else {
        Registrar "GP-01" "FALHA" "gpresult nao gerou o arquivo."
    }
} catch {
    Registrar "GP-01" "FALHA" "gpresult falhou: $($_.Exception.Message)"
}

# ---------------------------------------------------------------------------
#  GP-02 - variaveis de ambiente que colidem com chaves do Settings
# ---------------------------------------------------------------------------

$chaves = @(
    'DATABASE_URL','SECRET_KEY','ENVIRONMENT','ALGORITHM','API_PREFIX',
    'PRINT_SERVER_MODE','PRINT_SERVER_HOST','PRINT_SERVER_TIMEOUT_SECONDS',
    'COLLECTION_ENABLED','COLLECTION_INTERVAL_MINUTES','COLLECTION_MODE',
    'COLLECTION_SCENARIO','COLLECTION_MAX_WORKERS','COLLECTION_PRINTER_IDS',
    'SNMP_COMMUNITY','SNMP_TIMEOUT','SNMP_RETRIES','ALLOW_MOCK_COLLECT',
    'WEBHOOK_URL','WEBHOOK_TIMEOUT_SECONDS','CORS_ORIGINS',
    'TRUST_PROXY_HEADERS','TRUSTED_PROXY_IPS','ACCESS_TOKEN_EXPIRE_HOURS',
    'LOGIN_MAX_ATTEMPTS','LOGIN_WINDOW_SECONDS','LOG_LEVEL','LOG_FILE',
    'HTTP_PROXY','HTTPS_PROXY','NO_PROXY','SSL_CERT_FILE','REQUESTS_CA_BUNDLE'
)

$colisoes = @()
$ambiente = Passo "GP-02" "Variaveis de ambiente (Usuario, Maquina, Processo)" "GP-02-ambiente.txt" {
    "=== Colisoes com chaves de backend/app/config.py ========="
    "(o Pydantic da PRECEDENCIA ao ambiente sobre o .env - uma variavel"
    " aqui muda o comportamento do backend sem nada mudar no repositorio)"
    ""
    foreach ($escopo in @('Machine','User','Process')) {
        $vars = [Environment]::GetEnvironmentVariables($escopo)
        foreach ($k in $chaves) {
            if ($vars.Contains($k)) {
                $valor = if ($k -match 'SECRET|WEBHOOK|PASSWORD') { '<omitido>' } else { $vars[$k] }
                "COLISAO [$escopo] $k = $valor"
                $script:colisoes += "[$escopo] $k"
            }
        }
    }
    if ($script:colisoes.Count -eq 0) { "Nenhuma colisao encontrada." }
    ""
    "=== Ambiente de MAQUINA (o que o SYSTEM enxerga) ========="
    [Environment]::GetEnvironmentVariables('Machine').GetEnumerator() |
        Sort-Object Name | Format-Table -AutoSize | Out-String
    ""
    "=== Ambiente de USUARIO =================================="
    [Environment]::GetEnvironmentVariables('User').GetEnumerator() |
        Sort-Object Name | Format-Table -AutoSize | Out-String
    ""
    "=== Proxy de nivel de maquina (o que o SYSTEM usa) ======="
    netsh winhttp show proxy
}

if ($colisoes.Count -eq 0) {
    Registrar "GP-02" "OK" "Nenhuma variavel de ambiente colide com chave do backend."
} else {
    Registrar "GP-02" "FALHA" ("{0} colisao(oes): {1}. Resolva ANTES do resto - todo teste seguinte mediria a configuracao errada." -f $colisoes.Count, ($colisoes -join ', '))
}

# ---------------------------------------------------------------------------
#  GP-04 - ExecutionPolicy e logging de script
# ---------------------------------------------------------------------------

$psPolicy = Passo "GP-04" "ExecutionPolicy e logging de script" "GP-04-powershell.txt" {
    "=== Get-ExecutionPolicy -List ============================"
    Get-ExecutionPolicy -List | Format-Table -AutoSize | Out-String
    ""
    "=== Politicas de PowerShell no registro =================="
    foreach ($p in @(
        "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell",
        "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging",
        "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription",
        "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging"
    )) {
        "--- $p"
        if (Test-Path $p) {
            Get-ItemProperty $p | Format-List | Out-String
        } else { "  (nao definida)"; "" }
    }
    "=== Versao do PowerShell ================================="
    $PSVersionTable | Format-List | Out-String
}

if ($psPolicy -match 'EnableScriptBlockLogging\s*:\s*1' -or $psPolicy -match 'EnableTranscripting\s*:\s*1') {
    Registrar "GP-04" "ATENCAO" "Logging/transcricao de script LIGADO - pode poluir o stdout que o backend parseia como JSON (SE-06)."
} else {
    Registrar "GP-04" "OK" "Sem logging/transcricao de script que polua o stdout."
}

# ---------------------------------------------------------------------------
#  GP-05 - UAC
# ---------------------------------------------------------------------------

Passo "GP-05" "Configuracao de UAC" "GP-05-uac.txt" {
    "=== Politicas de UAC ====================================="
    Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" |
        Select-Object EnableLUA, ConsentPromptBehaviorAdmin, ConsentPromptBehaviorUser,
                      FilterAdministratorToken, PromptOnSecureDesktop |
        Format-List | Out-String
    ""
    "=== Administradores locais ==============================="
    try { net localgroup Administradores } catch { }
    try { net localgroup Administrators } catch { }
} | Out-Null
Registrar "GP-05" "COLETADO" "Ver GP-05-uac.txt (correlacionar com IM-01/IM-03)."

# ---------------------------------------------------------------------------
#  GP-06 / IF-05 - pastas redirecionadas e disco do banco
# ---------------------------------------------------------------------------

Write-Host "Disco, perfil e banco" -ForegroundColor White
$dbLocal = $true
$disco = Passo "IF-05" "Local do banco e redirecionamento de pastas" "IF-05-disco.txt" {
    "=== Pastas do perfil ====================================="
    "Desktop     = $([Environment]::GetFolderPath('Desktop'))"
    "MyDocuments = $([Environment]::GetFolderPath('MyDocuments'))"
    ""
    "=== User Shell Folders (redirecionamento por GPO) ========"
    Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" -EA SilentlyContinue |
        Format-List | Out-String
    ""
    "=== Raiz do projeto ======================================"
    "Projeto = $script:RaizProjeto"
    ""
    "=== Banco de dados ======================================="
    $db = Join-Path $script:RaizProjeto "backend\printer_control.db"
    if (Test-Path $db) {
        $item = Get-Item $db
        "Caminho  = $($item.FullName)"
        "Tamanho  = $([math]::Round($item.Length/1MB,2)) MB"
        "Alterado = $($item.LastWriteTime)"
        try {
            $vol = Get-Volume -FilePath $item.FullName -ErrorAction Stop
            "Volume     = $($vol.DriveLetter)"
            "DriveType  = $($vol.DriveType)"
            "FileSystem = $($vol.FileSystem)"
            if ($vol.DriveType -ne 'Fixed') { $script:dbLocal = $false }
        } catch { "Nao foi possivel resolver o volume: $($_.Exception.Message)" }
    } else {
        "Banco nao encontrado em $db"
    }
    ""
    "=== O caminho e UNC? ====================================="
    if ($script:RaizProjeto.StartsWith("\\")) {
        "SIM - o projeto esta num caminho de rede. SQLite sobre SMB corrompe."
        $script:dbLocal = $false
    } else { "Nao - caminho local." }
}

if ($dbLocal) {
    Registrar "IF-05" "OK" "Banco em disco local fixo."
} else {
    Registrar "IF-05" "FALHA" "Banco NAO esta em disco local fixo. SQLite sobre SMB corrompe - nao siga sem resolver."
}

if ($disco -match 'Desktop\s*=\s*\\\\') {
    Registrar "GP-06" "ATENCAO" "Desktop redirecionado para caminho de rede."
} else {
    Registrar "GP-06" "OK" "Desktop nao redirecionado para rede."
}

# ---------------------------------------------------------------------------
#  SE-02 - firewall e perfil de rede
# ---------------------------------------------------------------------------

Write-Host "Rede e firewall" -ForegroundColor White
$fw = Passo "SE-02" "Perfis de firewall e conexao" "SE-02-firewall.txt" {
    "=== Perfis de firewall ==================================="
    Get-NetFirewallProfile |
        Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction |
        Format-Table -AutoSize | Out-String
    ""
    "=== Perfil da conexao ativa =============================="
    Get-NetConnectionProfile | Format-List | Out-String
    ""
    "=== Regras relevantes (loja ativa) ======================="
    Get-NetFirewallRule -PolicyStore ActiveStore -ErrorAction SilentlyContinue |
        Where-Object { $_.DisplayName -match 'Print|SNMP|ICMP|Python|Node|3000|8000' } |
        Select-Object DisplayName, Direction, Action, Enabled, Profile |
        Format-Table -AutoSize | Out-String
}

if ($fw -match 'DomainAuthenticated') {
    Registrar "SE-02" "OK" "Conexao no perfil DomainAuthenticated."
} else {
    Registrar "SE-02" "ATENCAO" "Conexao ativa NAO esta no perfil de dominio - as regras testadas podem nao ser as de producao."
}

# ---------------------------------------------------------------------------
#  RE-01 - DNS do print server
# ---------------------------------------------------------------------------

$resolveuCurto = $false
$dns = Passo "RE-01" "Resolucao de nome do print server ($PrintServer)" "RE-01-dns.txt" {
    "=== Servidores DNS configurados =========================="
    Get-DnsClientServerAddress -AddressFamily IPv4 |
        Select-Object InterfaceAlias, ServerAddresses |
        Format-Table -AutoSize | Out-String
    ""
    "=== Sufixo de busca (RE-02) =============================="
    Get-DnsClientGlobalSetting | Format-List | Out-String
    ""
    "=== Nome curto: $script:PrintServer ======================"
    try {
        Resolve-DnsName $script:PrintServer -ErrorAction Stop | Format-Table -AutoSize | Out-String
        $script:resolveuCurto = $true
    } catch { "FALHOU: $($_.Exception.Message)" }
    ""
    "=== FQDN (sufixo do dominio) ============================="
    if ($env:USERDNSDOMAIN) {
        $fqdn = "$script:PrintServer.$env:USERDNSDOMAIN"
        "Tentando $fqdn"
        try { Resolve-DnsName $fqdn -ErrorAction Stop | Format-Table -AutoSize | Out-String }
        catch { "FALHOU: $($_.Exception.Message)" }
    } else { "USERDNSDOMAIN vazio - sem FQDN para tentar." }
    ""
    "=== TCP/135 (RPC endpoint mapper) - RE-05 ================"
    try {
        Test-NetConnection $script:PrintServer -Port 135 -WarningAction SilentlyContinue |
            Select-Object ComputerName, RemoteAddress, TcpTestSucceeded, PingSucceeded |
            Format-List | Out-String
    } catch { "FALHOU: $($_.Exception.Message)" }
}

if ($resolveuCurto) {
    Registrar "RE-01" "OK" "Nome curto '$PrintServer' resolve."
} else {
    Registrar "RE-01" "FALHA" "Nome curto '$PrintServer' NAO resolve - sufixo de busca DNS ou nome errado."
}
if ($dns -match 'TcpTestSucceeded\s*:\s*True') {
    Registrar "RE-05" "OK" "TCP/135 alcancavel no print server."
} else {
    Registrar "RE-05" "FALHA" "TCP/135 NAO alcancavel - o RPC do Get-Printer nao vai funcionar."
}

# ---------------------------------------------------------------------------
#  SE-01 - segredo versionado (confirma presenca; NUNCA imprime o valor)
# ---------------------------------------------------------------------------

Write-Host "Seguranca" -ForegroundColor White
$mainPs1 = Join-Path $RaizProjeto "Main.ps1"
$temSegredo = $false
Passo "SE-01" "Segredo do webhook versionado em Main.ps1" "SE-01-segredo.txt" {
    "=== Presenca de assinatura de webhook em Main.ps1 ========"
    "(o VALOR nunca e gravado aqui - so a linha e o comprimento)"
    ""
    if (Test-Path $script:mainPs1) {
        $achados = Select-String -Path $script:mainPs1 -Pattern 'sig=' -AllMatches
        if ($achados) {
            $script:temSegredo = $true
            foreach ($a in $achados) {
                "ACHADO na linha $($a.LineNumber) - comprimento da linha: $($a.Line.Length) caracteres"
            }
        } else { "Nenhuma ocorrencia de 'sig=' encontrada." }
    } else { "Main.ps1 nao encontrado em $script:mainPs1" }
    ""
    "=== Quem consegue ler a pasta do projeto ================="
    try {
        (Get-Acl $script:RaizProjeto).Access |
            Select-Object IdentityReference, FileSystemRights, AccessControlType |
            Format-Table -AutoSize | Out-String
    } catch { "Nao foi possivel ler a ACL: $($_.Exception.Message)" }
    ""
    "=== ACL do backend\.env =================================="
    $envFile = Join-Path $script:RaizProjeto "backend\.env"
    if (Test-Path $envFile) {
        try {
            (Get-Acl $envFile).Access |
                Select-Object IdentityReference, FileSystemRights, AccessControlType |
                Format-Table -AutoSize | Out-String
        } catch { "Nao foi possivel ler a ACL: $($_.Exception.Message)" }
    } else { ".env nao encontrado." }
} | Out-Null

if ($temSegredo) {
    Registrar "SE-01" "FALHA" "Assinatura de webhook presente em Main.ps1 (achado A-01). Reporte AGORA, sem esperar o fim da bateria."
} else {
    Registrar "SE-01" "OK" "Nenhuma assinatura de webhook encontrada em Main.ps1."
}

# ---------------------------------------------------------------------------
#  Print server (opt-in) - SE-06, SV-01, SV-02, AD-04
# ---------------------------------------------------------------------------

if ($TestarPrintServer) {
    Write-Host "Print server (RPC - leitura)" -ForegroundColor White

    $jsonPuro = $false
    $qtdFilas = -1

    $rpc = Passo "SV-01" "Get-Printer / Get-PrinterPort via RPC" "SV-01-printserver.txt" {
        $cmdP = "Get-Printer -ComputerName '$script:PrintServer' -ErrorAction Stop | Select-Object Name,DriverName,PortName | ConvertTo-Json -Compress"
        $cmdQ = "Get-PrinterPort -ComputerName '$script:PrintServer' -ErrorAction Stop | Select-Object Name,PrinterHostAddress | ConvertTo-Json -Compress"

        "=== SE-06: o stdout e JSON PURO? ========================="
        "(mesma invocacao de backend/app/services/print_server.py:159)"
        ""
        $saida = & powershell.exe -NoProfile -NonInteractive -Command $cmdP 2>&1 | Out-String
        $saida = $saida.Trim()
        "Primeiros 200 caracteres do stdout:"
        if ($saida.Length -gt 200) { $saida.Substring(0,200) } else { $saida }
        ""
        try {
            $obj = $saida | ConvertFrom-Json -ErrorAction Stop
            $script:jsonPuro = $true
            $script:qtdFilas = @($obj).Count
            "ConvertFrom-Json: OK - $($script:qtdFilas) filas."
        } catch {
            "ConvertFrom-Json: FALHOU - $($_.Exception.Message)"
            "  => stdout poluido (banner, BOM ou transcricao por GPO), ou erro de RPC."
        }
        ""
        "=== SV-01: contagem pelo cmdlet direto ==================="
        try {
            $direto = @(Get-Printer -ComputerName $script:PrintServer -ErrorAction Stop)
            "Get-Printer direto: $($direto.Count) filas"
            $direto | Select-Object Name, DriverName, PortName |
                Sort-Object Name | Format-Table -AutoSize | Out-String
        } catch { "FALHOU: $($_.Exception.Message)" }
        ""
        "=== SV-02: Get-PrinterPort =============================="
        try {
            $portas = @(Get-PrinterPort -ComputerName $script:PrintServer -ErrorAction Stop)
            "Portas: $($portas.Count)"
            $portas | Select-Object Name, PrinterHostAddress |
                Sort-Object Name | Format-Table -AutoSize | Out-String
        } catch { "FALHOU: $($_.Exception.Message)" }
    }

    if ($jsonPuro) {
        Registrar "SE-06" "OK" "stdout do PowerShell e JSON puro - o parse do backend vai funcionar."
    } else {
        Registrar "SE-06" "FALHA" "stdout NAO parseia como JSON. O backend vai reportar 'Saida do PowerShell nao e JSON valido' e o erro aponta para o lugar errado."
    }

    if ($qtdFilas -gt 0) {
        Registrar "SV-01" "OK" "$qtdFilas filas enumeradas. Compare com o count da API antes de qualquer sync (PORTAO PE-05)."
    } elseif ($rpc -match 'Access is denied|Acesso negado') {
        Registrar "SV-01" "FALHA" "Acesso negado no RPC - e o cenario D-01 (identidade do processo)."
    } else {
        Registrar "SV-01" "VERIFICAR" "Nao consegui contar as filas - leia SV-01-printserver.txt."
    }

    Passo "AD-04" "Tickets Kerberos apos o RPC" "AD-04-kerberos.txt" {
        "=== klist (tickets da sessao apos o Get-Printer) ========="
        klist
        ""
        "Um ticket host/$script:PrintServer ou cifs/$script:PrintServer prova Kerberos."
        "Ausencia sugere NTLM - relevante se o dominio restringir NTLM."
    } | Out-Null
    Registrar "AD-04" "COLETADO" "Ver AD-04-kerberos.txt."
}
else {
    Registrar "SV-01" "PULADO" "Rode de novo com -TestarPrintServer para exercitar o RPC."
    Registrar "SE-06" "PULADO" "Depende de -TestarPrintServer."
}

# ---------------------------------------------------------------------------
#  Estado do sistema, se estiver no ar
# ---------------------------------------------------------------------------

Write-Host "Estado do sistema" -ForegroundColor White
Passo "IF-04" "Tarefas agendadas e /health" "IF-04-sistema.txt" {
    "=== Tarefas agendadas do PrinterControl =================="
    $tarefas = Get-ScheduledTask -TaskName "PrinterControl-*" -ErrorAction SilentlyContinue
    if ($tarefas) {
        foreach ($t in $tarefas) {
            "--- $($t.TaskName)"
            "Estado    = $($t.State)"
            "UserId    = $($t.Principal.UserId)"
            "LogonType = $($t.Principal.LogonType)"
            "RunLevel  = $($t.Principal.RunLevel)"
            try {
                $info = Get-ScheduledTaskInfo -TaskName $t.TaskName
                "UltimaExecucao  = $($info.LastRunTime)"
                "UltimoResultado = $($info.LastTaskResult)"
                "ProximaExecucao = $($info.NextRunTime)"
            } catch { }
            ""
        }
    } else { "Nenhuma tarefa PrinterControl-* instalada." }
    ""
    "=== /health =============================================="
    try {
        $h = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 5
        $h | ConvertTo-Json -Depth 5
    } catch { "A API nao respondeu em http://127.0.0.1:8000/health - $($_.Exception.Message)" }
    ""
    "=== Processos python/node ================================"
    Get-Process python, node -ErrorAction SilentlyContinue |
        Select-Object Id, ProcessName, StartTime, WorkingSet |
        Format-Table -AutoSize | Out-String
} | Out-Null
Registrar "IF-04" "COLETADO" "Ver IF-04-sistema.txt (conta da tarefa e /health)."

# copia do log, se existir
$log = Join-Path $RaizProjeto "backend\logs\printercontrol.log"
if (Test-Path $log) {
    Copy-Item $log (Join-Path $Saida "printercontrol.log") -ErrorAction SilentlyContinue
}

# ---------------------------------------------------------------------------
#  Resumo
# ---------------------------------------------------------------------------

$resumo = @()
$resumo += "RESUMO DA COLETA - Bloco 0 (Reconhecimento)"
$resumo += "PrinterControl / bateria de testes em maquina do dominio"
$resumo += ""
$resumo += "Data           : $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')"
$resumo += "Maquina        : $env:COMPUTERNAME"
$resumo += "Dominio        : $env:USERDOMAIN"
$resumo += "Conta          : $env:USERNAME"
$resumo += "Print server   : $PrintServer"
$resumo += "RPC exercitado : $($TestarPrintServer.IsPresent)"
$resumo += ""
$resumo += "Este script e SOMENTE LEITURA. Nada foi alterado nesta maquina."
$resumo += ""
$resumo += "VEREDITO POR ITEM"
$resumo += "-----------------"
$resumo += $Veredito
$resumo += ""
$resumo += "PORTAO DO BLOCO 0"
$resumo += "-----------------"

$bloqueios = @($Veredito | Where-Object { $_ -match '\bFALHA\b' })
if ($bloqueios.Count -eq 0) {
    $resumo += "Nenhuma FALHA. Pode seguir para o Bloco 1 (caminho critico do dominio)."
} else {
    $resumo += "$($bloqueios.Count) FALHA(S) - NAO avance para o Bloco 1 sem resolver:"
    $resumo += $bloqueios
    $resumo += ""
    $resumo += "Motivo: cada uma destas faz os blocos seguintes falharem por causa errada."
}
$resumo += ""
$resumo += "Proximo passo: docs\TESTES_MAQUINA_DOMINIO.md, secao 5, Bloco 1."

$resumoTxt = $resumo -join "`r`n"
Set-Content -LiteralPath (Join-Path $Saida "RESUMO.txt") -Value $resumoTxt -Encoding UTF8

Write-Host ""
Write-Host "=== RESUMO ===" -ForegroundColor Cyan
foreach ($linha in $Veredito) {
    $cor = switch -Regex ($linha) {
        '\bFALHA\b'    { "Red" }
        '\bATENCAO\b'  { "Yellow" }
        '\bOK\b'       { "Green" }
        default        { "Gray" }
    }
    Write-Host "  $linha" -ForegroundColor $cor
}
Write-Host ""
if ($bloqueios.Count -eq 0) {
    Write-Host "Bloco 0 liberado - pode seguir para o Bloco 1." -ForegroundColor Green
} else {
    Write-Host "$($bloqueios.Count) FALHA(S) - nao avance para o Bloco 1 sem resolver." -ForegroundColor Red
}
Write-Host ""
Write-Host "Evidencias em: $Saida" -ForegroundColor Cyan
Write-Host ""

# Codigo de saida: 0 = bloco 0 liberado, 1 = ha FALHA bloqueando o bloco 1.
# Deixa o script encadeavel sem que alguem precise ler o resumo a olho.
if ($bloqueios.Count -eq 0) { exit 0 } else { exit 1 }
