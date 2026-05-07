# Импортируем библиотеки
import sqlite3


# Создаём базу данных
db = sqlite3.connect('inventory_con.db')
cursor = db.cursor()

# Начальное  кол-во товара
amount = 0


# Создаём функцию - обработчика ошибок
def ask_int(question):
    while True:
        try:
            amount = int(input(question))
            return amount
        except:
            print('Ошибка! Введите число!')     




# Создаём таблицу inventory
cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
               id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
               item_name TEXT UNIQUE NOT NULL,
               quantity BIGINT,
               price INTEGER,
               category_id INTEGER)'''
)



# Создаём таблицу categories
cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
               id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
               category_name TEXT NOT NULL)'''
)



# Запрашиваем у пользователя название товара
product = input('Название товара:\n')


# Есть ли этот товар в базе
cursor.execute('''SELECT item_name FROM inventory WHERE item_name = ?''', (product,))
result_name = cursor.fetchone()


# В зависимости от условия выполняем действия
if result_name:
    # Сначала узнаём, сколько было (достаём из ячейки [0])
    cursor.execute('''SELECT quantity FROM inventory WHERE item_name = ?''', (product,))
    old_quantity = cursor.fetchone()[0]

    # Обработка ошибки
    new_amount = ask_int('Сколько единиц прибыло?\n')

    # Обновляем в базе
    cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE item_name = ?", (new_amount, product))
    # Считаем и выводим итог
    total = old_quantity + new_amount
    print(f'Запасы обновлены. Теперь на складе: {total} шт.')
else:
    # Запрашиваем у пользователя категорию
    category_ans = input('Введите название категории:\n')

    # Находим id этой категории
    cursor.execute("SELECT id FROM categories WHERE category_name = ?", (category_ans,))
    category_result = cursor.fetchone()

    # Если категории нет - добавляем, иначе - берём id этой категории
    if category_result == None:
        # Добавляем название этой категории в таблицу
        cursor.execute("INSERT INTO categories (category_name) VALUES (?)", (category_ans,))
        # Записываем айди этой категории в переменную
        category_ans_id = cursor.lastrowid
    else:
        category_ans_id = category_result[0]

        # Обработка ошибки
        amount = ask_int('Количество товара:\n')

    # Обработка ошибки
        cost = ask_int('Цена:\n')

    cursor.execute('''INSERT INTO inventory (item_name, quantity, price, category_id) VALUES (?, ?, ?, ?)''',
                    (product, amount, cost, category_ans_id))
    print(f'Товар {product} добавлен. Общая стоимость на складе: {cost * amount}')




# Находим все товары, где кол-во меньше 5
cursor.execute('''SELECT item_name, quantity FROM inventory WHERE quantity < 5''')
# Список коробок
min_result = cursor.fetchall()

if min_result:
    print('Внимание! Заканчиваются товары:')

# Берем по очереди каждую "коробку" из списка найденных
for tovar in min_result:
    print('- Название:', tovar[0], '| осталось:', tovar[1], 'шт.')


# Объединяем таблицы и показыввем результат
cursor.execute('''SELECT inventory.item_name, categories.category_name 
FROM inventory
JOIN categories ON inventory.category_id = categories.id
WHERE inventory.item_name = ?''', (product,))

join_result = cursor.fetchall()

for name in join_result:
    print(f'Товар: {name[0]}, Категория: {name[1]}')

# Сохраняем и закрываем базу даных
db.commit()
db.close()