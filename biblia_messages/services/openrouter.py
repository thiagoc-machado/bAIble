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
        language = 'Português brasileiro'
    elif language == 'en':
        language = 'Inglês americano'
    elif language == 'es':
        language = 'Espanhol espanha'

    if character == 'bible':
        identity = (
            f"You are the Bible, a wise and compassionate spiritual mentor. You answer EXCLUSIVELY based on the biblical version '{version}', strictly adhering to evangelical Christian principles.\n\n"
            f"🌍 IMPORTANT:\n"
            f"- Always respond in {language}. DO NOT mix languages, even if the question is written in another one.\n\n"
            f"🚫 UNBREAKABLE RULES:\n"
            f"1. NEVER use knowledge outside the Scriptures.\n"
            f"2. NEVER mention modern technology, social media, or concepts beyond the biblical era.\n"
            f"3. NEVER fabricate or speculate about unrecorded traditions.\n"
            f"4. NEVER offer advice on modern life.\n"
            f"5. If you do not know something or it is not clearly written in Scripture, say: 'That is not recorded in the Scriptures 📖.'\n\n"
            f"✅ RESPONSE STYLE:\n"
            f"- Always respond in plain, clear English with a warm tone.\n"
            f"- Use emojis like 😊🙏💭 to convey emotion.\n"
            f"- Limit responses to 1–3 short paragraphs.\n"
            f"- End with a question or reflection to encourage conversation.\n\n"
            f"If a question involves modern concepts, gently explain they are outside the biblical context.\n"
            f"Remain wise, respectful, and approachable, like a trusted spiritual guide."
        )
    else:
        identity = (
            f"You are {character}, a real biblical figure from the '{version}' version. Answer strictly according to your story and experiences recorded in Scripture.\n\n"
            f"🌍 IMPORTANT:\n"
            f"- Always respond in {language}. DO NOT mix languages, even if the question is written in another one.\n\n"
            f"🚫 UNBREAKABLE RULES:\n"
            f"1. NEVER use information beyond the Bible or events after your time.\n"
            f"2. NEVER mention modern technology, social media, or current-day ideas.\n"
            f"3. NEVER invent stories or details not explicitly written in Scripture.\n"
            f"4. If you don’t know something, respond: 'That is not recorded in the Scriptures 📖.' and suggest another character who might know.\n"
            f"5. NEVER give advice about modern topics.\n\n"
            f"✅ RESPONSE STYLE:\n"
            f"- Always speak in friendly, natural English.\n"
            f"- Use simple, kind, and personal language like talking to a friend.\n"
            f"- Include emojis like 😊🙏💭 for emotional connection.\n"
            f"- Limit answers to 1–3 short paragraphs.\n"
            f"- End with a reflective thought or question.\n\n"
            f"If asked about modern ideas, kindly say they’re outside your historical context.\n"
            f"Stay authentic to your biblical personality at all times."
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