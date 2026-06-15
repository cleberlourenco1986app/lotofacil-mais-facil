import os
import json
import time
from itertools import combinations
from math import comb
from collections import Counter
import heapq

import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

TODAS_DEZENAS = set(range(1, 26))
URL_CAIXA = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"
ARQUIVO_CACHE = "historico_lotofacil_cache.json"
CACHE_TTL_SEGUNDOS = 60 * 30


def formatar_dezenas(dezenas):
    return [str(int(n)).zfill(2) for n in sorted(dezenas)]


def baixar_json(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=25)
    r.raise_for_status()
    return r.json()


def carregar_cache():
    if not os.path.exists(ARQUIVO_CACHE):
        return None
    try:
        with open(ARQUIVO_CACHE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def salvar_cache(dados):
    with open(ARQUIVO_CACHE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def carregar_historico():
    cache = carregar_cache()
    agora = time.time()
    if cache and cache.get("historico") and agora - cache.get("atualizado_em", 0) < CACHE_TTL_SEGUNDOS:
        return cache["historico"]

    historico = cache.get("historico", []) if cache else []
    ultimo_cache = cache.get("ultimo_concurso", 0) if cache else 0

    try:
        ultimo_online = int(baixar_json(URL_CAIXA)["numero"])
    except Exception:
        if historico:
            return historico
        raise

    concursos_existentes = {int(item["concurso"]) for item in historico}

    for concurso in range(1, ultimo_online + 1):
        if concurso in concursos_existentes:
            continue
        try:
            dados = baixar_json(f"{URL_CAIXA}/{concurso}")
            dezenas = dados.get("listaDezenas") or []
            if len(dezenas) == 15:
                dezenas_int = sorted(int(d) for d in dezenas)
                historico.append({
                    "concurso": int(dados.get("numero", concurso)),
                    "data": dados.get("dataApuracao", ""),
                    "dezenas": dezenas_int,
                    "dezenas_formatadas": formatar_dezenas(dezenas_int)
                })
            time.sleep(0.015)
        except Exception:
            continue

    historico = sorted(historico, key=lambda x: int(x["concurso"]))
    salvar_cache({
        "ultimo_concurso": ultimo_online,
        "atualizado_em": agora,
        "historico": historico,
    })
    return historico


def calcular_frequencias(historico):
    c = Counter()
    for item in historico:
        c.update(int(n) for n in item["dezenas"])
    return {n: c[n] for n in range(1, 26)}


def tem_sequencia_maior_que_4(jogo):
    nums = sorted(jogo)
    atual = 1
    maior = 1
    for i in range(1, len(nums)):
        if nums[i] == nums[i - 1] + 1:
            atual += 1
            maior = max(maior, atual)
        else:
            atual = 1
    return maior > 4


def criar_bloqueios_historicos(historico):
    bloqueios_14 = set()
    bloqueios_15 = set()
    for item in historico:
        dezenas = tuple(sorted(int(n) for n in item["dezenas"]))
        bloqueios_15.add(dezenas)
        for grupo in combinations(dezenas, 14):
            bloqueios_14.add(tuple(grupo))
    return bloqueios_14, bloqueios_15


def ja_fez_14_ou_15(jogo, bloqueios_14, bloqueios_15):
    jogo = tuple(sorted(jogo))
    if jogo in bloqueios_15:
        return True
    for grupo in combinations(jogo, 14):
        if tuple(grupo) in bloqueios_14:
            return True
    return False


def validar_numeros(nome, valores, minimo=2, maximo=6):
    if not isinstance(valores, list):
        raise ValueError(f"{nome} deve ser uma lista.")
    if not minimo <= len(valores) <= maximo:
        raise ValueError(f"Escolha de {minimo} a {maximo} dezenas em {nome}.")
    if len(valores) != len(set(valores)):
        raise ValueError(f"Há dezenas repetidas em {nome}.")
    if not set(valores).issubset(TODAS_DEZENAS):
        raise ValueError(f"Todas as dezenas em {nome} precisam estar entre 1 e 25.")


def gerar_jogos(fixos, eliminados, quantidade):
    validar_numeros("fixos", fixos)
    validar_numeros("eliminados", eliminados)
    if set(fixos) & set(eliminados):
        raise ValueError("Uma dezena não pode ser fixa e eliminada ao mesmo tempo.")
    if quantidade < 1 or quantidade > 5000:
        raise ValueError("A quantidade de jogos precisa ficar entre 1 e 5000.")

    historico = carregar_historico()
    frequencias = calcular_frequencias(historico)
    bloqueios_14, bloqueios_15 = criar_bloqueios_historicos(historico)

    fixos_set = set(fixos)
    eliminados_set = set(eliminados)
    livres = sorted(TODAS_DEZENAS - fixos_set - eliminados_set)
    completar = 15 - len(fixos_set)
    total_bruto = comb(len(livres), completar)

    eliminados_sequencia = 0
    eliminados_historico = 0
    aprovados = 0
    heap = []
    contador = 0

    for comp in combinations(livres, completar):
        jogo = sorted(list(fixos_set) + list(comp))
        if tem_sequencia_maior_que_4(jogo):
            eliminados_sequencia += 1
            continue
        if ja_fez_14_ou_15(jogo, bloqueios_14, bloqueios_15):
            eliminados_historico += 1
            continue
        aprovados += 1
        pontuacao = sum(frequencias[n] for n in jogo)
        contador += 1
        item = (pontuacao, contador, jogo)
        if len(heap) < quantidade:
            heapq.heappush(heap, item)
        else:
            if pontuacao > heap[0][0]:
                heapq.heapreplace(heap, item)

    melhores = sorted(heap, key=lambda x: x[0], reverse=True)
    jogos = [{
        "dezenas": jogo,
        "dezenas_formatadas": formatar_dezenas(jogo),
        "pontuacao": pontuacao,
    } for pontuacao, _, jogo in melhores]

    return {
        "jogos": jogos,
        "resumo": {
            "total_bruto": total_bruto,
            "eliminados_por_sequencia": eliminados_sequencia,
            "eliminados_por_historico": eliminados_historico,
            "total_aprovados": aprovados,
            "total_selecionados": len(jogos),
            "concursos_no_historico": len(historico),
            "ultimo_concurso": historico[-1]["concurso"] if historico else None,
        }
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def status():
    historico = carregar_historico()
    return jsonify({
        "ok": True,
        "concursos": len(historico),
        "ultimo": historico[-1] if historico else None,
    })


@app.route("/api/resultados/ultimo")
def resultado_ultimo():
    historico = carregar_historico()
    if not historico:
        return jsonify({"erro": "Histórico vazio"}), 404
    return jsonify(historico[-1])


@app.route("/api/resultados/<int:concurso>")
def resultado_por_concurso(concurso):
    historico = carregar_historico()
    for item in historico:
        if int(item["concurso"]) == concurso:
            return jsonify(item)
    return jsonify({"erro": "Concurso não encontrado"}), 404


@app.route("/api/resultados/ultimos/<int:qtd>")
def ultimos_resultados(qtd):
    qtd = max(1, min(qtd, 100))
    historico = carregar_historico()
    return jsonify(list(reversed(historico[-qtd:])))


@app.route("/api/frequencias")
def frequencias_api():
    historico = carregar_historico()
    freq = calcular_frequencias(historico)
    ranking = [{"dezena": n, "dezena_formatada": str(n).zfill(2), "vezes": freq[n]} for n in range(1, 26)]
    ranking.sort(key=lambda x: x["vezes"], reverse=True)
    return jsonify(ranking)


@app.route("/api/gerar", methods=["POST"])
def gerar_api():
    try:
        data = request.get_json(force=True)
        fixos = [int(x) for x in data.get("fixos", [])]
        eliminados = [int(x) for x in data.get("eliminados", [])]
        quantidade = int(data.get("quantidade", 20))
        return jsonify(gerar_jogos(fixos, eliminados, quantidade))
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
