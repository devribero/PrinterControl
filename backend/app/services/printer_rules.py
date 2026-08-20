"""
Regras de classificacao portadas do Main.ps1 (Etapa 4).

Correspondencia exata:
    Obter-Modelo          -> obter_modelo
    Obter-TipoImpressora   -> obter_tipo_impressora

O PowerShell usa `switch -Regex` sem `break` em Obter-Modelo, o que
tecnicamente deixaria varios casos "casarem" se os padroes se sobrepusessem
— na pratica os padroes sao mutuamente exclusivos (P 311 vs P 502 vs M3040,
etc.), entao aqui usamos a primeira regra que casar, com o mesmo resultado.
Obter-TipoImpressora ja usa `break` explicito no original.
"""
import re

# Ordem importa: primeira regra que casar vence (equivalente ao Main.ps1).
_MODEL_RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"P 311", re.I), "Ricoh P311"),
    (re.compile(r"P 502", re.I), "Ricoh P502"),
    (re.compile(r"M3040", re.I), "Kyocera M3040idn"),
    (re.compile(r"P3055", re.I), "Kyocera P3055dn"),
    (re.compile(r"M6530", re.I), "Kyocera M6530cdn"),
    (re.compile(r"Honeywell", re.I), "Honeywell RP4f"),
    (re.compile(r"TT042", re.I), "Elgin TT042"),
    (re.compile(r"ELGIN", re.I), "Elgin TT042 Plus"),
]

# `$Driver -replace '\s+(PCL\d*|PS|KX|XPS|UFR\s*II|Class Driver)\b.*', ''`
_SUFFIX_RE = re.compile(r"\s+(PCL\d*|PS|KX|XPS|UFR\s*II|Class Driver)\b.*", re.I)


def obter_modelo(driver_name: str) -> str:
    """Traduz DriverName (Windows) em nome comercial, igual ao Main.ps1."""
    for pattern, model in _MODEL_RULES:
        if pattern.search(driver_name or ""):
            return model
    return _SUFFIX_RE.sub("", driver_name or "").strip()


# Etiqueta/Portatil sao checados antes de A4 porque marcas como Elgin/
# Honeywell tambem podem casar termos genericos — mesma ordem do Main.ps1.
_TYPE_RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"zebra|elgin|tt042|argox", re.I), "Etiqueta"),
    (re.compile(r"honeywell|rp4f|sewoo|portatil|portátil", re.I), "Portatil"),
    (
        re.compile(r"canon|kyocera|ricoh|pantum|hp\b|epson|brother|xerox|lexmark|samsung", re.I),
        "A4",
    ),
]


def obter_tipo_impressora(nome: str, modelo: str) -> str:
    """Classifica A4 / Etiqueta / Portatil a partir de Nome+Modelo, igual ao Main.ps1."""
    texto = f"{nome or ''} {modelo or ''}"
    for pattern, tipo in _TYPE_RULES:
        if pattern.search(texto):
            return tipo
    return "A4"
