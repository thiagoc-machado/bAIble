# biblia_contexto/indexar_biblia.py

import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

def embed_text(texto):
    emb = model.encode([texto], normalize_embeddings=True)[0]
    return emb

def indexar_versao(idioma, versao):
    print(f'📖 Indexando: {idioma}/{versao}...')
    caminho_json = f'json/{idioma}/{versao}.json'
    with open(caminho_json, 'r', encoding='utf-8-sig') as f:
        dados = json.load(f)

    versiculos = dados['verses']
    embeddings = []
    metadados = []

    for i, v in enumerate(versiculos):
        referencia = f'{v["book_name"]} {v["chapter"]}:{v["verse"]}'
        texto = v['text']
        texto_para_embedding = f'{referencia}: {texto}'
        emb = embed_text(texto_para_embedding)

        embeddings.append(emb)
        metadados.append({
            'id': i,
            'referencia': referencia,
            'texto': texto
        })

    vetor_np = np.array(embeddings).astype('float32')
    index = faiss.IndexFlatL2(vetor_np.shape[1])
    index.add(vetor_np)

    os.makedirs(f'biblia_contexto/indices/{idioma}', exist_ok=True)
    faiss.write_index(index, f'biblia_contexto/indices/{idioma}/{versao}.index')

    with open(f'biblia_contexto/indices/{idioma}/{versao}_metadados.json', 'w', encoding='utf-8') as f:
        json.dump(metadados, f, ensure_ascii=False, indent=2)

    print(f'✅ Indexação finalizada: {len(versiculos)} versículos processados.')

if __name__ == '__main__':
    indexar_versao('pt', 'almeida_ra')
    indexar_versao('en', 'kjv')
    indexar_versao('es', 'rv_1858')
