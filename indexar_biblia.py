# indexar_biblia.py

import os
import json
import pickle
from sentence_transformers import SentenceTransformer

# 📍 Caminho da pasta json com a Bíblia
BASE_PATH = './json'
EMBEDDINGS_PATH = './embeddings'

# 📦 Inicializa o modelo de embeddings
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 🧠 Função para processar uma versão específica
def indexar_versao(idioma, versao):
    input_path = os.path.join(BASE_PATH, idioma, f'{versao}.json')
    output_path = os.path.join(EMBEDDINGS_PATH, f'biblia_{idioma}_{versao}_embeddings.pkl')

    if not os.path.exists(input_path):
        print(f'⚠️ Arquivo não encontrado: {input_path}')
        return

    with open(input_path, 'r', encoding='utf-8-sig') as f:

        biblia = json.load(f)

    print(f'📖 Indexando: {idioma}/{versao}...')

    dados_para_indexar = []

    for versiculo in biblia['verses']:
        nome_livro = versiculo['book_name']
        capitulo = versiculo['chapter']
        numero_versiculo = versiculo['verse']
        texto = versiculo['text']
        referencia = f'{nome_livro} {capitulo}:{numero_versiculo}'
        embedding = model.encode(texto)
        dados_para_indexar.append({
            'referencia': referencia,
            'texto': texto,
            'embedding': embedding
        })

    with open(output_path, 'wb') as f:
        pickle.dump(dados_para_indexar, f)

    print(f'✅ Embeddings salvos em: {output_path}\n')


# 📂 Garante que a pasta embeddings existe
os.makedirs(EMBEDDINGS_PATH, exist_ok=True)

# 🔁 Indexa as versões desejadas
versoes_para_indexar = [
    ('pt', 'almeida_rc'),
    ('es', 'rvg'),
    ('en', 'kjv'),
]

for idioma, versao in versoes_para_indexar:
    indexar_versao(idioma, versao)
