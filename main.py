import psycopg2


def create_db(conn):
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS phones (
            id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL,
            phone TEXT NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    ''')
    conn.commit()


def add_client(conn, first_name, last_name, email, phones=None):

    cur = conn.cursor()
    cur.execute('INSERT INTO clients (first_name, last_name, email) VALUES (%s, %s, %s) RETURNING id',
                (first_name, last_name, email))
    client_id = cur.fetchone()[0]
    if phones:
        for phone in phones:
            add_phone(conn, client_id, phone)
    conn.commit()


def add_phone(conn, client_id, phone):
    cur = conn.cursor()
    cur.execute('INSERT INTO phones (client_id, phone) VALUES (%s, %s)', (client_id, phone))
    conn.commit()


def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    cur = conn.cursor()
    if first_name:
        cur.execute('UPDATE clients SET first_name = %s WHERE id = %s', (first_name, client_id))
    if last_name:
        cur.execute('UPDATE clients SET last_name = %s WHERE id = %s', (last_name, client_id))
    if email:
        cur.execute('UPDATE clients SET email = %s WHERE id = %s', (email, client_id))
    if phones:
        cur.execute('DELETE FROM phones WHERE client_id = %s', (client_id,))
        for phone in phones:
            add_phone(conn, client_id, phone)
    conn.commit()


def delete_phone(conn, client_id, phone):
    cur = conn.cursor()
    cur.execute('DELETE FROM phones WHERE client_id = %s AND phone = %s', (client_id, phone))
    conn.commit()


def delete_client(conn, client_id):
    cur = conn.cursor()
    cur.execute('DELETE FROM phones WHERE client_id = %s', (client_id,))
    cur.execute('DELETE FROM clients WHERE id = %s', (client_id,))
    conn.commit()


def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    cur = conn.cursor()
    if first_name:
        cur.execute('SELECT * FROM clients WHERE first_name = %s', (first_name,))
    elif last_name:
        cur.execute('SELECT * FROM clients WHERE last_name = %s', (last_name,))
    elif email:
        cur.execute('SELECT * FROM clients WHERE email = %s', (email,))
    elif phone:
        cur.execute('''
            SELECT c.* FROM clients c
            JOIN phones p ON c.id = p.client_id
            WHERE p.phone = %s
        ''', (phone,))
    else:
        return None
    return cur.fetchone()

with psycopg2.connect(database="test", user="test", password="test") as conn:
    create_db(conn)

    # Добавление клиента
    add_client(conn, 'Иван', 'Иванов', 'test@example.ru', ['1234567890', '9876543210'])

    # Обновление данных
    change_client(conn, 1, surname='Петров')

    # Удаление телефона
    delete_phone(conn, 1, '1234567890')

    # Удаление клиента
    delete_client(conn, 1)

    # Поиск клиента
    print(find_client(conn, first_name='Иван'))  # (1, 'Иван', 'Иванов', 'test@example.ru')
    print(find_client(conn, phone='9876543210'))  # (1, 'Иван', 'Иванов', 'test@example.ru')

conn.close()