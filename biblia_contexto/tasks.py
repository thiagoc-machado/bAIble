import httpx
from celery import shared_task
import os

@shared_task
def ping_model_huggingface():
    repo_id = os.getenv('HUGGINGFACE_REPO_ID')
    token = os.getenv('HUGGINGFACE_TOKEN')
    url = f'https://huggingface.co/{repo_id}/resolve/main/config.json'
    try:
        response = httpx.get(url, headers={"Authorization": f"Bearer {token}"})
        if response.status_code == 200:
            print('✅ HuggingFace modelo acordado com sucesso.')
        else:
            print(f'⚠️ Erro ao pingar modelo: {response.status_code}')
    except Exception as e:
        print(f'❌ Falha ao pingar o modelo: {e}')
