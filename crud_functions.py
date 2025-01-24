import sqlite3


def initiate_db():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL         
        )
    ''')
    connection.commit()


def add_product(prod_id, title, description, price):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    check_product = cursor.execute("SELECT * FROM Products WHERE id=?", (prod_id,))

    if check_product.fetchone() is None:
        cursor.execute(f'''
    INSERT INTO Products VALUES('{prod_id}', '{title}', '{description}', '{price}')
''')
    connection.commit()


def get_all_products():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    all_prod = cursor.execute("SELECT * FROM Products").fetchall()
    connection.commit()
    connection.close()
    return all_prod


# initiate_db()

add_product(1, "Витамин А", "Полезная штука", 100)
add_product(2, "Глютамин", "Аминокислота", 200)
add_product(3, "Омега-3", "Полезная штука №2", 300)
add_product(4, "Протеин", "Полезная штука для мышечной массы", 400)