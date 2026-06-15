services:
  - type: web
    name: lotofacil-mais-facil
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
