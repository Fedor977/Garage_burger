import sqlite3

async def get_users_count():
    database = sqlite3.connect("fastfood.db")
    cursor = database.cursor()

    cursor.execute("""
    SELECT count(telegram_id) FROM users;
    """)
    count = cursor.fetchone()[0]
    database.close()
    return count


async def get_all_users():
    database = sqlite3.connect("fastfood.db")
    cursor = database.cursor()
    cursor.execute("""
    SELECT telegram_id FROM users;
    """)
    users = cursor.fetchall()

    users = [user[0] for user in users]
    return users



