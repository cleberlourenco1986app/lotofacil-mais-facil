# Lotofacil + Facil - Backend Render

Versao v3 com 3 fontes de resultado:

1. Caixa
2. Guidi
3. Loterias Caixa API Heroku

Se uma fonte falhar, o backend tenta a proxima.

## Subir no GitHub

Suba estes arquivos na raiz do repositorio:

- app.py
- requirements.txt
- Procfile
- render.yaml
- README.md
- .gitignore

## Render

Root Directory: deixe em branco

Build Command:
pip install -r requirements.txt

Start Command:
gunicorn app:app

Depois use:
Manual Deploy > Clear build cache & deploy

## Testes

/api/ultimo
/api/concurso/3000
/api/frequencias
