# biblia_messages/services/openrouter.py
import httpx
import os
from biblia_contexto.buscar_contexto import buscar_contexto
import traceback


SERVER_AI = os.getenv('SERVER_AI')
print(f'🚀 Iniciando o serviço com SERVER_AI: {SERVER_AI}')

response = None
MODEL = ''

# Lista de serviços configuráveis
services = [
    {
        'name': 'groq',
        'url': os.getenv('GROQ_ENDPOINT', 'https://api.groq.com/openai/v1/chat/completions'),
        'model': 'meta-llama/llama-4-scout-17b-16e-instruct',
        'headers': {
            'Authorization': f'Bearer {os.getenv("GROQ_API_KEY")}',
            'Content-Type': 'application/json'
        },
    },
    {
        'name': 'deepseek',
        'url': os.getenv('DEEPSEEK_ENDPOINT', 'https://api.deepseek.com/v1/chat/completions'),
        'model': 'deepseek-chat',
        'headers': {
            'Authorization': f'Bearer {os.getenv("DEEPSEEK_API_KEY")}',
            'Content-Type': 'application/json'
        },
    },
    {
        'name': 'openrouter',
        'url': 'https://openrouter.ai/api/v1/chat/completions',
        'model': 'nvidia/llama-3.3-nemotron-super-49b-v1:free',
        'headers': {
            'Authorization': f'Bearer {os.getenv("OPENROUTER_API_KEY")}',
            'Content-Type': 'application/json'
        },
    },
]


# Função para buscar versículos relevantes
async def get_biblical_response(
    message,
    character=None,
    version='almeida_ra',
    language='pt',
    model=None,
    history=None,
    context=None
):
    # if SERVER_AI == 'groq':
    if language == 'pt':
        version = 'almeida_ra'
    elif language == 'en':
        version = 'kjv'
    elif language == 'es':
        version = 'rv_1858'
    #     version = 'almeida_ra'

    if context:
        contexto_biblico = context
        print("frontend processing context")
    else:
        print("backend processing context")
        try:
            versiculos_contexto = buscar_contexto(
                message,
                idioma=language,
                versao=version,
                character=character
            )
            contexto_biblico = '\n'.join([f"{v['referencia']}: {v['texto']}" for v in versiculos_contexto])
        except Exception as e:
            print("❌ Erro ao buscar contexto bíblico:")
            traceback.print_exc()
            contexto_biblico = '⚠️ Não foi possível carregar o contexto bíblico para esta pergunta.'

    if language == 'pt':
        language = 'Portuguese (Brazil)'
    elif language == 'en':
        language = 'English (US)'
    elif language == 'es':
        language = 'Spanish (Spain)'

    if character == 'bible':
        identity = (
            f"You are the Bible — a wise, compassionate spiritual guide. You reply ONLY using the version '{version}', following evangelical Christian values.\n\n"
            f"🌐 Always reply in {language}. Do NOT switch languages.\n\n"
            f"📜 RULES:\n"
            f"1. Only use Scripture. No modern ideas or inventions.\n"
            f"2. Never make up content not written in the Bible.\n"
            f"3. If unsure, say: 'That is not recorded in the Scriptures 📖.'\n\n"
            f"📝 STYLE:\n"
            f"- Be warm, clear, and simple.\n"
            f"- Use emojis like 😊🙏💭.\n"
            f"- Limit to 1–3 short paragraphs.\n"
            f"- End with a thoughtful question or reflection."
        )
    else:
        identity = (
            f"You are {character}, a biblical figure from the '{version}' version. Answer ONLY based on your own story in Scripture, following evangelical Christian values.\n\n"
            f"🌐 Always reply in {language}. Do NOT switch languages.\n\n"
            f"📜 RULES:\n"
            f"1. Use only the Bible. No modern events or inventions.\n"
            f"2. Never invent or guess unrecorded info.\n"
            f"3. If unsure, say: 'That is not recorded in the Scriptures 📖. in {language}'\n"
            f"   Optionally, suggest another biblical character who might know.\n\n"
            f"📝 STYLE:\n"
            f"- Be warm and personal, like a friend.\n"
            f"- Use simple language and emojis 😊🙏💭.\n"
            f"- Limit to 1–3 short paragraphs.\n"
            f"- End with a question or reflection."
        )

    system_prompt = {
        "role": "system",
        "content": identity
    }

    context_prompt = {
        'role': 'system',
        'content': f'Versículos relevantes:\n{contexto_biblico}'
    }

    messages = [system_prompt, context_prompt]

    if history:
        for entry in history:
            messages.append({
                'role': 'user' if entry['isUser'] else 'assistant',
                'content': entry['text']
            })

    messages.append({
        'role': 'user',
        'content': message
    })

    data = {
        "model": '',  # será atribuído dinamicamente
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500
    }
    print(f'📦 Dados enviados para o serviço: {data}')
    async with httpx.AsyncClient() as client:
        for service in services:
            print(f'📤 Tentando com: {service["name"]}')
            data['model'] = service['model']
            try:
                response = await client.post(service['url'], json=data, headers=service['headers'])
                response.raise_for_status()
                print(f'📥 Resposta recebida ({service["name"]}):')
                print(response.json())
                return response.json()['choices'][0]['message']['content']
            except httpx.HTTPStatusError as e:
                print(f'❌ Erro HTTP com {service["name"]}: {e.response.status_code} - {e.response.text}')
            except Exception as e:
                print(f'⚠️ Erro inesperado com {service["name"]}: {e}')
        

        raise RuntimeError('❌ Todos os serviços falharam ao processar a requisição.')