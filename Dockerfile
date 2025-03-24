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

# Copia os arquivos de requisitos
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte
COPY . .

# Coleta arquivos estáticos
RUN python manage.py collectstatic --noinput

# Expõe a porta definida na variável de ambiente
EXPOSE $PORT

# Comando para iniciar o servidor
CMD gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT 