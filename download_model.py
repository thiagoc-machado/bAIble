from transformers import AutoTokenizer, AutoModel
from pathlib import Path

MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
LOCAL_DIR = Path('biblia_contexto/models/paraphrase-multilingual-MiniLM-L12-v2')

print(f'⬇️ Baixando modelo para: {LOCAL_DIR.resolve()}')

# Cria o diretório se não existir
LOCAL_DIR.mkdir(parents=True, exist_ok=True)

# Baixa e salva o tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.save_pretrained(LOCAL_DIR)

# Baixa e salva o modelo
model = AutoModel.from_pretrained(MODEL_NAME)
model.save_pretrained(LOCAL_DIR)

print('✅ Modelo baixado com sucesso para uso offline.')
