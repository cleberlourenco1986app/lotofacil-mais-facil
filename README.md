# Lotofacil + Facil - Render v4 sem timeout

Esta versao corrige o timeout do Render Free.

O erro anterior ocorreu porque /api/frequencias tentava carregar todos os concursos um por um.
No Render Free, o worker do Gunicorn estoura tempo.

Agora:
- /api/ultimo consulta rapido
- /api/frequencias usa ultimos 300 concursos por padrao
- /api/frequencias?limite=500 permite aumentar
- /api/gerar usa limite_historico=300 por padrao

## Subir no GitHub

Suba estes arquivos na raiz:
- app.py
- requirements.txt
- Procfile
- render.yaml
- README.md
- .gitignore

## Render

Root Directory: vazio

Build Command:
pip install -r requirements.txt

Start Command:
gunicorn --timeout 120 app:app

Depois:
Manual Deploy > Clear build cache & deploy

## Testes

/api/ultimo
/api/frequencias
/api/frequencias?limite=500

## Observacao

Para usar o historico completo de todos os concursos com boa velocidade, o ideal e salvar os concursos em banco/cache permanente.
