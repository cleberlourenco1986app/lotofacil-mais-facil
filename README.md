# Lotofacil + Facil - Backend Render

Este pacote esta pronto para subir no GitHub e publicar no Render.

## Arquivos que devem ficar na raiz do repositorio

- app.py
- requirements.txt
- Procfile
- render.yaml
- README.md

## Configuracao no Render

Language: Python 3

Root Directory: deixe em branco

Build Command:
pip install -r requirements.txt

Start Command:
gunicorn app:app

## Depois de publicar

Abra o link do Render. A tela deve mostrar:

{
  "app": "Lotofacil + Facil",
  "status": "online"
}

## Rotas principais

/api/ultimo
/api/concurso/3000
/api/frequencias
/api/gerar

## Importante

Este app e uma ferramenta estatistica independente.
Nao realiza apostas, nao vende boloes e nao garante resultados.
