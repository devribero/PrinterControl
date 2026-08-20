# Graph Report - PrinterControl  (2026-08-18)

## Corpus Check
- 101 files · ~42,919 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 688 nodes · 1361 edges · 38 communities (29 shown, 9 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 52 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `df944eb9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- snmp_fleet_mock.py
- package.json
- .collect
- Elgin Impressoras (painel de monitoramento)
- TonerInfo
- Coletar-Impressoras.ps1
- compilerOptions
- collect.py
- useAppData
- ComingSoon.tsx
- plugins
- HistoryMatrix.tsx
- graphify (knowledge graph tool)
- next.config.ts
- Elgin (Brand)
- PrinterControl Favicon Icon
- npm run build
- npm run dev
- next-env.d.ts
- navIds.ts
- SNMPResult
- PrinterCollector
- tests_collect_api.py
- Simular-Ambiente.ps1
- Login.tsx
- app-data.tsx
- Modo Simulado
- services
- printers.py
- snmp.py
- SNMPClient
- cn
- Settings

## God Nodes (most connected - your core abstractions)
1. `SNMPClient` - 32 edges
2. `cn()` - 31 edges
3. `Printer` - 26 edges
4. `PrinterCollector` - 24 edges
5. `SNMPResult` - 23 edges
6. `useAppData()` - 21 edges
7. `Printer` - 20 edges
8. `Elgin Impressoras (painel de monitoramento)` - 20 edges
9. `compilerOptions` - 19 edges
10. `useToast()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `Lucide` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md
- `React` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md
- `Recharts` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md
- `Tailwind CSS v4` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md
- `TypeScript` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Comandos do CLI graphify (query/path/explain/update)** — claude_graphify, claude_graphify_query, claude_graphify_path, claude_graphify_explain, claude_graphify_update [EXTRACTED 1.00]
- **Stack tecnológico do painel (Vite/React/TS/Tailwind/Recharts/Lucide)** — readme_vite, readme_react, readme_typescript, readme_tailwind_css_v4, readme_recharts, readme_lucide [EXTRACTED 1.00]
- **Arquitetura de dados de 3 modos (Demo/Real/Simulado)** — contexto_desenvolvimento_elgin_impressoras, contexto_desenvolvimento_modo_demo, contexto_desenvolvimento_modo_real, contexto_desenvolvimento_modo_simulado [EXTRACTED 1.00]

## Communities (38 total, 9 thin omitted)

### Community 0 - "snmp_fleet_mock.py"
Cohesion: 0.23
Nodes (10): _base_page_count(), _increment(), profile_for(), Simulador de frota — APENAS PARA TESTE LOCAL. Diferenca para snmp_mock.py: la…, Perfil deterministico da impressora: online | offline | snmp_mudo | baixo |…, Contador inicial plausivel para uma impressora que nunca foi lida., Paginas impressas entre duas coletas — fixo por impressora, 5 a 124., Nivel do toner: base do perfil + desvio deterministico por impressora/cor,… (+2 more)

### Community 1 - "package.json"
Cohesion: 0.06
Nodes (31): lucide-react, next, oxlint, dependencies, lucide-react, next, react, react-dom (+23 more)

### Community 2 - ".collect"
Cohesion: 0.20
Nodes (5): Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta., ICMP ping, equivalente ao `New-Object ...Ping).Send($ip, 400)` do PS1. SNMP…, Escolhe os toners finais. PS1 colorida: um por cor (primeiro de cada grupo),…, Ticks de 1/100s -> 'Xd, Yh, Zm' (mesmo formato do PS1).

### Community 3 - "Elgin Impressoras (painel de monitoramento)"
Cohesion: 0.10
Nodes (21): Tela Alertas, Tela Dashboard, Elgin Impressoras (painel de monitoramento), Tela Histórico, Tela Impressoras, Tela Login, Migração futura para FastAPI (Python) + Next.js + banco de dados, Modo claro/escuro (toggle) (+13 more)

### Community 4 - "TonerInfo"
Cohesion: 0.18
Nodes (11): Decodifica bytes BER como inteiro sem sinal., Retorna (candidatos, houve_resposta_snmp)., GETBULK das tres colunas de uma vez (PS1: Build-SnmpGetBulk)., Fallback: um GET por indice (PS1: laco 1..20 com 3 falhas seguidas)., Aplica os filtros do PS1 e monta um candidato a toner., GET de um valor numerico (INTEGER, Counter32, Gauge32, TimeTicks)., Envia um pacote e aguarda a resposta (UDP/161)., Nivel de um consumivel de toner. (+3 more)

### Community 5 - "Coletar-Impressoras.ps1"
Cohesion: 0.21
Nodes (13): Build-SnmpGet(), Build-SnmpGetBulk(), Convert-SnmpValueBytes(), Get-ImpressorasServidor(), Get-TonerSNMP(), Parse-SnmpBulkResponse(), Parse-SnmpCounter(), Parse-SnmpInt() (+5 more)

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): dom, dom.iterable, esnext, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+22 more)

### Community 7 - "collect.py"
Cohesion: 0.06
Nodes (58): AsyncIOScheduler, create_db_and_tables(), get_session(), _migrate_alert_type(), Adiciona alerts.alert_type em bancos criados antes da Etapa 8A., health_check(), lifespan(), get (+50 more)

### Community 8 - "useAppData"
Cohesion: 0.08
Nodes (29): react, ibmPlexMono, metadata, publicSans, sourceSerif, PrintersPage(), Providers(), ReportsPage() (+21 more)

### Community 10 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 11 - "HistoryMatrix.tsx"
Cohesion: 0.27
Nodes (5): HistoryPage(), HistoryMatrix(), HistoryMatrixProps, getDepartmentLabel(), getPrinterSite()

### Community 12 - "graphify (knowledge graph tool)"
Cohesion: 0.25
Nodes (8): graphify (knowledge graph tool), graphify explain command, graphify path command, graphify query command, graphify update command, graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/wiki/index.md

### Community 20 - "SNMPResult"
Cohesion: 0.13
Nodes (15): MockSNMPScenarios, Agente SNMP simulado — APENAS PARA TESTE LOCAL. Existe porque a maquina de…, SNMP responde o contador, mas nao expoe a tabela de consumiveis., Monocromatica com toner em 5%., Colorida com ciano critico (18%) e os demais normais., Contador reiniciado (troca de placa/formatador): page_count baixo., Cenarios de teste. Cada metodo devolve um SNMPResult completo., Monocromatica saudavel. (+7 more)

### Community 21 - "PrinterCollector"
Cohesion: 0.07
Nodes (38): Alert, Alert, SQLModel, TonerHistory, Printer, PrinterMonthly, PrinterReading, SQLModel (+30 more)

### Community 22 - "tests_collect_api.py"
Cohesion: 0.67
Nodes (3): check(), main(), Teste ponta a ponta dos endpoints /api/collect com os cenarios simulados.…

### Community 28 - "Simular-Ambiente.ps1"
Cohesion: 0.16
Nodes (6): Modo Real, Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês), Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev), public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório

### Community 29 - "Login.tsx"
Cohesion: 0.06
Nodes (33): Levantamento_impressões (planilha original), Logo Elgin é redesenho à mão (IA sem acesso a imagens coladas no chat, só uploads), src/components/ (padrão com header-comment por arquivo), DecommissionedList(), DecommissionedListProps, DepartmentBreakdown(), DepartmentBreakdownProps, MONTHS (+25 more)

### Community 32 - "app-data.tsx"
Cohesion: 0.08
Nodes (40): adaptAlert(), adaptPrinter(), ApiMonthlyReport, formatLastSeen(), loadMonthlyReportFromApi(), toStatus(), toToner(), VALID_COLORS (+32 more)

### Community 36 - "services"
Cohesion: 0.25
Nodes (7): root, framework, root, rewrites, services, backend, frontend

### Community 38 - "printers.py"
Cohesion: 0.17
Nodes (24): create_printer(), create_printer_reading(), get_printer(), get_printer_readings(), list_printers(), list_printers_with_status(), monthly_report(), get (+16 more)

### Community 40 - "snmp.py"
Cohesion: 0.11
Nodes (15): parse_varbinds(), SNMP Collector para impressoras. Porte direto da funcao Get-TonerSNMP de…, Decodifica um OID BER para notacao pontuada., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Le um TLV BER. Retorna (tag, length, value_start, next_pos)., _read_oid(), _read_tlv(), check() (+7 more)

### Community 41 - "SNMPClient"
Cohesion: 0.20
Nodes (7): Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Cor pela descricao; se nao identificar e for colorida, usa indice % 4., GET de uma OCTET STRING., Envia um GET e devolve o primeiro varbind valido da resposta., SNMPv1 GET (PS1: Build-SnmpGet, version 0, PDU 0xA0)., SNMPv2c GETBULK (PS1: Build-SnmpGetBulk, version 1, PDU 0xA5)., SNMPClient

### Community 42 - "cn"
Cohesion: 0.05
Nodes (66): AlertsPage(), DashboardPage(), AlertBanner(), AlertBannerProps, AlertsView(), AlertsViewProps, AlertsDonutCard(), AlertsDonutCardProps (+58 more)

### Community 46 - "Settings"
Cohesion: 0.29
Nodes (5): Config, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Settings, BaseSettings, field_validator

## Knowledge Gaps
- **133 isolated node(s):** `$schema`, `typescript`, `oxc`, `react/rules-of-hooks`, `warn` (+128 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SNMPClient` connect `SNMPClient` to `snmp.py`, `.collect`, `TonerInfo`, `PrinterCollector`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `PrinterCollector` connect `PrinterCollector` to `SNMPClient`, `SNMPResult`, `collect.py`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `Elgin Impressoras (painel de monitoramento)` connect `Elgin Impressoras (painel de monitoramento)` to `Modo Simulado`, `Simular-Ambiente.ps1`, `Login.tsx`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `SNMPClient` (e.g. with `PrinterCollector` and `FakeAgent`) actually correct?**
  _`SNMPClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `PrinterCollector` (e.g. with `collect_fleet()` and `collect_printer()`) actually correct?**
  _`PrinterCollector` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `SNMPResult` (e.g. with `PrinterCollector` and `FleetMockClient`) actually correct?**
  _`SNMPResult` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `typescript`, `oxc` to the rest of the system?**
  _133 weakly-connected nodes found - possible documentation gaps or missing edges._