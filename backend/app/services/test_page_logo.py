"""
Logo Elgin da pagina de teste: bitmap de 1 bit, 300 dpi, linha a linha.

GERADO por gerar_logo_pagina_teste.py a partir de public/logo-elgin-trim.png
— nao editar a mao.
"""
import base64
import zlib

LARGURA = 600
ALTURA = 248
BYTES_POR_LINHA = 75

_DADOS = (
    "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"
    "9A=="
)


def linhas() -> list[bytes]:
    """Uma entrada por linha de pixels, bit 1 = tinta, MSB a esquerda."""
    bruto = zlib.decompress(base64.b64decode(_DADOS))
    return [bruto[i:i + BYTES_POR_LINHA] for i in range(0, len(bruto), BYTES_POR_LINHA)]
