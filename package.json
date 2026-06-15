let fixos = new Set();
let eliminados = new Set();
let ultimosJogos = [];

const qs = s => document.querySelector(s);
const qsa = s => [...document.querySelectorAll(s)];
const dezenas = Array.from({length:25},(_,i)=>i+1);
const fmt = n => String(n).padStart(2,'0');

qsa('.tab').forEach(btn=>btn.addEventListener('click',()=>{
  qsa('.tab').forEach(b=>b.classList.remove('active'));
  qsa('.panel').forEach(p=>p.classList.remove('active'));
  btn.classList.add('active');
  qs('#tab-'+btn.dataset.tab).classList.add('active');
  if(btn.dataset.tab==='salvos') renderSalvos();
}));

function gridHTML(sorteadas=[], extraClass={}){
  const s = new Set(sorteadas.map(Number));
  return `<div class="mini-grid">${dezenas.map(n=>{
    let cls='ball';
    if(s.has(n)) cls += ' drawn';
    if(extraClass[n]) cls += ' '+extraClass[n];
    return `<span class="${cls}">${fmt(n)}</span>`;
  }).join('')}</div>`;
}

function dezenasBadges(nums){
  return `<div class="badges">${nums.map(n=>`<span class="badge">${fmt(n)}</span>`).join('')}</div>`;
}

function criarSelecaoGrid(id, tipo){
  const el = qs(id);
  el.innerHTML = dezenas.map(n=>`<button class="ball" data-num="${n}" type="button">${fmt(n)}</button>`).join('');
  el.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>toggleNumero(Number(b.dataset.num),tipo)));
  atualizarGrids();
}

function toggleNumero(n,tipo){
  if(tipo==='fixo'){
    if(fixos.has(n)) fixos.delete(n);
    else {
      if(eliminados.has(n)) return alert('Essa dezena está eliminada. Remova de eliminados primeiro.');
      if(fixos.size>=6) return alert('Máximo de 6 fixos.');
      fixos.add(n);
    }
  } else {
    if(eliminados.has(n)) eliminados.delete(n);
    else {
      if(fixos.has(n)) return alert('Essa dezena está fixa. Remova de fixos primeiro.');
      if(eliminados.size>=6) return alert('Máximo de 6 eliminados.');
      eliminados.add(n);
    }
  }
  atualizarGrids();
}

function atualizarGrids(){
  qs('#countFixos').textContent = fixos.size;
  qs('#countEliminados').textContent = eliminados.size;
  qsa('#gridFixos .ball').forEach(b=>b.classList.toggle('fixed',fixos.has(Number(b.dataset.num))));
  qsa('#gridEliminados .ball').forEach(b=>b.classList.toggle('out',eliminados.has(Number(b.dataset.num))));
}

async function api(url, opts={}){
  const base = (window.LOTOFACIL_API_BASE || '').replace(/\/$/, '');
  const finalUrl = url.startsWith('http') ? url : base + url;
  const r = await fetch(finalUrl, opts);
  const data = await r.json();
  if(!r.ok) throw new Error(data.erro || 'Erro na requisição');
  return data;
}

async function atualizarStatus(){
  qs('#status').textContent = 'Carregando histórico...';
  if(!window.LOTOFACIL_API_BASE){ qs('#status').innerHTML = 'Configure o link do backend no arquivo <b>mobile/www/config.js</b> antes de publicar o app.'; return; }
  try{
    const s = await api('/api/status');
    qs('#status').innerHTML = `Histórico carregado: <b>${s.concursos}</b> concursos. Último: <b>${s.ultimo.concurso}</b> em ${s.ultimo.data}.`;
  }catch(e){ qs('#status').textContent = 'Erro ao carregar histórico: '+e.message; }
}

function renderResultado(item, target){
  qs(target).innerHTML = `<div class="result-card"><h3>Concurso ${item.concurso}</h3><p class="muted">${item.data||''}</p>${gridHTML(item.dezenas)}<p><b>Sorteados:</b> ${item.dezenas_formatadas.join(' ')}</p></div>`;
}
async function carregarUltimo(){ try{ renderResultado(await api('/api/resultados/ultimo'),'#resultadoAtual'); }catch(e){alert(e.message)} }
async function buscarConcurso(){ const n=Number(qs('#concursoBusca').value); if(!n)return alert('Digite o concurso.'); try{ renderResultado(await api('/api/resultados/'+n),'#resultadoAtual'); }catch(e){alert(e.message)} }
async function carregarUltimos(){ const qtd=Number(qs('#qtdUltimos').value)||5; try{ const arr=await api('/api/resultados/ultimos/'+qtd); qs('#ultimosResultados').innerHTML=arr.map(item=>`<div class="result-card"><b>Concurso ${item.concurso}</b><p class="muted">${item.data||''}</p>${gridHTML(item.dezenas)}<p>${item.dezenas_formatadas.join(' ')}</p></div>`).join(''); }catch(e){alert(e.message)} }

async function carregarRanking(){
  qs('#rankingArea').innerHTML='Carregando...';
  try{
    const r=await api('/api/frequencias');
    const max=Math.max(...r.map(x=>x.vezes));
    qs('#rankingArea').innerHTML=r.map(x=>`<div class="rank-row"><b>${x.dezena_formatada}</b><div class="bar"><span style="width:${(x.vezes/max)*100}%"></span></div><span>${x.vezes}</span></div>`).join('');
  }catch(e){qs('#rankingArea').textContent=e.message}
}

async function gerarJogos(){
  if(fixos.size<2) return alert('Escolha pelo menos 2 fixos.');
  if(eliminados.size<2) return alert('Escolha pelo menos 2 eliminados.');
  const quantidade=Number(qs('#quantidadeJogos').value)||20;
  qs('#resumoGeracao').classList.remove('hidden');
  qs('#resumoGeracao').innerHTML='Gerando jogos...';
  qs('#jogosGerados').classList.add('hidden');
  try{
    const data=await api('/api/gerar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({fixos:[...fixos],eliminados:[...eliminados],quantidade})});
    ultimosJogos=data.jogos;
    const r=data.resumo;
    qs('#resumoGeracao').innerHTML=`<h2>Resumo</h2><p>Total bruto: <b>${r.total_bruto}</b></p><p>Eliminados por sequência maior que 4: <b>${r.eliminados_por_sequencia}</b></p><p>Eliminados por histórico 14/15: <b>${r.eliminados_por_historico}</b></p><p>Aprovados: <b>${r.total_aprovados}</b> | Selecionados: <b>${r.total_selecionados}</b></p>`;
    qs('#jogosGerados').classList.remove('hidden');
    qs('#jogosGerados').innerHTML=`<h2>Jogos gerados</h2><div class="row wrap"><button onclick="salvarTodosGerados()">Salvar todos</button><button class="secondary" onclick="baixarCSV()">Baixar CSV</button></div>${data.jogos.map((j,i)=>renderJogo(j,i,true)).join('')}`;
  }catch(e){qs('#resumoGeracao').innerHTML='Erro: '+e.message;}
}

function renderJogo(j,i,comSalvar=false, resultado=null){
  let acertos='';
  let extra={};
  if(resultado){
    const s=new Set(resultado.map(Number));
    const hit=j.dezenas.filter(n=>s.has(n));
    hit.forEach(n=>extra[n]='hit');
    acertos=`<span class="badge">Acertos: ${hit.length}</span>`;
  }
  return `<div class="game"><div class="game-main"><b>Jogo ${String(i+1).padStart(3,'0')}</b> ${acertos}<p>${j.dezenas_formatadas.join(' ')}</p>${gridHTML(j.dezenas, extra)}<span class="badge">Pontuação: ${j.pontuacao||0}</span></div>${comSalvar?`<button class="secondary" onclick="salvarUm(${i})">Salvar</button>`:''}</div>`;
}

function getSalvos(){ return JSON.parse(localStorage.getItem('jogosSalvosLotofacilMaisFacil')||'[]'); }
function setSalvos(v){ localStorage.setItem('jogosSalvosLotofacilMaisFacil',JSON.stringify(v)); }
function salvarUm(i){ const salvos=getSalvos(); salvos.push({...ultimosJogos[i], salvoEm:new Date().toLocaleString('pt-BR')}); setSalvos(salvos); alert('Jogo salvo.'); }
function salvarTodosGerados(){ const salvos=getSalvos(); ultimosJogos.forEach(j=>salvos.push({...j,salvoEm:new Date().toLocaleString('pt-BR')})); setSalvos(salvos); alert(`${ultimosJogos.length} jogos salvos.`); }
function renderSalvos(){ const salvos=getSalvos(); qs('#salvosArea').innerHTML=salvos.length?salvos.map((j,i)=>renderJogo(j,i,false)).join(''):'Nenhum jogo salvo ainda.'; }
function limparSalvos(){ if(confirm('Apagar todos os jogos salvos neste aparelho?')){setSalvos([]);renderSalvos();} }
async function conferirSalvos(){
  const n=Number(qs('#concursoConferencia').value); if(!n)return alert('Digite o concurso.');
  const salvos=getSalvos(); if(!salvos.length)return alert('Nenhum jogo salvo.');
  try{
    const res=await api('/api/resultados/'+n);
    qs('#salvosArea').innerHTML=`<div class="result-card"><h3>Conferindo com concurso ${res.concurso}</h3>${gridHTML(res.dezenas)}<p>${res.dezenas_formatadas.join(' ')}</p></div>`+salvos.map((j,i)=>renderJogo(j,i,false,res.dezenas)).join('');
  }catch(e){alert(e.message)}
}
function baixarCSV(){
  if(!ultimosJogos.length)return;
  const linhas=['Jogo;Dezenas;Pontuacao',...ultimosJogos.map((j,i)=>`${i+1};${j.dezenas_formatadas.join(' ')};${j.pontuacao}`)];
  const blob=new Blob([linhas.join('\n')],{type:'text/csv;charset=utf-8'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='jogos_lotofacil_mais_facil.csv'; a.click(); URL.revokeObjectURL(a.href);
}

criarSelecaoGrid('#gridFixos','fixo');
criarSelecaoGrid('#gridEliminados','eliminado');
atualizarStatus();
carregarUltimo();
