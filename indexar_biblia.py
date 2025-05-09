# biblia_contexto/indexar_biblia.py

import json
import os
import faiss
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from tqdm import tqdm

# Carrega modelo E5
tokenizer = AutoTokenizer.from_pretrained('intfloat/e5-large-v2')
model = AutoModel.from_pretrained('intfloat/e5-large-v2').eval()

def embed_text(texto):
    texto = 'passage: ' + texto.strip()  # obrigatório para o modelo e5
    inputs = tokenizer(texto, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        emb = outputs.last_hidden_state
        mask = inputs['attention_mask'].unsqueeze(-1).expand(emb.size())
        masked = emb * mask
        summed = masked.sum(1)
        counted = mask.sum(1)
        mean_pooled = (summed / counted).squeeze().cpu().numpy()
        return mean_pooled

def indexar_versao(idioma, versao):
    print(f'📖 Indexando: {idioma}/{versao}...')
    caminho_json = f'json/{idioma}/{versao}.json'
    with open(caminho_json, 'r', encoding='utf-8-sig') as f:
        dados = json.load(f)

    versiculos = dados['verses']
    embeddings = []
    metadados = []

    for i, v in enumerate(tqdm(versiculos, desc="🔍 Processando versículos")):
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

    os.makedirs(f'indices/bible-indices/{idioma}', exist_ok=True)
    faiss.write_index(index, f'indices/bible-indices/{idioma}/{versao}.index')

    with open(f'indices/bible-indices/{idioma}/{versao}_metadados.json', 'w', encoding='utf-8') as f:
        json.dump(metadados, f, ensure_ascii=False, indent=2)

    print(f'✅ Indexação finalizada: {len(versiculos)} versículos processados.')

if __name__ == '__main__':
    indexar_versao('pt', 'almeida_ra')
    # indexar_versao('en', 'kjv')
    # indexar_versao('es', 'rv_1858')
