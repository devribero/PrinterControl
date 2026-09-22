r"""
Gera app/services/test_page_logo.py a partir de public/logo-elgin-trim.png.

A pagina de teste e PCL enviado direto ao IP: a logo vai como raster de 1 bit
(300 dpi), e nao existe Pillow no ambiente — por isso o PNG e decodificado
aqui mesmo, com zlib da biblioteca padrao. Roda so quando a logo mudar:

    .\venv\Scripts\python.exe gerar_logo_pagina_teste.py

Suporta o que o arquivo da logo usa: PNG 8 bits RGBA (tipo 6) sem
entrelacamento. A mascara sai do canal alfa (logo sobre fundo transparente).
"""
import base64
import struct
import zlib
from pathlib import Path

ORIGEM = Path(__file__).resolve().parent.parent / "public" / "logo-elgin-trim.png"
DESTINO = Path(__file__).resolve().parent / "app" / "services" / "test_page_logo.py"
LARGURA_PX = 600  # 2 polegadas a 300 dpi


def ler_png_alfa(caminho: Path) -> tuple[int, int, list[bytearray]]:
    dados = caminho.read_bytes()
    assert dados[:8] == b"\x89PNG\r\n\x1a\n", "nao e PNG"
    pos, idat = 8, bytearray()
    largura = altura = 0
    while pos < len(dados):
        tamanho, tipo = struct.unpack(">I4s", dados[pos:pos + 8])
        corpo = dados[pos + 8:pos + 8 + tamanho]
        if tipo == b"IHDR":
            largura, altura, prof, cor, _, _, entrelaca = struct.unpack(">IIBBBBB", corpo)
            assert (prof, cor, entrelaca) == (8, 6, 0), "so PNG RGBA 8 bits sem entrelacamento"
        elif tipo == b"IDAT":
            idat += corpo
        pos += 12 + tamanho

    bruto = zlib.decompress(bytes(idat))
    bpp, passo = 4, largura * 4
    anterior = bytearray(passo)
    alfas: list[bytearray] = []
    i = 0
    for _ in range(altura):
        filtro = bruto[i]
        linha = bytearray(bruto[i + 1:i + 1 + passo])
        i += 1 + passo
        if filtro == 1:
            for x in range(bpp, passo):
                linha[x] = (linha[x] + linha[x - bpp]) & 0xFF
        elif filtro == 2:
            for x in range(passo):
                linha[x] = (linha[x] + anterior[x]) & 0xFF
        elif filtro == 3:
            for x in range(passo):
                esq = linha[x - bpp] if x >= bpp else 0
                linha[x] = (linha[x] + ((esq + anterior[x]) >> 1)) & 0xFF
        elif filtro == 4:
            for x in range(passo):
                a = linha[x - bpp] if x >= bpp else 0
                b = anterior[x]
                c = anterior[x - bpp] if x >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                linha[x] = (linha[x] + pred) & 0xFF
        alfas.append(linha[3::4])
        anterior = linha
    return largura, altura, alfas


def reduzir(largura: int, altura: int, alfas: list[bytearray], alvo: int) -> tuple[int, int, list[list[int]]]:
    """Media de cobertura por bloco; pixel vira tinta com cobertura >= 50%."""
    escala = largura / alvo
    alvo_h = max(1, round(altura / escala))
    mascara = []
    for yy in range(alvo_h):
        y0, y1 = int(yy * escala), max(int(yy * escala) + 1, int((yy + 1) * escala))
        linha = []
        for xx in range(alvo):
            x0, x1 = int(xx * escala), max(int(xx * escala) + 1, int((xx + 1) * escala))
            soma = n = 0
            for y in range(y0, min(y1, altura)):
                fila = alfas[y]
                for x in range(x0, min(x1, largura)):
                    soma += fila[x]
                    n += 1
            linha.append(1 if n and soma / n >= 128 else 0)
        mascara.append(linha)
    return alvo, alvo_h, mascara


def empacotar(mascara: list[list[int]]) -> bytes:
    saida = bytearray()
    for linha in mascara:
        for i in range(0, len(linha), 8):
            byte = 0
            for bit in linha[i:i + 8]:
                byte = (byte << 1) | bit
            byte <<= 8 - len(linha[i:i + 8])
            saida.append(byte)
    return bytes(saida)


def main() -> None:
    largura, altura, alfas = ler_png_alfa(ORIGEM)
    w, h, mascara = reduzir(largura, altura, alfas, LARGURA_PX)
    bits = empacotar(mascara)
    codificado = base64.b64encode(zlib.compress(bits, 9)).decode("ascii")
    linhas = [codificado[i:i + 100] for i in range(0, len(codificado), 100)]
    DESTINO.write_text(
        '"""\n'
        "Logo Elgin da pagina de teste: bitmap de 1 bit, 300 dpi, linha a linha.\n\n"
        "GERADO por gerar_logo_pagina_teste.py a partir de public/logo-elgin-trim.png\n"
        "— nao editar a mao.\n"
        '"""\n'
        "import base64\n"
        "import zlib\n\n"
        f"LARGURA = {w}\n"
        f"ALTURA = {h}\n"
        f"BYTES_POR_LINHA = {(w + 7) // 8}\n\n"
        "_DADOS = (\n" + "".join(f'    "{l}"\n' for l in linhas) + ")\n\n\n"
        "def linhas() -> list[bytes]:\n"
        '    """Uma entrada por linha de pixels, bit 1 = tinta, MSB a esquerda."""\n'
        "    bruto = zlib.decompress(base64.b64decode(_DADOS))\n"
        "    return [bruto[i:i + BYTES_POR_LINHA] for i in range(0, len(bruto), BYTES_POR_LINHA)]\n",
        encoding="utf-8",
    )
    print(f"{DESTINO.name}: {w}x{h} px, {len(bits)} bytes de bitmap")


if __name__ == "__main__":
    main()
