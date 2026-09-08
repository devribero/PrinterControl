"""
Tipos compartilhados pelos schemas e pelas rotas.
"""
from typing import Annotated

from fastapi import Path

# Maior inteiro que um INTEGER de SQLite (e um BIGINT de PostgreSQL) guarda.
# Duplicado de schemas/printer.py de proposito: este modulo nao importa nada
# do projeto, para poder ser usado por qualquer rota sem risco de ciclo.
INT64_MAX = 2**63 - 1


#: Id de recurso vindo da URL.
#:
#: QA-08: `printer_id: int` puro aceitava
#: `/api/printers/999999999999999999999999999999` — o Pydantic converte o
#: numero sem reclamar, e so o driver do banco protestava, com OverflowError
#: virando 500. Um id impossivel e um pedido malformado do cliente, entao a
#: resposta certa e 422, decidida antes de qualquer consulta.
#:
#: `ge=1` porque as chaves sao AUTOINCREMENT e comecam em 1: 0 e negativos
#: nunca correspondem a nada e nao precisam chegar ao banco.
RecursoId = Annotated[int, Path(ge=1, le=INT64_MAX)]
