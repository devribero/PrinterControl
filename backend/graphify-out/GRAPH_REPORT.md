# Graph Report - backend  (2026-08-18)

## Corpus Check
- 30 files · ~9,885 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 244 nodes · 495 edges · 14 communities
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 27 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `df944eb9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SNMPClient
- collect.py
- PrinterCollector
- SNMPResult
- routes/auth.py
- printers.py
- FakeAgent
- tests_collect_api.py

## God Nodes (most connected - your core abstractions)
1. `SNMPClient` - 32 edges
2. `PrinterCollector` - 20 edges
3. `SNMPResult` - 19 edges
4. `Printer` - 16 edges
5. `Alert` - 13 edges
6. `FakeAgent` - 12 edges
7. `PrinterReading` - 11 edges
8. `MockSNMPScenarios` - 11 edges
9. `TonerInfo` - 9 edges
10. `MockSNMPClient` - 9 edges

## Surprising Connections (you probably didn't know these)
- `active()` --uses--> `Alert`  [INFERRED]
  tests_alerts.py → app/models/alert.py
- `resolved()` --uses--> `Alert`  [INFERRED]
  tests_alerts.py → app/models/alert.py
- `FakeAgent` --uses--> `SNMPClient`  [INFERRED]
  tests_snmp_local.py → app/services/snmp.py
- `seed_database()` --calls--> `create_db_and_tables()`  [EXTRACTED]
  seed.py → app/database.py
- `seed_database()` --calls--> `Printer`  [EXTRACTED]
  seed.py → app/models/printer.py

## Import Cycles
- None detected.

## Communities (14 total, 0 thin omitted)

### Community 0 - "SNMPClient"
Cohesion: 0.06
Nodes (35): parse_varbinds(), SNMP Collector para impressoras. Porte direto da funcao Get-TonerSNMP de…, Decodifica um OID BER para notacao pontuada., Decodifica bytes BER como inteiro sem sinal., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta. (+27 more)

### Community 1 - "collect.py"
Cohesion: 0.07
Nodes (41): Config, Settings, create_db_and_tables(), get_session(), _migrate_alert_type(), Adiciona alerts.alert_type em bancos criados antes da Etapa 8A., health_check(), lifespan() (+33 more)

### Community 2 - "PrinterCollector"
Cohesion: 0.11
Nodes (25): Alert, SQLModel, TonerHistory, PrinterMonthly, PrinterReading, SQLModel, _active(), evaluate_reading() (+17 more)

### Community 3 - "SNMPResult"
Cohesion: 0.09
Nodes (19): Cenarios de teste disponiveis (fonte unica: snmp_mock.SCENARIOS)., Args: mode: "real" (SNMP de verdade) ou "mock" (cenario simulado)…, MockSNMPClient, MockSNMPScenarios, Agente SNMP simulado — APENAS PARA TESTE LOCAL. Existe porque a maquina de…, SNMP responde o contador, mas nao expoe a tabela de consumiveis., Monocromatica com toner em 5%., Colorida com ciano critico (18%) e os demais normais. (+11 more)

### Community 4 - "routes/auth.py"
Cohesion: 0.19
Nodes (17): SQLModel, User, login(), post, Session, register(), Config, BaseModel (+9 more)

### Community 5 - "printers.py"
Cohesion: 0.21
Nodes (20): Printer, create_printer(), create_printer_reading(), get_printer(), get_printer_readings(), list_printers(), get, patch (+12 more)

### Community 6 - "FakeAgent"
Cohesion: 0.24
Nodes (3): FakeAgent, Extrai (pdu_tag, [oids]) de um GET/GETBULK., Responde GET e GETBULK para um conjunto de OIDs configurado.

### Community 7 - "tests_collect_api.py"
Cohesion: 0.67
Nodes (3): check(), main(), Teste ponta a ponta dos endpoints /api/collect com os cenarios simulados.…

## Knowledge Gaps
- **2 isolated node(s):** `Config`, `Config`
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SNMPClient` connect `SNMPClient` to `PrinterCollector`, `SNMPResult`, `FakeAgent`?**
  _High betweenness centrality (0.337) - this node is a cross-community bridge._
- **Why does `PrinterCollector` connect `PrinterCollector` to `SNMPClient`, `collect.py`, `SNMPResult`, `printers.py`?**
  _High betweenness centrality (0.216) - this node is a cross-community bridge._
- **Why does `SNMPResult` connect `SNMPResult` to `SNMPClient`, `PrinterCollector`?**
  _High betweenness centrality (0.144) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `SNMPClient` (e.g. with `PrinterCollector` and `FakeAgent`) actually correct?**
  _`SNMPClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `PrinterCollector` (e.g. with `collect_printer()` and `list_scenarios()`) actually correct?**
  _`PrinterCollector` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `SNMPResult` (e.g. with `PrinterCollector` and `MockSNMPClient`) actually correct?**
  _`SNMPResult` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `Printer` (e.g. with `create_printer()` and `create_printer_reading()`) actually correct?**
  _`Printer` has 6 INFERRED edges - model-reasoned connections that need verification._