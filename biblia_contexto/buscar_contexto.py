# biblia_contexto/buscar_contexto.py

import json
import time
import faiss
import torch
import numpy as np
from pathlib import Path
from transformers import AutoTokenizer, AutoModel

_cache = {
    'tokenizer': None,
    'model': None,
    'index': None,
    'metadados': None,
    'last_used': 0
}

TIMEOUT = 120  # segundos


def unload_after_timeout():
    if time.time() - _cache['last_used'] > TIMEOUT:
        print('⏳ Tempo de inatividade excedido. Liberando memória...')
        _cache['model'] = None
        _cache['tokenizer'] = None
        _cache['index'] = None
        _cache['metadados'] = None
        torch.cuda.empty_cache()


def get_tokenizer_and_model():
    unload_after_timeout()
    if _cache['model'] is None or _cache['tokenizer'] is None:
        print('🔄 Carregando modelo de embeddings com float16...')
        path = 'biblia_contexto/models/paraphrase-multilingual-MiniLM-L12-v2'
        _cache['tokenizer'] = AutoTokenizer.from_pretrained(path)
        _cache['model'] = AutoModel.from_pretrained(path, torch_dtype=torch.float16).eval()
    _cache['last_used'] = time.time()
    return _cache['tokenizer'], _cache['model']


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
    tokenizer, model = get_tokenizer_and_model()
    inputs = tokenizer(texto, return_tensors='pt', truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state
        mask = inputs['attention_mask'].unsqueeze(-1).expand(embeddings.size())
        masked_embeddings = embeddings * mask
        summed = torch.sum(masked_embeddings, dim=1)
        counted = torch.clamp(mask.sum(1), min=1e-9)
        mean_pooled = summed / counted
        return mean_pooled[0].cpu().numpy()


def buscar_contexto(pergunta, idioma='pt', versao='almeida_rc', top_k=5):
    index, metadados = get_index_and_metadados(idioma, versao)
    pergunta_exp = f'O que a Bíblia diz sobre: {pergunta}'
    pergunta_emb = embed_text(pergunta_exp).astype('float32').reshape(1, -1)
    distancias, indices = index.search(pergunta_emb, top_k)
    return [metadados[idx] for idx in indices[0]]
