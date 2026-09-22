"""
Fase 12 - importa o historico de paginas por impressora (Jan-Jun/2026,
ou o que a planilha tiver) da planilha "Levantamento impressoes" para
PrinterMonthly — a mesma tabela que o fechamento automatico do scheduler
usa (services/scheduler.py). E o que faz GET /monthly-report mostrar
consumo real nos meses anteriores a existencia do backend, em vez de cair
no conjunto de demonstracao.

So biblioteca padrao do Python (zipfile + xml.etree) — sem openpyxl nem
pandas. E um script de uso unico/esporadico (roda de novo quando um mes
novo da planilha ficar pronto), entao nao vale adicionar uma dependencia
permanente ao requirements.txt so por causa dele.

FORMATO ESPERADO DA PLANILHA (aba "Contabilizacao mensal")
------------------------------------------------------------
Blocos por site (um "ELGIN MC", "MANAUS 1 - ...", etc. por bloco), cada um
com uma linha "IP, Modelo, Serial, Departamento, Janeiro..Dezembro" seguida
de uma linha por impressora e uma linha "Total:" no fim. Um bloco e
reconhecido assim: a linha do cabecalho de site tem EXATAMENTE UMA celula
preenchida (o nome do site); a linha seguinte comeca com "IP"; dali em
diante, toda linha com IP valido na primeira coluna e uma impressora, ate
a linha "Total:"/"Total".

Impressoras cujo identificador nao e um IPv4 valido (ex.: "Estoque",
"Backup", "-") sao PULADAS e listadas no relatorio, nunca adivinhadas.

CASAMENTO COM O BANCO (revisto em 21/09/2026, planilha v8)
----------------------------------------------------------
Primeiro pelo SERIAL, depois pelo IP. O serial identifica o equipamento
fisico; o IP muda — na v8, 13 equipamentos ja estavam em outro endereco.
Um IP com varias filas e um equipamento so: o historico vai para uma fila
(a ativa de menor id). Ficam de fora, listados no relatorio, nunca
adivinhados: IP repetido na propria planilha sem serial que resolva, IP em
que o SNMP identifica outro equipamento, e dois itens apontando para o
mesmo equipamento.

Alem do historico, atualiza o cadastro: departamento no formato
"Departamento — Unidade" e serial onde o banco nao tem (ver
importar_para_banco).

USO
----
    # sempre roda em modo simulacao primeiro — nao grava nada, so mostra
    # o que seria importado e o que ficaria de fora
    .\\venv\\Scripts\\python.exe import_historico_planilha.py "Levantamento impressoes_v6.xlsx"

    # depois de revisar o relatorio, grava de verdade
    .\\venv\\Scripts\\python.exe import_historico_planilha.py "Levantamento impressoes_v6.xlsx" --aplicar

    # planilha de outro ano (padrao: 2026, o ano dos meses da aba)
    .\\venv\\Scripts\\python.exe import_historico_planilha.py planilha.xlsx --ano 2027 --aplicar

Idempotente: rodar de novo (planilha atualizada, com Julho preenchido por
exemplo) so sobrescreve os meses que a nova planilha tiver — mesma chave
(impressora, mes) de upsert_printer_monthly(), nunca duplica.
"""
import argparse
import sys
from datetime import datetime

# Leitura e reconhecimento da planilha vivem em app/services/planilha_levantamento.py
# desde 22/09/2026 — o gerador do levantamento mensal (services/levantamento.py)
# usa os mesmos. Reexportados aqui porque testes e scripts importam daqui.
from app.services.planilha_levantamento import (  # noqa: F401
    IPV4_RE,
    MAC_RE,
    MONTH_COLUMNS,
    NS,
    NS_R,
    SHEET_NAME,
    LinhaImpressora,
    PlanilhaError,
    _cell_value,
    _coluna,
    _e_cabecalho_de_site,
    _e_linha_ip,
    _e_linha_total,
    _ler_planilha,
    _num,
    _parse_blocos,
    _posicao_total,
    indices_do_banco,
    localizar_equipamento,
    meses_preenchidos,
    periodos_da_planilha,
)


# Bloco da planilha -> unidade, no padrao "Departamento — Unidade" que o
# banco ja usa (e que o painel separa em lib/site.ts para agrupar o
# Historico por unidade). Bloco que nao estiver aqui entra com o proprio
# nome, e aparece no relatorio.
UNIDADES = {
    "ELGIN VILA OLÍMPIA": "Vila Olímpia",
    "ELGIN MC": "MC",
    "ELGIN ITAJAÍ": "Itajaí",
    "MANAUS 1 - PRODUÇÃO AR CONDICIONADO": "Manaus 1 - Ar Condicionado",
    "MANAUS 2 - AUTOMAÇÃO": "Manaus 2 - Automação",
    "MANAUS 3 - LOGÍSTICA": "Manaus 3 - Logística",
    "JUNDIAÍ - LOGÍSTICA": "Jundiaí",
    "CABO DE SANTO AGOSTINHO - LOGÍSTICA": "Cabo de Santo Agostinho",
    "COLORIDAS": "Coloridas (multi-site)",
}

def _unidade(site: str | None) -> str:
    nome = (site or "").strip()
    return UNIDADES.get(nome.upper(), nome.title())


def _departamento(item: "LinhaImpressora") -> str | None:
    """'Qualidade HDB (P&B).' + bloco ELGIN MC -> 'Qualidade HDB (P&B) — MC'."""
    dep = (item.departamento or "").strip().rstrip(".").strip()
    if not dep or dep == "-":
        return None
    return f"{dep} — {_unidade(item.site)}"


def importar_para_banco(
    session,
    impressoras: list[LinhaImpressora],
    ano: int,
    aplicar: bool,
    periodos: dict[str, tuple[datetime, datetime]] | None = None,
) -> dict:
    """
    Casa cada LinhaImpressora por IP contra o banco e, se aplicar=True:

      - grava o historico mensal em PrinterMonthly (upsert por impressora+mes);
      - atualiza o cadastro de TODAS as filas daquele IP: departamento no
        formato "Departamento — Unidade", e o serial onde o banco nao tem.

    Nao commita — quem chama decide (main() so commita com --aplicar).

    POR EQUIPAMENTO (21/09/2026)
    ----------------------------
    Um IP com varias filas e UM equipamento, e a planilha tem uma linha por
    equipamento. O historico vai para uma fila so — a ativa de menor id —
    para nao contar as paginas uma vez por fila (mesma regra do relatorio
    ao vivo, ver monthly_report._one_per_device). Antes, IP com mais de uma
    fila era pulado inteiro como "ambiguo", e equipamentos importantes
    ficavam sem historico.

    Ambiguo agora e o IP que aparece MAIS DE UMA VEZ NA PLANILHA com
    equipamentos diferentes: nao da para saber qual linha e a certa, entao
    nenhuma entra.

    SERIAL
    ------
    So preenche onde o banco esta vazio. Quando ja existe um serial, ele
    veio do SNMP — lido do proprio equipamento — e e mais confiavel que o
    digitado; divergencias aparecem no relatorio em vez de sobrescrever.
    """
    from collections import Counter

    from sqlmodel import select

    from app.models.printer import Printer, PrinterMonthly
    from app.services.monthly_report import upsert_printer_monthly

    por_ip, por_serial = indices_do_banco(session.exec(select(Printer)).all())

    repeticoes = Counter(item.ip for item in impressoras)
    meses = meses_preenchidos(impressoras)

    importados = 0
    linhas_gravadas = 0
    nao_encontrados: list[str] = []
    ambiguos: list[str] = []
    multiplas_filas: list[str] = []
    cadastro: list[str] = []
    conflitos: list[str] = []
    casados_por_serial: list[str] = []
    realocados: list[str] = []
    seriais_ignorados: list[str] = []
    # IP de equipamento ja usado por uma linha: uma segunda linha apontando
    # para o mesmo equipamento e conflito, nunca soma por cima.
    equipamentos_usados: dict[str, int] = {}

    for item in impressoras:
        rotulo = f"[{item.site}] linha {item.linha_num}: {item.ip} ({item.modelo}, {item.departamento})"
        casamento = localizar_equipamento(item, por_ip, por_serial, repeticoes)
        serial, serial_valido = casamento.serial, casamento.serial_valido
        if serial and serial != "-" and not serial_valido:
            seriais_ignorados.append(f"IP {item.ip}: {serial!r} parece MAC, nao numero de serie — ignorado.")

        # SERIAL primeiro, depois IP — regra e motivos em
        # planilha_levantamento.localizar_equipamento.
        if casamento.situacao == "ambiguo":
            ambiguos.append(f"{rotulo}: IP aparece {repeticoes[item.ip]} vezes na planilha — corrija la e importe de novo.")
            continue
        if casamento.situacao == "nao_encontrado":
            nao_encontrados.append(f"{rotulo}: nao encontrado no banco (nem pelo IP, nem pelo serial).")
            continue
        if casamento.situacao == "conflito":
            conflitos.append(
                f"{rotulo}: no banco esse IP e o serial {', '.join(casamento.seriais_no_ip)} (lido por SNMP), "
                f"e o serial da planilha ({serial}) nao existe em lugar nenhum — equipamento trocado? Nao importado."
            )
            continue
        filas = casamento.filas
        if casamento.ip_real:
            casados_por_serial.append(f"{rotulo}: o serial {serial} esta hoje em {casamento.ip_real} — casado por la.")

        chave = filas[0].ip
        if chave in equipamentos_usados:
            conflitos.append(
                f"{rotulo}: o equipamento em {chave} ja recebeu a linha {equipamentos_usados[chave]} da planilha. Nao importado."
            )
            continue
        equipamentos_usados[chave] = item.linha_num

        # Representante do equipamento: ativa primeiro, depois o menor id.
        filas = sorted(filas, key=lambda p: (not p.active, p.id))
        representante = filas[0]
        if len(filas) > 1:
            multiplas_filas.append(
                f"IP {chave}: {len(filas)} filas; historico em {representante.name} (id={representante.id})"
            )

        importados += 1
        periodos_do_item = []
        for idx, mes_nome in enumerate(MONTH_COLUMNS, start=1):
            if mes_nome not in meses or mes_nome not in item.meses:
                continue
            period = f"{ano}-{idx:02d}"
            periodos_do_item.append(period)
            # Periodo real da planilha (ex.: agosto = 04/08 a 03/09) quando a
            # aba traz a tabela de periodos; senao, o mes do calendario. O fim
            # e o ponto de onde o sistema continua contando o mes seguinte.
            if periodos and mes_nome in periodos:
                mes_inicio, mes_fim = periodos[mes_nome]
            else:
                mes_inicio = datetime(ano, idx, 1)
                mes_fim = datetime(ano + 1, 1, 1) if idx == 12 else datetime(ano, idx + 1, 1)
            if aplicar:
                upsert_printer_monthly(session, representante.id, period, item.meses[mes_nome], mes_inicio, mes_fim)
            linhas_gravadas += 1

        # Autocorrecao: outro registro com o MESMO serial em outro IP e copia
        # velha (ex.: a importacao anterior casou pelo IP antigo, antes do
        # SNMP ler o serial do equipamento no IP novo). O historico destes
        # meses sai de la — ele agora esta no equipamento certo — e, se o
        # registro velho estiver inativo, o serial duplicado tambem sai.
        if serial_valido:
            for velho in por_serial.get(serial.upper(), []):
                if velho.ip == chave:
                    continue
                antigos = session.exec(
                    select(PrinterMonthly)
                    .where(PrinterMonthly.printer_id == velho.id)
                    .where(PrinterMonthly.month.in_(periodos_do_item))
                ).all()
                if antigos:
                    realocados.append(
                        f"{velho.name} ({velho.ip}): {len(antigos)} mes(es) de historico movidos para "
                        f"{representante.name} ({chave}) — mesmo serial {serial}."
                    )
                    if aplicar:
                        for linha in antigos:
                            session.delete(linha)
                if not velho.active:
                    realocados.append(f"{velho.name} ({velho.ip}, inativa): serial duplicado {serial} removido.")
                    if aplicar:
                        velho.serial_number = None
                        session.add(velho)

        # Cadastro: vale para todas as filas do equipamento. Serial so onde o
        # banco esta vazio — chegando aqui ou ele ja e o mesmo (casou pelo
        # serial) ou o IP nao tinha serial nenhum.
        departamento = _departamento(item)
        for fila in filas:
            if departamento and fila.department != departamento:
                cadastro.append(f"{fila.name}: departamento {fila.department or '(vazio)'!r} -> {departamento!r}")
                if aplicar:
                    fila.department = departamento
                    session.add(fila)
            if serial_valido and not (fila.serial_number or "").strip():
                cadastro.append(f"{fila.name}: serial (vazio) -> {serial!r}")
                if aplicar:
                    fila.serial_number = serial
                    session.add(fila)

    return {
        "importados": importados,
        "nao_encontrados": nao_encontrados,
        "ambiguos": ambiguos,
        "linhas_gravadas": linhas_gravadas,
        "meses": meses,
        "multiplas_filas": multiplas_filas,
        "cadastro": cadastro,
        "conflitos": conflitos,
        "casados_por_serial": casados_por_serial,
        "realocados": realocados,
        "seriais_ignorados": seriais_ignorados,
    }


def main() -> int:
    # Console do Windows costuma abrir em cp1252/850, nao UTF-8 — sem isto,
    # nomes de site com acento (ex.: "Vila Olimpia") saem como lixo no
    # relatorio, mesmo com o dado lido corretamente.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("planilha", help="Caminho do arquivo .xlsx")
    parser.add_argument("--aplicar", action="store_true", help="Grava de verdade no banco (padrao: so simula)")
    parser.add_argument("--ano", type=int, default=2026, help="Ano dos meses da planilha (padrao: 2026)")
    args = parser.parse_args()

    try:
        linhas = _ler_planilha(args.planilha)
    except PlanilhaError as e:
        print(f"[ERRO] {e}")
        return 1

    impressoras, avisos = _parse_blocos(linhas)

    if not impressoras:
        print("[ERRO] Nenhuma linha de impressora encontrada — formato da planilha mudou?")
        return 1

    # So importa aqui para nao exigir DATABASE_URL/venv soh para --help.
    from sqlmodel import Session

    from app.database import engine

    with Session(engine) as session:
        resultado = importar_para_banco(
            session, impressoras, args.ano, args.aplicar, periodos_da_planilha(linhas, args.ano)
        )
        if args.aplicar:
            session.commit()

    verbo = "gravad" if args.aplicar else "que SERIAM gravad"
    print(f"\n{'=' * 70}")
    print(f"Linhas de impressora lidas na planilha: {len(impressoras)}")
    print(f"Meses ja fechados na planilha (os unicos importados): {', '.join(resultado['meses']) or '(nenhum)'}")
    print(f"Equipamentos casados (pelo serial ou pelo IP) e {verbo}os: {resultado['importados']}")
    print(f"Meses/equipamento {verbo}os: {resultado['linhas_gravadas']}")
    print(f"Mudancas de cadastro {verbo}as: {len(resultado['cadastro'])}")

    if resultado["cadastro"]:
        print(f"\n--- Cadastro (departamento/serial) ({len(resultado['cadastro'])}) ---")
        for msg in resultado["cadastro"]:
            print(f"  {msg}")

    if resultado["multiplas_filas"]:
        print(f"\n--- Equipamentos com mais de uma fila ({len(resultado['multiplas_filas'])}) ---")
        for msg in resultado["multiplas_filas"]:
            print(f"  {msg}")

    if resultado["casados_por_serial"]:
        print(f"\n--- Casados pelo serial: o equipamento mudou de IP ({len(resultado['casados_por_serial'])}) ---")
        for msg in resultado["casados_por_serial"]:
            print(f"  {msg}")

    if resultado["realocados"]:
        print(f"\n--- Autocorrecao: historico/serial movidos de registros velhos ({len(resultado['realocados'])}) ---")
        for msg in resultado["realocados"]:
            print(f"  {msg}")

    if resultado["conflitos"]:
        print(f"\n--- Conflitos, nao importados ({len(resultado['conflitos'])}) ---")
        for msg in resultado["conflitos"]:
            print(f"  {msg}")

    if resultado["seriais_ignorados"]:
        print(f"\n--- Serial ignorado ({len(resultado['seriais_ignorados'])}) ---")
        for msg in resultado["seriais_ignorados"]:
            print(f"  {msg}")

    if resultado["nao_encontrados"]:
        print(f"\n--- IP nao encontrado no banco ({len(resultado['nao_encontrados'])}) ---")
        for msg in resultado["nao_encontrados"]:
            print(f"  {msg}")

    if resultado["ambiguos"]:
        print(f"\n--- IP repetido na planilha, nao importado ({len(resultado['ambiguos'])}) ---")
        for msg in resultado["ambiguos"]:
            print(f"  {msg}")

    if avisos:
        print(f"\n--- Avisos ({len(avisos)}) ---")
        for msg in avisos:
            print(f"  {msg}")

    print(f"\n{'=' * 70}")
    if args.aplicar:
        print("GRAVADO no banco.")
    else:
        print("SIMULACAO — nada foi gravado. Revise o relatorio acima e rode de novo com --aplicar.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
