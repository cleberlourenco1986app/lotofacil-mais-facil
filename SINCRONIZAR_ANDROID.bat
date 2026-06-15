<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Lotofácil + Fácil</title>
  <link rel="stylesheet" href="static/style.css" />
</head>
<body>
  <div class="shell">
    <header class="hero">
      <div>
        <p class="eyebrow">Gerador inteligente</p>
        <h1>Lotofácil + Fácil</h1>
        <p>Resultados coloridos, filtros, geração de jogos e conferência direto no celular.</p>
      </div>
      <button class="ghost" onclick="atualizarStatus()">Atualizar</button>
    </header>

    <section id="status" class="status-card">Carregando histórico...</section>

    <nav class="tabs">
      <button class="tab active" data-tab="resultados">Resultados</button>
      <button class="tab" data-tab="gerar">Gerar</button>
      <button class="tab" data-tab="salvos">Salvos</button>
      <button class="tab" data-tab="ranking">Ranking</button>
    </nav>

    <main>
      <section class="panel active" id="tab-resultados">
        <div class="card">
          <h2>Resultado do sorteio</h2>
          <div class="row wrap">
            <button onclick="carregarUltimo()">Ver último</button>
            <input id="concursoBusca" type="number" placeholder="Concurso" />
            <button class="secondary" onclick="buscarConcurso()">Buscar</button>
          </div>
          <div id="resultadoAtual" class="result-box"></div>
        </div>
        <div class="card">
          <h2>Últimos resultados</h2>
          <div class="row">
            <input id="qtdUltimos" type="number" value="5" min="1" max="100" />
            <button onclick="carregarUltimos()">Listar</button>
          </div>
          <div id="ultimosResultados" class="list"></div>
        </div>
      </section>

      <section class="panel" id="tab-gerar">
        <div class="card">
          <h2>Montar matriz</h2>
          <p class="hint">Escolha de 2 a 6 fixos e de 2 a 6 eliminados. Clique nas dezenas para selecionar.</p>
          <h3>Fixos <span id="countFixos">0</span>/6</h3>
          <div id="gridFixos" class="number-grid"></div>
          <h3>Eliminados <span id="countEliminados">0</span>/6</h3>
          <div id="gridEliminados" class="number-grid"></div>
          <div class="row wrap topgap">
            <label>Quantidade de jogos</label>
            <input id="quantidadeJogos" type="number" value="20" min="1" max="5000" />
            <button onclick="gerarJogos()">Gerar jogos</button>
          </div>
        </div>
        <div id="resumoGeracao" class="card hidden"></div>
        <div id="jogosGerados" class="card hidden"></div>
      </section>

      <section class="panel" id="tab-salvos">
        <div class="card">
          <h2>Jogos salvos</h2>
          <div class="row wrap">
            <input id="concursoConferencia" type="number" placeholder="Concurso para conferir" />
            <button onclick="conferirSalvos()">Conferir</button>
            <button class="danger" onclick="limparSalvos()">Limpar salvos</button>
          </div>
          <div id="salvosArea" class="list"></div>
        </div>
      </section>

      <section class="panel" id="tab-ranking">
        <div class="card">
          <h2>Dezenas mais sorteadas</h2>
          <button onclick="carregarRanking()">Carregar ranking</button>
          <div id="rankingArea" class="ranking"></div>
        </div>
      </section>
    </main>
  </div>
  <script src="config.js"></script>
  <script src="static/app.js"></script>
</body>
</html>
