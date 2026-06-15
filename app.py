from flask import Flask, jsonify, request
from flask_cors import CORS
from itertools import combinations
from collections import Counter
from math import comb
import requests
import time

app = Flask(__name__)
CORS(app)

TODAS_DEZENAS = set(range(1, 26))

# Fonte principal rapida. A documentacao publica indica /api/<loteria>/latest e /api/<loteria>/<concurso>.
URL_HEROKU_BASE = "https://loteriascaixa-api.herokuapp.com/api/lotofacil"

# Fallbacks
URL_GUIDI_BASE = "https://api.guidi.dev.br/loteria/lotofacil"
URL_CAIXA = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"

CACHE_HISTORICO = {}
CACHE_CRIADO_EM = {}
CACHE_TTL_SEGUNDOS = 60 * 60 * 6

# No Render Free, carregar todos os concursos um por um estoura timeout.
# Esta versao usa os ultimos N concursos para frequencia e historico.
LIMITE_HISTORICO_PADRAO = 300
LIMITE_HISTORICO_MAXIMO = 800


def formatar_dezenas(dezenas):
    return [str(int(n)).zfill(2) for n in dezenas]


def normalizar_dezenas(valor):
    if not valor:
        return []

    dezenas = []
    for item in valor:
        try:
            numero = int(item)
            if 1 <= numero <= 25:
                dezenas.append(numero)
        except Exception:
            pass

    dezenas = sorted(set(dezenas))
    if len(dezenas) == 15:
        return dezenas

    return []


def extrair_resultado(dados):
    if not isinstance(dados, dict):
        raise ValueError("Resposta da API em formato inesperado.")

    concurso = (
        dados.get("numero")
        or dados.get("concurso")
        or dados.get("numeroConcurso")
        or dados.get("id")
    )

    data = (
        dados.get("dataApuracao")
        or dados.get("data")
        or dados.get("dataSorteio")
        or dados.get("data_concurso")
        or ""
    )

    possiveis_chaves_dezenas = [
        "listaDezenas",
        "dezenas",
        "numeros",
        "resultado",
        "dezenasSorteadasOrdemSorteio",
        "dezenasSorteadas",
    ]

    dezenas = []
    for chave in possiveis_chaves_dezenas:
        if chave in dados:
            dezenas = normalizar_dezenas(dados.get(chave))
            if dezenas:
                break

    if not dezenas:
        for valor in dados.values():
            if isinstance(valor, list):
                dezenas = normalizar_dezenas(valor)
                if dezenas:
                    break

    if not concurso or not dezenas:
        raise ValueError("Nao consegui identificar concurso ou dezenas na resposta da API.")

    return {
        "concurso": int(concurso),
        "data": data,
        "dezenas": dezenas
    }


def get_json(url, timeout=12):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json,text/plain,*/*",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    }

    resposta = requests.get(url, headers=headers, timeout=timeout)
    resposta.raise_for_status()
    return resposta.json()


def baixar_concurso_heroku(numero=None):
    sufixo = "latest" if numero is None else str(numero)
    dados = get_json(f"{URL_HEROKU_BASE}/{sufixo}", timeout=12)
    resultado = extrair_resultado(dados)
    resultado["fonte"] = "heroku"
    return resultado


def baixar_concurso_guidi(numero=None):
    sufixo = "ultimo" if numero is None else str(numero)
    dados = get_json(f"{URL_GUIDI_BASE}/{sufixo}", timeout=12)
    resultado = extrair_resultado(dados)
    resultado["fonte"] = "guidi"
    return resultado


def baixar_concurso_caixa(numero=None):
    url = URL_CAIXA if numero is None else f"{URL_CAIXA}/{numero}"
    dados = get_json(url, timeout=12)
    resultado = extrair_resultado(dados)
    resultado["fonte"] = "caixa"
    return resultado


def baixar_concurso(numero=None):
    erros = []

    # Heroku primeiro porque no Render tem sido mais rapido e menos bloqueado.
    for nome, funcao in [
        ("heroku", baixar_concurso_heroku),
        ("guidi", baixar_concurso_guidi),
        ("caixa", baixar_concurso_caixa),
    ]:
        try:
            return funcao(numero)
        except Exception as erro:
            erros.append(f"{nome}: {erro}")

    raise RuntimeError("Nao foi possivel carregar o concurso. Erros: " + " | ".join(erros))


def obter_limite_historico():
    try:
        limite = int(request.args.get("limite", LIMITE_HISTORICO_PADRAO))
    except Exception:
        limite = LIMITE_HISTORICO_PADRAO

    if limite < 20:
        limite = 20

    if limite > LIMITE_HISTORICO_MAXIMO:
        limite = LIMITE_HISTORICO_MAXIMO

    return limite


def carregar_historico(limite=None):
    global CACHE_HISTORICO, CACHE_CRIADO_EM

    if limite is None:
        limite = LIMITE_HISTORICO_PADRAO

    agora = time.time()
    chave_cache = str(limite)

    if (
        chave_cache in CACHE_HISTORICO
        and (agora - CACHE_CRIADO_EM.get(chave_cache, 0)) < CACHE_TTL_SEGUNDOS
    ):
        return CACHE_HISTORICO[chave_cache]

    ultimo = baixar_concurso()
    ultimo_numero = int(ultimo["concurso"])

    inicio = max(1, ultimo_numero - limite + 1)
    historico = []

    # Carrega do mais recente para tras. Assim, se alguma fonte falhar, ainda usa o que conseguiu.
    for numero in range(ultimo_numero, inicio - 1, -1):
        try:
            item = baixar_concurso(numero)
            if len(item["dezenas"]) == 15:
                historico.append(item)
        except Exception:
            continue

    historico = sorted(historico, key=lambda item: item["concurso"])

    CACHE_HISTORICO[chave_cache] = historico
    CACHE_CRIADO_EM[chave_cache] = agora

    return historico


def calcular_frequencias(historico):
    contador = Counter()

    for item in historico:
        contador.update(item["dezenas"])

    ranking = []

    for dezena in range(1, 26):
        ranking.append({
            "dezena": str(dezena).zfill(2),
            "quantidade": contador[dezena]
        })

    ranking.sort(key=lambda x: x["quantidade"], reverse=True)
    return ranking


def tem_sequencia_maior_que_4(jogo):
    jogo = sorted(jogo)
    atual = 1
    maior = 1

    for i in range(1, len(jogo)):
        if jogo[i] == jogo[i - 1] + 1:
            atual += 1
            maior = max(maior, atual)
        else:
            atual = 1

    return maior > 4


def ja_fez_14_ou_15(jogo, historico):
    jogo_set = set(jogo)

    for item in historico:
        sorteio = set(item["dezenas"])
        acertos = len(jogo_set & sorteio)

        if acertos >= 14:
            return True

    return False


@app.route("/")
def inicio():
    return jsonify({
        "app": "Lotofacil + Facil",
        "status": "online",
        "mensagem": "Backend funcionando corretamente.",
        "modo_historico": f"ultimos {LIMITE_HISTORICO_PADRAO} concursos por padrao para evitar timeout no Render Free",
        "rotas": [
            "/api/ultimo",
            "/api/concurso/3000",
            "/api/frequencias",
            "/api/frequencias?limite=500",
            "/api/gerar"
        ]
    })


@app.route("/api/ultimo")
def api_ultimo():
    try:
        resultado = baixar_concurso()
        resultado["dezenas"] = formatar_dezenas(resultado["dezenas"])
        return jsonify(resultado)
    except Exception as erro:
        return jsonify({"erro": str(erro)}), 500


@app.route("/api/concurso/<int:numero>")
def api_concurso(numero):
    try:
        resultado = baixar_concurso(numero)
        resultado["dezenas"] = formatar_dezenas(resultado["dezenas"])
        return jsonify(resultado)
    except Exception as erro:
        return jsonify({"erro": str(erro)}), 500


@app.route("/api/frequencias")
def api_frequencias():
    try:
        limite = obter_limite_historico()
        historico = carregar_historico(limite=limite)
        ranking = calcular_frequencias(historico)
        return jsonify({
            "total_concursos_usados": len(historico),
            "limite_solicitado": limite,
            "observacao": "No Render Free o historico e limitado para evitar timeout.",
            "ranking": ranking
        })
    except Exception as erro:
        return jsonify({"erro": str(erro)}), 500


@app.route("/api/gerar", methods=["POST"])
def api_gerar():
    try:
        dados = request.get_json() or {}

        fixos = [int(n) for n in dados.get("fixos", [])]
        eliminados = [int(n) for n in dados.get("eliminados", [])]
        quantidade = int(dados.get("quantidade", 10))
        limite_historico = int(dados.get("limite_historico", LIMITE_HISTORICO_PADRAO))

        if limite_historico < 20:
            limite_historico = 20
        if limite_historico > LIMITE_HISTORICO_MAXIMO:
            limite_historico = LIMITE_HISTORICO_MAXIMO

        if quantidade <= 0:
            return jsonify({"erro": "A quantidade de jogos precisa ser maior que zero."}), 400

        if not 2 <= len(fixos) <= 6:
            return jsonify({"erro": "Escolha de 2 a 6 numeros fixos."}), 400

        if not 2 <= len(eliminados) <= 6:
            return jsonify({"erro": "Escolha de 2 a 6 numeros eliminados."}), 400

        if set(fixos) & set(eliminados):
            return jsonify({"erro": "Um numero nao pode ser fixo e eliminado ao mesmo tempo."}), 400

        if not set(fixos).issubset(TODAS_DEZENAS):
            return jsonify({"erro": "Fixos devem estar entre 1 e 25."}), 400

        if not set(eliminados).issubset(TODAS_DEZENAS):
            return jsonify({"erro": "Eliminados devem estar entre 1 e 25."}), 400

        historico = carregar_historico(limite=limite_historico)
        ranking = calcular_frequencias(historico)

        frequencias = {
            int(item["dezena"]): item["quantidade"]
            for item in ranking
        }

        livres = sorted(TODAS_DEZENAS - set(fixos) - set(eliminados))
        completar = 15 - len(fixos)

        if completar > len(livres):
            return jsonify({"erro": "Nao ha dezenas suficientes para completar o jogo."}), 400

        total_bruto = comb(len(livres), completar)

        aprovados = []
        eliminados_sequencia = 0
        eliminados_historico = 0

        for complemento in combinations(livres, completar):
            jogo = sorted(fixos + list(complemento))

            if tem_sequencia_maior_que_4(jogo):
                eliminados_sequencia += 1
                continue

            if ja_fez_14_ou_15(jogo, historico):
                eliminados_historico += 1
                continue

            pontuacao = sum(frequencias.get(n, 0) for n in jogo)

            aprovados.append({
                "dezenas": formatar_dezenas(jogo),
                "pontuacao": pontuacao
            })

        aprovados.sort(key=lambda x: x["pontuacao"], reverse=True)
        selecionados = aprovados[:quantidade]

        return jsonify({
            "fixos": formatar_dezenas(fixos),
            "eliminados": formatar_dezenas(eliminados),
            "historico_usado": len(historico),
            "limite_historico": limite_historico,
            "observacao": "Historico limitado para evitar timeout no Render Free.",
            "total_bruto": total_bruto,
            "eliminados_por_sequencia": eliminados_sequencia,
            "eliminados_por_historico": eliminados_historico,
            "total_aprovados": len(aprovados),
            "total_selecionados": len(selecionados),
            "jogos": selecionados
        })

    except Exception as erro:
        return jsonify({"erro": str(erro)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
