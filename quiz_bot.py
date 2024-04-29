import aiosqlite
from aiogram import types, Dispatcher
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
from command import Command
import json
import database

# Function to generate keyboard for quiz options
def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()
    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )
    builder.adjust(1)
    return builder.as_markup()

# Function to start a new quiz
async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await database.update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)

# Function to get and display a quiz question
async def get_question(message, user_id):
    with open('quiz_data.json', 'r', encoding='utf-8') as file:
        quiz_data = json.load(file)

    current_question_index = await database.get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

# Handler for the quiz command
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)

# Handler for the statistics command
async def cmd_statistics(message: types.Message):
    statistics = await get_quiz_statistics()
    await message.answer(statistics)

# Function to get quiz statistics from the database
async def get_quiz_statistics():
    async with aiosqlite.connect(database.DB_NAME) as db:
        async with db.execute('SELECT COUNT(user_id) AS total_players, MAX(question_index) AS max_score FROM quiz_state') as cursor:
            result = await cursor.fetchone()
            if result:
                total_players, max_score = result
                return f"Total players: {total_players}\nMax score: {max_score}"
            else:
                return "No statistics available."

# Registering handlers and commands
def setup(dp: Dispatcher):
    dp.register_message_handler(new_quiz, Command("quiz"), F.text == "Начать игру")
    dp.register_message_handler(cmd_statistics, Command("stats"))
    dp.register_message_handler(cmd_statistics, Command("help"))