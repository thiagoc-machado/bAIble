import pickle
import json
import os

INPUT_PKL = 'embeddings/biblia_en_kjv_embeddings.pkl'
OUTPUT_JSON = 'public/embeddings/biblia_en_kjv_embeddings.json'

with open(INPUT_PKL, 'rb') as f:
    dados = pickle.load(f)

# Remove o numpy (converter para list)
for item in dados:
    if hasattr(item['embedding'], 'tolist'):
        item['embedding'] = item['embedding'].tolist()

os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)

with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(dados, f, ensure_ascii=False, indent=2)

print(f'✅ Convertido: {OUTPUT_JSON}')
