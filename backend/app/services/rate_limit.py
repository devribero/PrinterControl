"""
Limite de tentativas para o login (Fase 10).

POR QUE existe
--------------
`POST /api/auth/login` era ilimitado: com o backend exposto por tunel, uma
lista de senhas comuns podia ser testada contra `pedro.ribeiro@example.com`
na velocidade da rede, sem que nada no sistema registrasse ou atrasasse a
tentativa. O argon2 encarece cada verificacao, mas nao impede milhares delas.

DUAS CHAVES, de proposito
-------------------------
Cada tentativa consome credito em duas contagens independentes:

    ip:<endereco>      -> segura um atacante de uma origem so, varrendo
                          varias contas ("password spraying").
    email:<conta>      -> segura um ataque distribuido contra UMA conta, que
                          a contagem por IP nao veria.

A contagem por e-mail e o que mais protege nesta instalacao: atras de um
Cloudflare Tunnel todo request chega com o mesmo IP de origem (o do tunel),
entao a contagem por IP tende a virar uma contagem global. Ela e mantida
assim mesmo — se um dia o backend for exposto direto, ela volta a discriminar
— mas nao se deve contar com ela enquanto o tunel estiver na frente.

ESTADO EM MEMORIA
-----------------
Um dicionario no processo, nao Redis. E coerente com o resto do deploy: uma
unica instancia de uvicorn na maquina do Print Server. As consequencias sao
reais e ficam registradas: reiniciar o servico zera as contagens, e se um dia
houver mais de um worker cada um contara por si. Enquanto o desenho for de um
processo so, isso e suficiente; deixar de limitar por nao ter Redis nao era.

O bloqueio e por JANELA DESLIZANTE e nao trava a conta: passada a janela sem
tentativas, o acesso volta sozinho. Bloquear a conta ate um admin liberar
transformaria o ataque em negacao de servico contra o dono legitimo.
"""
import threading
import time
from dataclasses import dataclass


@dataclass
class ResultadoLimite:
    """Veredito de uma checagem. `retry_after` so faz sentido quando bloqueado."""

    bloqueado: bool
    retry_after: int = 0
    tentativas: int = 0


class RateLimiter:
    """
    Janela deslizante em memoria, protegida por lock.

    O lock existe porque o uvicorn atende requisicoes em threads: sem ele,
    duas tentativas simultaneas poderiam ler a mesma contagem e ambas passar.
    """

    def __init__(self, max_tentativas: int, janela_segundos: int):
        self.max_tentativas = max_tentativas
        self.janela_segundos = janela_segundos
        self._tentativas: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    def _limpar(self, chave: str, agora: float) -> list[float]:
        """Descarta o que saiu da janela e devolve o que restou."""
        limite = agora - self.janela_segundos
        restantes = [t for t in self._tentativas.get(chave, []) if t > limite]
        if restantes:
            self._tentativas[chave] = restantes
        else:
            self._tentativas.pop(chave, None)
        return restantes

    def verificar(self, chaves: list[str]) -> ResultadoLimite:
        """
        Diz se a tentativa deve ser recusada — sem consumir credito.

        Separado de `registrar_falha` porque a checagem acontece ANTES de
        tocar no banco ou no hash: o objetivo do limite e justamente nao
        pagar esse custo por tentativa.
        """
        agora = time.monotonic()
        with self._lock:
            pior = ResultadoLimite(bloqueado=False)
            for chave in chaves:
                restantes = self._limpar(chave, agora)
                if len(restantes) >= self.max_tentativas:
                    espera = int(self.janela_segundos - (agora - restantes[0])) + 1
                    if espera > pior.retry_after:
                        pior = ResultadoLimite(
                            bloqueado=True,
                            retry_after=espera,
                            tentativas=len(restantes),
                        )
            return pior

    def registrar_falha(self, chaves: list[str]) -> None:
        """Consome credito. So a FALHA conta — login certo nao gasta nada."""
        agora = time.monotonic()
        with self._lock:
            for chave in chaves:
                self._limpar(chave, agora)
                self._tentativas.setdefault(chave, []).append(agora)

    def limpar(self, chaves: list[str]) -> None:
        """
        Zera as contagens apos um login BEM-SUCEDIDO.

        Sem isto, quem erra a senha algumas vezes, acerta, e erra de novo mais
        tarde acabaria bloqueado por tentativas que ja foram explicadas por um
        acesso legitimo no meio.
        """
        with self._lock:
            for chave in chaves:
                self._tentativas.pop(chave, None)

    def reset(self) -> None:
        """Esvazia tudo. Existe para os testes; nao ha rota que chegue aqui."""
        with self._lock:
            self._tentativas.clear()
