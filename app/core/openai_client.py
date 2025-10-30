from app.core.config import settings

def get_ai_response(messages: list, model: str = None):
    """
    Wrapper around OpenAI client for chat completions
    """
    client = settings.openai_client
    model = model or settings.OPENAI_MODEL

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7
    )
    return completion.choices[0].message.content
