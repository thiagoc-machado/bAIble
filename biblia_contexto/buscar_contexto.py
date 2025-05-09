# biblia_contexto/buscar_contexto.py

import json
import faiss
import torch
import numpy as np
from pathlib import Path
import os
import httpx
from huggingface_hub import hf_hub_download

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
    print('📦 Buscando índice e metadados do Hugging Face...')
    repo_id = 'thiagocmach/bible-indices'
    filename_index = f'{idioma}/{versao}.index'
    filename_metadata = f'{idioma}/{versao}_metadados.json'

    try:
        index_path = hf_hub_download(repo_id=repo_id, filename=filename_index, repo_type='dataset')
        metadata_path = hf_hub_download(repo_id=repo_id, filename=filename_metadata, repo_type='dataset')
    except Exception as e:
        print(f'❌ Erro ao baixar arquivos do Hugging Face: {e}')
        raise FileNotFoundError('❌ Arquivos de índice ou metadados não encontrados.')

    print(f'🔍 Índice carregado: {filename_index}')
    index = faiss.read_index(index_path)
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadados = json.load(f)

    return index, metadados
# def embed_text(texto):
#     tokenizer, model = get_tokenizer_and_model()
#     inputs = tokenizer(texto, return_tensors='pt', truncation=True, padding=True)

#     with torch.no_grad():
#         outputs = model(**inputs)
#         embeddings = outputs.last_hidden_state
#         mask = inputs['attention_mask'].unsqueeze(-1).expand(embeddings.size())
#         masked_embeddings = embeddings * mask
#         summed = torch.sum(masked_embeddings, dim=1)
#         counted = torch.clamp(mask.sum(1), min=1e-9)
#         mean_pooled = summed / counted
#         return mean_pooled[0].cpu().numpy()

def embed_text(texto):
    url = 'https://thiagocmach-bible-embeddings-api.hf.space/embed'
    headers = {
        'Authorization': f'Bearer {os.getenv("EMBEDDING_API_TOKEN")}',
        'Content-Type': 'application/json'
    }
    try:
        response = httpx.post(url, json={'texto': texto}, headers=headers, timeout=10)
        response.raise_for_status()
        return np.array(response.json()['embedding'], dtype='float32')
    except Exception as e:
        print(f'❌ Erro ao consultar o modelo remoto: {e}')
        return np.zeros(384, dtype='float32')  # fallback

def buscar_contexto(pergunta, idioma='pt', versao='almeida_ra', character='biblia', top_k=5):
    index, metadados = get_index_and_metadados(idioma, versao)
    # 📌 Incluímos o personagem como o destinatário da pergunta para contextualizar a busca
    pergunta_exp = f'Baseado na Bíblia, como {character} responderia à pergunta: {pergunta}?'
    print(50*'=')
    print(f'{pergunta_exp}')
    print(50*'=')
    pergunta_emb = embed_text(pergunta_exp).astype('float32').reshape(1, -1)
    distancias, indices = index.search(pergunta_emb, top_k)
    return [metadados[idx] for idx in indices[0]]
