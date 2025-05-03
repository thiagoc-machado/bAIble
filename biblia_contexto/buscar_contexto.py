# biblia_contexto/buscar_contexto.py

import json
import time
import faiss
import numpy as np
from pathlib import Path
import torch

# Armazena recursos em cache com controle de tempo
_cache = {
    'model': None,
    'index': None,
    'metadados': None,
    'last_used': 0
}

TIMEOUT = 10  # 2 minutos de inatividade


def unload_after_timeout():
    if time.time() - _cache['last_used'] > TIMEOUT:
        print('⏳ Tempo de inatividade excedido. Liberando memória...')
        _cache['model'] = None
        _cache['index'] = None
        _cache['metadados'] = None
        torch.cuda.empty_cache()


def get_model():
    if _cache['model'] is None:
        print('🔄 Carregando modelo de embeddings...')
        from sentence_transformers import SentenceTransformer
        _cache['model'] = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    _cache['last_used'] = time.time()
    return _cache['model']


def get_index_and_metadados(idioma, versao):
    if _cache['index'] is None or _cache['metadados'] is None:
        print('📦 Carregando índice FAISS e metadados...')
        index_path = f'biblia_contexto/indices/{idioma}/{versao}.index'
        metadata_path = f'biblia_contexto/indices/{idioma}/{versao}_metadados.json'

        if not Path(index_path).exists() or not Path(metadata_path).exists():
            raise FileNotFoundError('❌ Arquivos de índice ou metadados não encontrados.')

        _cache['index'] = faiss.read_index(index_path, faiss.IO_FLAG_MMAP)
        with open(metadata_path, 'r', encoding='utf-8') as f:
            _cache['metadados'] = json.load(f)
    _cache['last_used'] = time.time()
    return _cache['index'], _cache['metadados']


def embed_text(texto):
    model = get_model()
    return model.encode([texto], normalize_embeddings=True)[0]


def buscar_contexto(pergunta, idioma='pt', versao='almeida_rc', top_k=5):
    index, metadados = get_index_and_metadados(idioma, versao)

    pergunta_exp = f'O que a Bíblia diz sobre: {pergunta}'
    pergunta_emb = embed_text(pergunta_exp).astype('float32').reshape(1, -1)

    distancias, indices = index.search(pergunta_emb, top_k)
    return [metadados[idx] for idx in indices[0]]

__all__ = ['buscar_contexto', '_cache', 'TIMEOUT']