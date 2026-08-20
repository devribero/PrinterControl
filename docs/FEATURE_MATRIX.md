# Matriz de Funcionalidades

Legenda: **Funcional**, **Parcial**, **Mock**, **Simulada**, **Falsa**, **Ausente**, **Coming Soon**.

| Funcionalidade | Frontend | API | Backend | Banco/Rede | Estado | Análise |
|---|---|---|---|---|---|---|
| Login | `Login.tsx`, `auth.ts` | `POST /api/auth/login` | JWT e hash de senha | SQLite/users | Funcional | Autenticação real; token no storage do navegador |
| Dashboard | `src/app/page.tsx` | `/api/printers/with-status`, `/api/alerts`, `/api/printers/monthly-report` | Agrega resposta | SQLite | Funcional/Parcial | Fallback para dados locais |
| Busca | `PrinterTable` | Nenhuma | Filtragem no frontend | Memória do navegador | Funcional | Não é busca no banco |
| Filtros | `PrinterTable` | Nenhuma | Filtragem no frontend | Memória do navegador | Funcional | Status e tipo locais |
| Agrupamento por IP | Não exposto como tela | Não | `printer_fleet.py` | SNMP/SQLite | Funcional no backend | Deduplicação por ciclo |
| Toner | `TonerMonitoring` | `/api/printers/with-status` | SNMP e adaptação | SNMP/SQLite | Funcional/Parcial | Depende de leituras existentes |
| Uptime | Parcial | Retornado em coleta/modelo | SNMP/PrinterCollector | SNMP/SQLite | Parcial | Contrato frontend não exibe plenamente |
| Alertas | `AlertsView`, `AlertBanner` | `GET /api/alerts` | `alert_engine.py` | SQLite | Funcional na leitura | Ações não conectadas à UI |
| Webhook | Nenhuma tela | `POST /api/alerts/{id}/notify` | `webhook_notifier.py` | Rede externa opcional | Parcial | Endpoint existe, frontend não usa |
| Relatório mensal | `reports`, `MonthlyCounters` | `GET /api/printers/monthly-report` | Diferença de contadores | SQLite/JSON | Parcial | Partes do relatório são locais |
| Histórico | `history`, `HistoryMatrix` | Helper de readings não usado na tela | Leituras existem | SQLite/JSON | Parcial | Mantém fallback e dados mensais locais |
| Exportação CSV | `exportCsv.ts` | Nenhuma | Nenhum | Download local | Funcional | Exporta dados exibidos |
| Acesso Web | `window.open` | Nenhuma | Nenhum | Rede do navegador | Parcial | Depende de HTTP e rota corporativa |
| Escanear Rede | `handleDiscovery`, `DiscoveryResults.tsx` | `POST /api/servers/discover` | `print_server.py`, `discovery.py` | Windows/RPC, SNMP | Funcional | Resultado transitório em painel separado; não altera o cadastro principal |
| Descoberta Print Server | `handleDiscovery` (botão "Escanear Rede") | `POST /api/servers/discover` | `print_server.py` | Windows/RPC | Funcional | Usada pelo frontend desde a Fase 4 |
| Sincronização Print Server | Nenhum | `POST /api/servers/sync` | `printer_sync.py` | Windows/RPC/SQLite | Funcional no backend | Grava e desativa registros; ação manual |
| Coleta individual | Nenhum | `POST /api/collect/printers/{id}` | `PrinterCollector` | SNMP/SQLite | Funcional no backend | JWT; não usada na UI |
| Coleta da frota | Nenhum | `POST /api/collect/fleet` | `printer_fleet.py` | SNMP/SQLite | Funcional no backend | Rota é coleta mock e protegida por configuração |
| Scheduler | Nenhum | `GET /api/collect/scheduler` | APScheduler | SNMP/SQLite | Funcional quando habilitado | Desligado por padrão |
| Imprimir teste | Toast | Nenhuma | Nenhuma | Nenhum | Simulada | Nenhum job real é criado |
| Gerenciamento de drivers | Toast | Nenhuma | Nenhuma | Windows não acionado | Coming Soon | Não há service de driver |
| Mapeamento de impressora | Placeholder | Nenhuma | Nenhuma | Nenhuma | Coming Soon | Sem topologia ou discovery |
| Notificações | Placeholder | Nenhuma na UI | Webhook parcial | Rede externa opcional | Coming Soon/Parcial | Backend existe, tela não |
| Configurações | Placeholder | Nenhuma | Nenhuma | Nenhuma | Coming Soon | Sem persistência de preferências |
| Usuários | Placeholder | Register existe, sem UI | Auth backend | SQLite/users | Coming Soon/Parcial | Gestão de usuários não implementada |
