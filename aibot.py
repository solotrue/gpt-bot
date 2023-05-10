import openai
from config import OPENAI_API_KEY, MODEL_ENGINE, MODEL_TOKENS, MODEL_TEMPERATURE


def generate_response(chat_id, message_text, context_items=None):
    context = ''
    if context_items:
        # Combine all previous messages and responses into one string, separated by newlines
        if isinstance(context_items, str):
            # Convert string to list of dictionaries
            context_items = [{'message': context_items, 'response': ''}]
        context = '\n'.join([f"User: {item['message']}\nBot: {item['response']}" for item in context_items]) + '\n'

    # Add the current message text to the end of the context
    prompt = context + f"User: {message_text}\nBot:"

    response = openai.Completion.create(
        engine=MODEL_ENGINE,
        prompt=prompt,
        max_tokens=MODEL_TOKENS,
        temperature=MODEL_TEMPERATURE,
    )

    text = response.choices[0].text.strip()

    return text


class Aibot:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY
