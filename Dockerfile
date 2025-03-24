# Copia o código fonte
COPY . .

# Permissões no entrypoint já copiado anteriormente
RUN chmod +x /app/entrypoint.sh

# Cria usuário não-root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expõe porta
EXPOSE $PORT

# Comando de inicialização
ENTRYPOINT ["/app/entrypoint.sh"]

