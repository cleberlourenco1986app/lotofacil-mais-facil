services:
  - type: web
    name: lotofacil-mais-facil
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
