# biblia_contexto/buscar_contexto.py

import json
import faiss
import torch
import numpy as np
from pathlib import Path
import os
import httpx
from huggingface_hub import hf_hub_download
from transformers import AutoTokenizer, AutoModel
import gc
import tempfile

REPO_ID = os.getenv('HUGGINGFACE_REPO_ID')           # Para o modelo
REPO_INDEX = os.getenv('HUGGINGFACE_REPO_INDEX')     # Para os índices FAISS
TOKEN = os.getenv('HUGGINGFACE_TOKEN')

_cache = {
    'tokenizer': None,
    'model': None,
    'index': None,
    'metadados': None,
}

def get_tokenizer_and_model():
    if _cache['model'] is None or _cache['tokenizer'] is None:
        print('🔄 Carregando modelo remoto do Hugging Face...')
        _cache['tokenizer'] = AutoTokenizer.from_pretrained(REPO_ID, token=TOKEN)
        _cache['model'] = AutoModel.from_pretrained(REPO_ID, torch_dtype=torch.float32, token=TOKEN).eval()
        print(f'📡 Modelo carregado: {REPO_ID}')
        print(f'🔑 Token presente: {"Sim" if TOKEN else "Não"}')
    return _cache['tokenizer'], _cache['model']

def get_index_and_metadados(idioma, versao):
    print('📦 Buscando índice e metadados do Hugging Face...')
    filename_index = f'{idioma}/{versao}.index'
    filename_metadata = f'{idioma}/{versao}_metadados.json'

    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = hf_hub_download(
            repo_id=REPO_INDEX,
            filename=filename_index,
            repo_type='dataset',
            token=TOKEN,
            cache_dir=tmpdir
        )
        metadata_path = hf_hub_download(
            repo_id=REPO_INDEX,
            filename=filename_metadata,
            repo_type='dataset',
            token=TOKEN,
            cache_dir=tmpdir
        )

        index = faiss.read_index(index_path)
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadados = json.load(f)

    return index, metadados

def embed_text(texto):
    url = 'https://thiagocmach-bible-embeddings-api.hf.space/embed'
    headers = {
        'Authorization': f'Bearer {os.getenv("EMBEDDING_API_TOKEN")}',
        'Content-Type': 'application/json'
    }
    try:
        response = httpx.post(url, json={'texto': texto}, headers=headers, timeout=20)
        response.raise_for_status()
        return np.array(response.json()['embedding'], dtype='float32')
    except Exception as e:
        print(f'❌ Erro ao consultar o modelo remoto: {e}')
        return np.zeros(64, dtype='float32')  # fallback

def buscar_contexto(pergunta, idioma='pt', versao='almeida_ra', character='biblia', top_k=5):
    index, metadados = get_index_and_metadados(idioma, versao)
    pergunta_exp = f"According to the Bible, answering strictly as {character}, respond to the message: {pergunta}"
    print('=' * 50)
    print(pergunta_exp)
    print('=' * 50)

    pergunta_emb = embed_text(pergunta_exp).astype('float32').reshape(1, -1)
    distancias, indices = index.search(pergunta_emb, top_k)
    resultados = [metadados[idx] for idx in indices[0]]

    del index, metadados
    gc.collect()

    return resultados
