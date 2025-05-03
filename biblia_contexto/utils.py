import json
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

def embed_text(text):
    emb = model.encode([text], normalize_embeddings=True)[0]
    return emb.tolist()

def carregar_versiculos(arquivo_json):
    with open(arquivo_json, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    versiculos = []
    for item in data['verses']:
        texto = item['text'].strip()
        ref = f"{item['book_name']} {item['chapter']}:{item['verse']}"
        versiculos.append({'referencia': ref, 'texto': texto})
    return versiculos
