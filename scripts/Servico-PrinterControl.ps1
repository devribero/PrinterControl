<#
    Servico-PrinterControl.ps1  (Fase 10)

    Sobe o backend como tarefa agendada do Windows, com inicio automatico no
    boot e reinicio automatico em caso de falha.

    POR QUE TAREFA AGENDADA, E NAO UM SERVICO WINDOWS
    --------------------------------------------------
    Um servico de verdade (services.msc) exigiria NSSM ou WinSW — download de
    binario de terceiros e direitos de administrador para instalar. A tarefa
    agendada e nativa, nao instala nada e entrega o que importa aqui: sobe no
    boot sem ninguem logado, reinicia sozinha se o processo morrer, e para/
    inicia por linha de comando. Se um dia for necessario aparecer em
    services.msc (para monitoramento corporativo que so enxerga servicos),
    o caminho e NSSM — ver docs/OPERATIONS.md.

    USO
    ----
        # instalar (uma vez, como Administrador)
        pwsh .\scripts\Servico-PrinterControl.ps1 -Acao instalar

        # dia a dia
        pwsh .\scripts\Servico-PrinterControl.ps1 -Acao status
        pwsh .\scripts\Servico-PrinterControl.ps1 -Acao parar
        pwsh .\scripts\Servico-PrinterControl.ps1 -Acao iniciar

        # remover
        pwsh .\scripts\Servico-PrinterControl.ps1 -Acao remover

    CONTA DE EXECUCAO — LEIA ANTES DE INSTALAR
    -------------------------------------------
    O padrao e SYSTEM, que sobe sem ninguem logado e nao exige senha
    guardada. MAS: a coleta real precisa de RPC/PowerShell ate o Print Server
    e SNMP ate as impressoras. Em dominio, SYSTEM se apresenta como a CONTA
    DE MAQUINA (DOMINIO\NOME-DA-MAQUINA$), que normalmente NAO tem essa
    permissao — o sintoma seria a API subir normalmente e toda coleta falhar.

    Se for esse o caso, instale com uma conta de dominio:

        pwsh .\scripts\Servico-PrinterControl.ps1 -Acao instalar -Conta "DOMINIO\usuario"

    O Windows pedira a senha e a guardara no cofre de credenciais da tarefa.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("instalar", "remover", "iniciar", "parar", "status")]
    [string]$Acao,

    # Vazio = SYSTEM. Ver "CONTA DE EXECUCAO" no cabecalho.
    [string]$Conta = "",

    [string]$NomeTarefa = "PrinterControl-Backend",
    [string]$NomeTarefaBackup = "PrinterControl-Backup",

    [int]$Porta = 8000,

    # Backups por dia. 0 desliga a tarefa de backup.
    [int]$BackupHoras = 6,
    [int]$BackupManter = 14
)

$ErrorActionPreference = "Stop"

$RaizProjeto = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$BackendDir  = Join-Path $RaizProjeto "backend"
$PythonExe   = Join-Path $BackendDir "venv\Scripts\python.exe"

function Escrever($Texto, $Cor = "Gray") { Write-Host $Texto -ForegroundColor $Cor }

function Confirmar-PreRequisitos {
    if (-not (Test-Path $PythonExe)) {
        throw "Interpretador nao encontrado: $PythonExe`nCrie o venv antes: python -m venv backend\venv"
    }
    $envFile = Join-Path $BackendDir ".env"
    if (-not (Test-Path $envFile)) {
        throw ".env nao encontrado em $envFile`nCopie de backend\.env.example e preencha antes de instalar."
    }
}

function Obter-Tarefa($Nome) {
    Get-ScheduledTask -TaskName $Nome -ErrorAction SilentlyContinue
}

function Instalar {
    Confirmar-PreRequisitos

    if (Obter-Tarefa $NomeTarefa) {
        Escrever "Tarefa '$NomeTarefa' ja existe. Removendo antes de recriar." "Yellow"
        Unregister-ScheduledTask -TaskName $NomeTarefa -Confirm:$false
    }

    # --host 127.0.0.1 de PROPOSITO: quem publica para fora e o Cloudflare
    # Tunnel (proxima fase), que roda na propria maquina. Escutar em 0.0.0.0
    # exporia a API para a rede local inteira sem nenhum controle na frente.
    $argumentos = "-m uvicorn app.main:app --host 127.0.0.1 --port $Porta"

    $acao = New-ScheduledTaskAction -Execute $PythonExe -Argument $argumentos -WorkingDirectory $BackendDir
    $gatilho = New-ScheduledTaskTrigger -AtStartup

    $config = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RestartCount 999 `
        -RestartInterval (New-TimeSpan -Minutes 1) `
        -MultipleInstances IgnoreNew `
        -ExecutionTimeLimit (New-TimeSpan -Seconds 0)

    # ExecutionTimeLimit 0 = sem limite. O padrao do Windows MATA a tarefa
    # depois de 3 dias — para um servico que deve rodar indefinidamente, isso
    # seria uma queda misteriosa toda semana.

    if ([string]::IsNullOrWhiteSpace($Conta)) {
        $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
        Register-ScheduledTask -TaskName $NomeTarefa -Action $acao -Trigger $gatilho -Settings $config -Principal $principal | Out-Null
        Escrever "Tarefa '$NomeTarefa' criada (conta SYSTEM)." "Green"
        Escrever "  ATENCAO: se a coleta real falhar, releia 'CONTA DE EXECUCAO' no cabecalho deste script." "Yellow"
    }
    else {
        Escrever "Informe a senha de $Conta (guardada pelo Windows, nao por este script):" "Cyan"
        $senha = Read-Host -AsSecureString
        $plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($senha))
        Register-ScheduledTask -TaskName $NomeTarefa -Action $acao -Trigger $gatilho -Settings $config `
            -User $Conta -Password $plain -RunLevel Highest | Out-Null
        Remove-Variable plain
        Escrever "Tarefa '$NomeTarefa' criada (conta $Conta)." "Green"
    }

    Instalar-Backup

    Escrever ""
    Escrever "Instalado. Para subir agora:" "Green"
    Escrever "  pwsh .\scripts\Servico-PrinterControl.ps1 -Acao iniciar"
}

function Instalar-Backup {
    if ($BackupHoras -le 0) {
        Escrever "Tarefa de backup NAO criada (-BackupHoras 0)." "Yellow"
        return
    }

    if (Obter-Tarefa $NomeTarefaBackup) {
        Unregister-ScheduledTask -TaskName $NomeTarefaBackup -Confirm:$false
    }

    $script = Join-Path $BackendDir "backup_db.py"
    $acao = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$script`" --keep $BackupManter" -WorkingDirectory $BackendDir

    # StartWhenAvailable cobre a maquina desligada na hora marcada: o backup
    # roda assim que ela voltar, em vez de simplesmente pular o dia.
    $gatilho = New-ScheduledTaskTrigger -Once -At (Get-Date).Date.AddHours(1) `
        -RepetitionInterval (New-TimeSpan -Hours $BackupHoras)
    $config = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 30)
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

    Register-ScheduledTask -TaskName $NomeTarefaBackup -Action $acao -Trigger $gatilho -Settings $config -Principal $principal | Out-Null
    Escrever "Tarefa '$NomeTarefaBackup' criada (a cada $BackupHoras h, mantendo $BackupManter)." "Green"
}

function Remover {
    foreach ($nome in @($NomeTarefa, $NomeTarefaBackup)) {
        if (Obter-Tarefa $nome) {
            Stop-ScheduledTask -TaskName $nome -ErrorAction SilentlyContinue
            Unregister-ScheduledTask -TaskName $nome -Confirm:$false
            Escrever "Removida: $nome" "Yellow"
        }
        else {
            Escrever "Nao existe: $nome"
        }
    }
}

function Iniciar {
    if (-not (Obter-Tarefa $NomeTarefa)) { throw "Tarefa '$NomeTarefa' nao instalada. Rode -Acao instalar." }
    Start-ScheduledTask -TaskName $NomeTarefa
    Escrever "Iniciada. Conferindo em 5s..." "Green"
    Start-Sleep -Seconds 5
    Status
}

function Parar {
    if (-not (Obter-Tarefa $NomeTarefa)) { throw "Tarefa '$NomeTarefa' nao instalada." }
    Stop-ScheduledTask -TaskName $NomeTarefa
    Escrever "Parada solicitada para '$NomeTarefa'." "Yellow"
}

function Status {
    foreach ($nome in @($NomeTarefa, $NomeTarefaBackup)) {
        $t = Obter-Tarefa $nome
        if (-not $t) { Escrever "[$nome] NAO INSTALADA" "Red"; continue }

        $info = Get-ScheduledTaskInfo -TaskName $nome
        $cor = if ($t.State -eq "Running") { "Green" } else { "Yellow" }
        Escrever "[$nome] estado=$($t.State) ultimoResultado=$($info.LastTaskResult) ultimaExecucao=$($info.LastRunTime)" $cor
    }

    # A verdade sobre "esta no ar" e a API responder, nao o Windows achar que
    # a tarefa esta rodando: o processo pode estar de pe e travado.
    try {
        $r = Invoke-RestMethod -Uri "http://127.0.0.1:$Porta/health" -TimeoutSec 5
        $cor = if ($r.status -eq "ok") { "Green" } else { "Red" }
        Escrever "[/health] status=$($r.status) ambiente=$($r.environment) banco=$($r.database) uptime=$([math]::Round($r.uptime_seconds))s scheduler=$($r.scheduler.running)" $cor
    }
    catch {
        Escrever "[/health] NAO RESPONDEU em http://127.0.0.1:$Porta — a API nao esta no ar." "Red"
    }
}

switch ($Acao) {
    "instalar" { Instalar }
    "remover"  { Remover }
    "iniciar"  { Iniciar }
    "parar"    { Parar }
    "status"   { Status }
}
