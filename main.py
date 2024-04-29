import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F
import json
from aiogram.enums import ParseMode


from database import create_table, update_quiz_index, get_quiz_index, count_players, get_max_score

logging.basicConfig(level=logging.INFO)

API_TOKEN = 'YOUR_API'

bot = Bot(token=API_TOKEN)


dp = Dispatcher()

DB_NAME = 'quiz_bot.db'

total_correct_answers = 0

with open('quiz_data.json', 'r', encoding='utf-8') as file:
    quiz_data = json.load(file)


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()


@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    global total_correct_answers
    total_correct_answers += 1
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_question_index = await get_quiz_index(callback.from_user.id)
    user_answer = quiz_data[current_question_index]['options'][quiz_data[current_question_index]['correct_option']]

    await callback.message.answer(f"Ваш ответ: {user_answer}")
    await callback.message.answer("Верно!")
    await callback.message.answer(f"Следующий вопрос:")

    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    user_answer = quiz_data[current_question_index]['options'][correct_option]
    correct_answer = quiz_data[current_question_index]['options'][correct_option]

    await callback.message.answer("Неверно")
    await callback.message.answer(f"Правильный ответ: {correct_answer}")
    await callback.message.answer(f"Следующий вопрос:")

    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        total_questions = len(quiz_data)
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен!\n\n"
                                      f"Вы ответили верно на {total_correct_answers} из {total_questions} вопросов.")


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    if current_question_index < len(quiz_data):
        correct_index = quiz_data[current_question_index]['correct_option']
        opts = quiz_data[current_question_index]['options']
        kb = generate_options_keyboard(opts, opts[correct_index])
        await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)
    else:
        await message.answer("Это был последний вопрос. Квиз завершен!")

async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)


@dp.message(F.text == "Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)

@dp.message(Command("stats"))
async def cmd_statistics(message: types.Message):
    statistics = await get_statistics()
    await message.answer(statistics)

async def get_statistics():
    total_players = await count_players()
    max_score = await get_max_score()
    return f"Статистика игроков:\n\nВсего игроков: {total_players}\nМаксимальное количество правильных ответов: {max_score}"

@dp.message(Command("help"))
async def show_all_commands(message: types.Message):
    await show_all_commands_info(message)

async def show_all_commands_info(message: types.Message):
    with open('commands.md', 'r', encoding='utf-8') as file:
        commands_info = file.read()
    await message.answer(commands_info, parse_mode=ParseMode.MARKDOWN)


async def main():
    await create_table()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
