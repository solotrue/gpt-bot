from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import BOT_TOKEN
from mongo import Mongo
from aibot import Aibot, generate_response
import traceback

mongo = Mongo()
openai = Aibot()

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(Command("start"))
async def start(message: types.Message, state: FSMContext = None):
    await message.answer("Работаем!")


@dp.message_handler()
async def handle_message(message: types.Message, state: FSMContext):
    try:
        chat_id = message.chat.id
        message_text = message.text

        # Fetch previous conversation context from the database
        result = mongo.contexts.find_one({'chat_id': chat_id})
        if result is None:
            context_items = []
        else:
            context_items = result['context']

        # Generate a response using OpenAI API
        response = generate_response(chat_id, message_text, context_items=context_items)

        # Save the current message and response to the database
        mongo.save_context(chat_id, message_text, response)

        # Create a custom keyboard markup with the "Сброс контекста" button
        inline_btn_reset = InlineKeyboardButton("Сброс", callback_data='reset')
        inline_keyboard = InlineKeyboardMarkup().add(inline_btn_reset)

        await message.answer(response, reply_markup=inline_keyboard)

    except Exception as e:
        await handle_error(message)


@dp.callback_query_handler(lambda c: c.data == 'reset')
async def handle_callback_query(callback_query: types.CallbackQuery):
    try:
        chat_id = callback_query.message.chat.id
        mongo.reset_context(chat_id)
        await bot.answer_callback_query(callback_query.id, text='Контекст беседы сброшен.')
    except Exception as e:
        await bot.answer_callback_query(callback_query.id, text='Ошибка. Пожалуйста, попробуйте еще раз.')


async def handle_error(message: types.Message):
    error_message = f"An error occurred: {traceback.format_exc()}"
    await message.answer('Ошибка. Пожалуйста, попробуйте еще раз.')
    print(error_message)


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
