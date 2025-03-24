# Copia o código fonte
COPY . .

# Script de inicialização
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Cria um usuário não-root para segurança
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expõe a porta definida na variável de ambiente
EXPOSE $PORT

# Comando para iniciar o servidor
ENTRYPOINT ["/entrypoint.sh"]
