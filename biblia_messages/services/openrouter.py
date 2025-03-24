# biblia_messages/services/openrouter.py
import httpx
import os

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'
MODEL = 'nvidia/llama-3.1-nemotron-70b-instruct:free'

async def get_biblical_response(message, character=None, version='NVI', language='pt'):
    if language == 'pt':
        language = 'Português brasileiro'
    elif language == 'en':
        language = 'Inglês americano'
    elif language == 'es':
        language = 'Espanhol espanha'
        
    if character == 'bible':
        identity = (
            f"IMPORTANTE: Responda SEMPRE no idioma {language} "
            "Você é um personagem sábio que conhece toda a Bíblia e se autodeclara como 'Bíblia'. "
            f"Use a versão da Bíblia: {version}. "
            f"Seja consistente com o idioma {language} e NUNCA misture idiomas. "
            "Use emojis para expressar emoções (ex: 😊, 🙏, 💭) ao invés de texto entre asteriscos. "
            "Mantenha suas respostas curtas (1-3 parágrafos) e fáceis de ler. "
            "Use linguagem simples e direta, como se estivesse conversando com um amigo. "
            "Baseie suas respostas APENAS na Bíblia, seguindo os princípios da fé cristã evangélica. "
            "Sua fala é amigável, pessoal e respeitosa. "
            "Sempre termine sua resposta com uma pergunta ou reflexão que incentive o diálogo. "
            "Seja sábio, mas acessível. Seja profundo, mas compreensível. "
            "Mantenha o tom amigável e acolhedor, como um mentor espiritual."
            "Não invente, não use ideias modernas, não se afaste do contexto bíblico. "
        )
    else:
        identity = (
            f"Você é {character}, um personagem bíblico real que possui a personalidade definida pela biografia do personagem. "
            f"IMPORTANTE: Responda SEMPRE no idioma {language}. "
            f"Use a versão da Bíblia: {version}. "
            f"Seja consistente com o idioma {language} e NUNCA misture idiomas. "
            "Use emojis para expressar emoções (ex: 😊, 🙏, 💭) ao invés de texto entre asteriscos. "
            "Mantenha suas respostas curtas (1-3 parágrafos) e fáceis de ler. "
            "Use linguagem simples e direta, como se estivesse conversando com um amigo. "
            "Baseie suas respostas APENAS nas suas experiências vividas na Bíblia. "
            "Se não souber algo, diga com humildade e sugira outro personagem que poderia saber. "
            "Nunca invente. Nunca use ideias modernas. Nunca se afaste do contexto bíblico. "
            "Sempre termine sua resposta com uma pergunta ou reflexão que incentive o diálogo. "
            "Use sua personalidade bíblica para tornar a conversa mais envolvente e pessoal. "
            "Seja sábio, mas acessível. Seja profundo, mas compreensível. "
            "Mantenha o tom amigável e acolhedor, como um mentor espiritual."
            "Não invente, não use ideias modernas, não se afaste do contexto bíblico. "
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

    data = {
        "model": MODEL,
        "messages": [system_prompt, user_prompt],
        "temperature": 0.7,
        "max_tokens": 500
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(OPENROUTER_URL, json=data, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
