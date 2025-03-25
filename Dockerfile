# Imagem base oficial do Python
FROM python:3.10-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Atualiza pip
RUN pip install --upgrade pip

# Copia requirements e instala dependências Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante da aplicação
COPY . /app/

# Dá permissão ao script de entrada
RUN chmod +x /app/entrypoint.sh

# Cria usuário não-root e troca para ele
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expondo a porta
EXPOSE $PORT

# Comando de entrada
ENTRYPOINT ["/app/entrypoint.sh"]
