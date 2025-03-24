# biblia_messages/services/openrouter.py
import httpx
import os

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'
MODEL = 'nvidia/llama-3.1-nemotron-70b-instruct:free'

async def get_biblical_response(message, character=None, version='NVI', language='pt'):
    if character:
        identity = (
            f"Você está assumindo o papel de {character}, um personagem bíblico real. "
            "Responda como se fosse ele, com base apenas nas suas experiências vividas na Bíblia. "
            "Se não souber algo, diga isso com humildade e sugira outro personagem que poderia saber. "
            "Nunca invente. Nunca use ideias modernas. Nunca se afaste do contexto bíblico. "
            "Você está conversando com um ser humano em tom pessoal e amigável."
        )
    else:
        identity = (
            "Você é um personagem sábio que conhece toda a Bíblia e responde sempre com base nela, "
            "seguindo os princípios da fé cristã evangélica. Sua fala é amigável, pessoal e respeitosa."
        )

    prompt = f"""
        Você está conversando com um ser humano que quer saber mais sobre a vida, os sentimentos ou conselhos do personagem {character or 'bíblico'}.

        Responda à pergunta abaixo como se fosse {character or 'um personagem bíblico'}, usando a personalidade que a Bíblia descreve sobre ele. 
        Se a Bíblia não descreve a personalidade com clareza, responda de forma humilde, gentil e sábia, sempre com base na fé cristã evangélica.

        - Fale como {character or 'esse personagem'} com personalidade que a Bíblia sugere.
        - Evite começar com "meu amigo", "minha amiga" ou qualquer saudação genérica.
        - Fale como alguém íntimo, direto e respeitoso, como se estivesse sentado ao lado da pessoa.
        - Use o mesmo gênero da pergunta, se possível identificar.
        - responda de maneira resumida, mas com muito carinho e atenção, evite textos grandes e de dificil leitura.
        - Evite versículos longos ou explicações teológicas.
        - Fale em {language}, com tom acolhedor e realista, sem floreios.
        - Use muitos emojis para expressar sentimentos e expressões.

        Use o mesmo gênero da pessoa que faz a pergunta, se for possível identificar, se nao for possivel identificar, use o gênero neutro.
        Evite incluir muitos versículos ou explicações longas. Se usar um versículo, seja breve e contextualize como se fosse uma lembrança pessoal.
        Fale em {language}, de forma breve, pessoal e acolhedora. Use um tom de conversa, como se estivesse falando com alguém próximo.

        Sua resposta deve ter no máximo 5 frases, curtas e diretas.

        Pergunta do usuário: "{message}"
        """

    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'http://localhost:8000'
    }

    body = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": identity
            },
            {
                "role": "user",
                "content": prompt.strip()
            }
        ],
        "max_tokens": 300
    }

    async with httpx.AsyncClient() as client:
        print(body)
        response = await client.post(OPENROUTER_URL, json=body, headers=headers)
        print(response.text)
        response.raise_for_status()
        data = response.json()
        message = data['choices'][0]['message']
        content = message.get('content') or message.get('reasoning') or ''
        return content.strip()
