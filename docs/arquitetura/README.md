# Arquitetura

O front-end (`frontend/`, publicado na Vercel) consulta a API Java (`backend/java/`, publicada no Render), que lê o banco Oracle da FIAP (`database/`); as alternativas de trajeto são calculadas antes pelo módulo `dynamic-programming/`.
