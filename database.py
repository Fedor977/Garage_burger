import sqlite3


database = sqlite3.connect('fastfood.db')
cursor = database.cursor()

def create_users_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        telegram_id INTEGER NOT NULL UNIQUE,
        phone_number INTEGER NOT NULL
    )
    ''')




def create_cart_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS carts(
        cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(user_id) UNIQUE,
        total_products INTEGER DEFAULT 0,
        total_price DECIMAL(12, 2) DEFAULT 0
    )
    ''')


def create_cart_products_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart_products(
        cart_product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cart_id INTEGER REFERENCES carts(cart_id),
        product_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        final_price DECIMAL(12, 2) NOT NULL,
        product_id INTEGER NOT NULL,
        
        UNIQUE(cart_id, product_name)
    )
    ''')


def create_user_location():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS locations(
    user_id INTEGER REFERENCES users(user_id),
    latitude TEXT NOT NULL,
    longitude  TEXT NOT NULL,
    description TEXT NOT NULL
    )
    
    ''')


create_user_location()
create_users_table()
create_cart_table()
create_cart_products_table()






database.commit()
database.close()




