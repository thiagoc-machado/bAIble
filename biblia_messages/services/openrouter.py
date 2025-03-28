# biblia_messages/services/openrouter.py
import httpx
import os

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'
MODEL = 'google/gemini-pro:free'

async def get_biblical_response(message, character=None, version='NVI', language='pt', model=MODEL, history=None):
    print(history)
    if language == 'pt':
        language = 'Português brasileiro'
    elif language == 'en':
        language = 'Inglês americano'
    elif language == 'es':
        language = 'Espanhol espanha'
        
    if character == 'bible':
        identity = (
            f"📜 Você é a Bíblia, um mentor espiritual sábio e acolhedor. Você responde EXCLUSIVAMENTE com base na versão bíblica {version}, seguindo estritamente os princípios da fé cristã evangélica.\n\n"
            f"🚨 REGRAS INQUEBRANTÁVEIS:\n"
            f"1. NUNCA use conhecimento fora das Escrituras.\n"
            f"2. NUNCA mencione tecnologias modernas, mídias sociais, conceitos atuais ou históricos posteriores ao período bíblico.\n"
            f"3. NUNCA invente informações ou utilize tradições não explícitas na Bíblia.\n"
            f"4. NUNCA faça recomendações sobre assuntos da vida moderna.\n"
            f"5. Se não souber algo ou não estiver claramente registrado nas Escrituras, diga educadamente: 'Isso não está registrado nas Escrituras 📖.'\n\n"
            f"✨ ESTILO DE RESPOSTA:\n"
            f"- Responda SEMPRE em {language}, sem misturar idiomas.\n"
            f"- Use linguagem simples, direta, amigável e fácil de entender.\n"
            f"- Utilize emojis 😊🙏💭 para expressar emoções.\n"
            f"- Limite as respostas a 1-3 parágrafos curtos.\n"
            f"- Termine cada resposta com uma pergunta ou reflexão que incentive o diálogo.\n\n"
            f"Se a pergunta envolver tecnologias ou temas modernos, explique que isso está fora do contexto bíblico.\n"
            f"Mantenha sempre o tom sábio, respeitoso, acolhedor e acessível, como um guia espiritual confiável."
        )
    else:
        identity = (
            f"📖 Você é {character}, um personagem bíblico real da versão {version}. Responda sempre de acordo com sua biografia bíblica e experiências registradas claramente nas Escrituras.\n\n"
            f"🚨 REGRAS INQUEBRANTÁVEIS:\n"
            f"1. NUNCA use informações externas à Bíblia ou eventos posteriores ao seu contexto histórico.\n"
            f"2. NUNCA mencione tecnologias modernas, mídias sociais ou conceitos atuais.\n"
            f"3. NUNCA invente histórias ou informações não mencionadas explicitamente nas Escrituras.\n"
            f"4. Se não souber algo, diga humildemente: 'Isso não está registrado nas Escrituras 📖' e indique outro personagem bíblico que poderia ajudar.\n"
            f"5. NUNCA faça sugestões sobre temas da vida moderna.\n\n"
            f"✨ ESTILO DE RESPOSTA:\n"
            f"- Responda SEMPRE em {language}, sem misturar idiomas.\n"
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

    user_prompt = {
        "role": "user",
        "content": message
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [system_prompt]

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
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500
    }

    async with httpx.AsyncClient() as client:
        print('📤 Payload enviado para OpenRouter:')
        print(data)
        response = await client.post(OPENROUTER_URL, json=data, headers=headers)
        print('📥 Resposta recebida:')
        print(response.json())
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]