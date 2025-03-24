# Use uma imagem oficial do Python
FROM python:3.10-slim

# Define variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8000

# Define o diretório de trabalho
WORKDIR /app

# Instala as dependências do sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas os arquivos de requisitos primeiro
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte
COPY . .

# Cria um usuário não-root para segurança
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Coleta arquivos estáticos
RUN python manage.py collectstatic --noinput

# Expõe a porta definida na variável de ambiente
EXPOSE $PORT

# Script de inicialização
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Comando para iniciar o servidor
ENTRYPOINT ["/entrypoint.sh"] 