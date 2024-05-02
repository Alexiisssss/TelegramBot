import aiosqlite

DB_NAME = 'quiz_bot.db'

# В функции создания таблицы базы данных добавим создание таблицы quiz_score
async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_score (user_id INTEGER PRIMARY KEY, score INTEGER)''')  # Добавим таблицу quiz_score
        await db.commit()

async def get_quiz_index(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def update_quiz_index(user_id, index):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        await db.commit()


async def count_players():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT COUNT(*) FROM quiz_state') as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def get_max_score():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT MAX(question_index) FROM quiz_state') as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0


# Функция для обновления количества правильных ответов игрока
async def update_quiz_score(user_id, username, score):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_score (user_id, username, score) VALUES (?, ?, ?)', (user_id, username, score))
        await db.commit()

# Функция для получения количества правильных ответов определенного игрока
async def get_player_score(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT score FROM quiz_score WHERE user_id = (?)', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0


# Функция для получения результатов каждого игрока
async def get_player_scores():
    player_scores = {}
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT user_id, username, score FROM quiz_score') as cursor:
            async for row in cursor:
                user_id, username, score = row
                player_scores[username] = score  # Используем имя пользователя в качестве ключа
    return player_scores


async def create_user_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)''')
        await db.commit()

async def insert_user(user_id, username):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
        await db.commit()


async def get_username(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT username FROM users WHERE user_id = (?)', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None


