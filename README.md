# Lotofacil + Facil - Backend Render

Versao corrigida para o erro 403 da Caixa no Render.

O backend tenta consultar a API da Caixa primeiro.
Se a Caixa bloquear o servidor com 403, ele usa a API alternativa:
https://api.guidi.dev.br/loteria/lotofacil

## Arquivos que devem ficar na raiz do repositorio

- app.py
- requirements.txt
- Procfile
- render.yaml
- README.md
- .gitignore

## Configuracao no Render

Root Directory: deixe em branco

Build Command:
pip install -r requirements.txt

Start Command:
gunicorn app:app

## Depois de publicar

Teste:

/api/ultimo
/api/concurso/3000
/api/frequencias

## Importante

Este app e uma ferramenta estatistica independente.
Nao realiza apostas, nao vende boloes e nao garante resultados.
