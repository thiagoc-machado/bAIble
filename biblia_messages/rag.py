import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Inicializa o modelo uma única vez
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Busca versículos relevantes com base na pergunta, versão e idioma
def buscar_versiculos_relevantes(pergunta, idioma, versao, top_n=5):
    # Monta o caminho do arquivo com base no idioma e versão
    file_name = f'biblia_{idioma}_{versao}_embeddings.pkl'
    file_path = os.path.join('embeddings', file_name)  # crie a pasta 'embeddings' para salvar todos

    # Carrega o arquivo .pkl correspondente
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'Arquivo de embeddings não encontrado: {file_path}')

    with open(file_path, 'rb') as f:
        versos_indexados = pickle.load(f)

    # 🧠 Gera o embedding da pergunta
    pergunta_emb = model.encode(pergunta)

    # Calcula a similaridade com todos os versículos
    resultados = []
    for item in versos_indexados:
        sim = cosine_similarity([pergunta_emb], [item['embedding']])[0][0]
        resultados.append((sim, item))

    # Seleciona os top N mais relevantes
    top_resultados = sorted(resultados, key=lambda x: x[0], reverse=True)[:top_n]

    # Retorna os trechos (texto + referência)
    trechos = [f"{item['referencia']}: {item['texto']}" for _, item in top_resultados]
    return trechos
