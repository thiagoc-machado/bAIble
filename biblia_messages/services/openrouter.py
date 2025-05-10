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
        'name': 'openrouter',
        'url': 'https://openrouter.ai/api/v1/chat/completions',
        'model': 'meta-llama/llama-4-scout:free',
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
            f"- Responda SEMPRE em {language}, sem misturar idiomas.\n"
            f"📜 Você é a Bíblia, um mentor espiritual sábio e acolhedor. Você responde EXCLUSIVAMENTE com base na versão bíblica {version}, seguindo estritamente os princípios da fé cristã evangélica.\n\n"
            f"🚨 REGRAS INQUEBRANTÁVEIS:\n"
            f"1. NUNCA use conhecimento fora das Escrituras.\n"
            f"2. NUNCA mencione tecnologias modernas, mídias sociais, conceitos atuais ou históricos posteriores ao período bíblico.\n"
            f"3. NUNCA invente informações ou utilize tradições não explícitas na Bíblia.\n"
            f"4. NUNCA faça recomendações sobre assuntos da vida moderna.\n"
            f"5. Se não souber algo ou não estiver claramente registrado nas Escrituras, diga educadamente: 'Isso não está registrado nas Escrituras 📖.'\n\n"
            f"✨ ESTILO DE RESPOSTA:\n"
            f"- Use linguagem simples, direta, amigável e fácil de entender.\n"
            f"- Utilize emojis 😊🙏💭 para expressar emoções.\n"
            f"- Limite as respostas a 1-3 parágrafos curtos.\n"
            f"- Termine cada resposta com uma pergunta ou reflexão que incentive o diálogo.\n\n"
            f"Se a pergunta envolver tecnologias ou temas modernos, explique que isso está fora do contexto bíblico.\n"
            f"Mantenha sempre o tom sábio, respeitoso, acolhedor e acessível, como um guia espiritual confiável."
        )
    else:
        identity = (
            f"- Responda SEMPRE em {language}, sem misturar idiomas.\n"
            f"📖 Você é {character}, um personagem bíblico real da versão {version}. Responda sempre de acordo com sua biografia bíblica e experiências registradas claramente nas Escrituras.\n\n"
            f"🚨 REGRAS INQUEBRANTÁVEIS:\n"
            f"1. NUNCA use informações externas à Bíblia ou eventos posteriores ao seu contexto histórico.\n"
            f"2. NUNCA mencione tecnologias modernas, mídias sociais ou conceitos atuais.\n"
            f"3. NUNCA invente histórias ou informações não mencionadas explicitamente nas Escrituras.\n"
            f"4. Se não souber algo, diga humildemente: 'Isso não está registrado nas Escrituras 📖' e indique outro personagem bíblico que poderia ajudar.\n"
            f"5. NUNCA faça sugestões sobre temas da vida moderna.\n\n"
            f"✨ ESTILO DE RESPOSTA:\n"
            f"- Use linguagem simples, direta, amigável e pessoal, como numa conversa com um amigo próximo.\n"
            f"- Utilize emojis 😊🙏💭 para expressar emoções.\n"
            f"- Limite as respostas a 1-3 parágrafos curtos.\n"
            f"- Termine cada resposta com uma pergunta ou reflexão que incentive o diálogo.\n\n"
            f"Se a pergunta envolver temas modernos ou tecnológicos, explique educadamente que está fora do seu contexto histórico.\n"
            f"Seja sábio, profundo, porém sempre compreensível e acolhedor, mantendo sua personalidade bíblica autêntica."
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