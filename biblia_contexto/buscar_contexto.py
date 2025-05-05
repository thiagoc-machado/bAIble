# biblia_contexto/buscar_contexto.py

import json
import faiss
import torch
import numpy as np
from pathlib import Path
from transformers import AutoTokenizer, AutoModel
import os

REPO_ID = os.getenv('HUGGINGFACE_REPO_ID')
TOKEN = os.getenv('HUGGINGFACE_TOKEN')

_cache = {
    'tokenizer': None,
    'model': None,
    'index': None,
    'metadados': None,
}

REPO_ID = os.getenv('HUGGINGFACE_REPO_ID', 'thiagocmach/paraphrase-pt-bible')

def get_tokenizer_and_model():
    if _cache['model'] is None or _cache['tokenizer'] is None:
        print('🔄 Carregando modelo remoto do Hugging Face...')
        _cache['tokenizer'] = AutoTokenizer.from_pretrained(REPO_ID, token=TOKEN)
        _cache['model'] = AutoModel.from_pretrained(REPO_ID, torch_dtype=torch.float32, token=TOKEN).eval()
        print(f'📡 Usando REPO_ID: {REPO_ID}')
        print(f'🔑 Token presente: {"Sim" if TOKEN else "Não"}')
    return _cache['tokenizer'], _cache['model']

def get_index_and_metadados(idioma, versao):
    if _cache['index'] is None or _cache['metadados'] is None:
        print('📦 Carregando índice FAISS e metadados locais...')
        index_path = f'biblia_contexto/indices/{idioma}/{versao}.index'
        print(f'🔍 Usando índice: {index_path}')
        metadata_path = f'biblia_contexto/indices/{idioma}/{versao}_metadados.json'

        if not Path(index_path).exists() or not Path(metadata_path).exists():
            raise FileNotFoundError('❌ Arquivos de índice ou metadados não encontrados.')

        _cache['index'] = faiss.read_index(index_path, faiss.IO_FLAG_MMAP)
        with open(metadata_path, 'r', encoding='utf-8') as f:
            _cache['metadados'] = json.load(f)
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
