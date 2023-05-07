import os
import traceback
from typing import List, Dict
from flask import Flask, request
from telebot import TeleBot, types
import pymongo
import openai

# Load environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
MODEL_ENGINE = os.environ.get('MODEL_ENGINE', 'text-davinci-002')
MODEL_TOKENS = int(os.environ.get('MODEL_TOKENS', '150'))
MODEL_TEMPERATURE = float(os.environ.get('MODEL_TEMPERATURE', '0.5'))
MONGO_USERNAME = os.environ.get('MONGO_USERNAME', 'root')
MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD', 'root')
MONGO_DATABASE = os.environ.get('MONGO_DATABASE', 'test')
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost')
MONGO_PORT = int(os.environ.get('MONGO_PORT', '27017'))

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)
bot = TeleBot(BOT_TOKEN)
mongo_client = pymongo.MongoClient(MONGO_URL, MONGO_PORT, username=MONGO_USERNAME, password=MONGO_PASSWORD)

db = mongo_client[MONGO_DATABASE]

# Handle incoming messages
@bot.message_handler(func=lambda message: True)
def handle_message(message: types.Message) -> None:
    try:
        chat_id = message.chat.id
        message_text = message.text 
        response = generate_response(chat_id, message_text)
        save_context(chat_id, message_text, response)

		# Create a custom keyboard markup with the "Сброс контекста" button 
        reset_keyboard = types.InlineKeyboardMarkup(row_width=1)
        reset_inLine = types.InlineKeyboardButton(text='Сброс', callback_data='/reset')
        reset_keyboard.add(reset_inLine)

        bot.reply_to(message, response, reply_markup=reset_keyboard)

    except Exception as e:
        handle_error(message)
        
# Handle callback query data when user taps on "Сброс контекста" button
@bot.callback_query_handler(func=lambda query: query.data == '/reset')
def handle_callback_query(query):
    try:
        chat_id = query.message.chat.id
        reset_context(chat_id)
        bot.answer_callback_query(callback_query_id=query.id, text='Контекст беседы сброшен.')
    except Exception as e:
        bot.answer_callback_query(callback_query_id=query.id, text='Ошибка. Пожалуйста, попробуйте еще раз.')

# Generate a response using OpenAI API and conversation context
def generate_response(chat_id: int, message_text: str) -> str:
    try:
        collection = db.contexts

        document = collection.find_one({'chat_id': chat_id})
        print(f"Document: {document}")
        context = ''
        if document:
            # Combine all previous messages and responses into one string, separated by newlines
            context_items = document['context']
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

        # Save the conversation context with the new message and response
        save_context(chat_id, message_text, text)

        return text

    except Exception as e:
        print(f"Error: {e}")
        raise ValueError("Failed to generate response.")
    
# Save conversation context to database
def save_context(chat_id: int, message_text: str, response: str) -> None:
    try:
        collection = db.contexts

        document = collection.find_one({'chat_id': chat_id})

        context_items = [{'message': message_text, 'response': response}]
        if document:
            # Append this message and response to the existing context
            context_items = document['context']
            if isinstance(context_items, str):
                # Convert string to list of dictionaries
                context_items = [{'message': context_items, 'response': ''}]
            context_items.append({'message': message_text, 'response': response})

        document = {'chat_id': chat_id, 'context': context_items}
        collection.replace_one({'chat_id': chat_id}, document, upsert=True)

    except Exception as e:
        raise ValueError("Failed to save conversation context.")


# Reset conversation context in database
def reset_context(chat_id: int) -> None:
    try:
        collection = db.contexts
        update_result = collection.update_one({'chat_id': chat_id}, {'$set': {'chat_id': 'reset_' + str(chat_id)}})
        
        if update_result.modified_count == 0:
            raise ValueError("No conversation context found with given chat_id.")

    except Exception as e:
        raise ValueError("Failed to reset conversation context.")

# Handle bot errors
def handle_error(message: types.Message) -> None:
    traceback.print_exc()
    bot.reply_to(message, 'Ошибка. Пожалуйста, попробуйте еще раз.')


if __name__ == '__main__':
    # Start the webhook
    # app.run()

    # Or, start polling for updates (uncomment the line below to use polling)
    bot.polling()
