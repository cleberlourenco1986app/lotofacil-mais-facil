BACKEND ONLINE DO LOTOFAQCIL BINHO

Este backend deve ser publicado primeiro, porque o app Android usa este servidor para:
- consultar resultados;
- calcular frequencias;
- gerar jogos;
- filtrar historico.

Publicacao no Render:
1. Crie conta em https://render.com
2. Crie um novo Web Service.
3. Envie a pasta backend para um repositorio GitHub ou use o projeto completo.
4. Configure:
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
5. Depois do deploy, copie a URL publica, exemplo:
   https://lotofacil-mais-facil.onrender.com
6. Cole essa URL em mobile/www/config.js.

Observacao: nao coloque barra no final da URL.
