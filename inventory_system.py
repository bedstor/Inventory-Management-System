# Импортируем библиотеки
import sqlite3


# Создаём функцию обработчика ошибок
def ask_int(question):
    while True:
        try:
            amount = int(input(question))
            return amount
        except:
            print("Ошибка! Введите число!")


def main():
    # Создаём базу данных
    db = sqlite3.connect("inventory_con.db")
    cursor = db.cursor()

    # Начальное  кол-во товара
    amount = 0

    # Создаём таблицу inventory
    cursor.execute("""CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    item_name TEXT UNIQUE NOT NULL,
    quantity BIGINT,
    price INTEGER,
    category_id INTEGER)""")

    # Создаём таблицу categories
    cursor.execute("""CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    category_name TEXT NOT NULL)""")

    # Меню
    while True:
        print("\n=== СИСТЕМА УЧЕТА СКЛАДА ===")
        print("1. Поступление / Добавление товара")
        print("2. Поиск информации о товаре")
        print("3. Отчет по дефициту (менее 5 шт.)")
        print("4. Выход")
        choice = input("\nВыберите действие (1-4): ")

        # Поступление или добавление товара
        if choice == "1":
            # Запрашиваем у пользователя название товара
            product = input("Название товара: \n").lower()

            # Есть ли этот товар в базе
            cursor.execute(
                """SELECT item_name FROM inventory WHERE item_name = ?""", (product,))

            # Результат в переменную
            result = cursor.fetchone()

            # В зависимости от условия выполняем действия
            if result:
                # Сначала узнаём, сколько было (достаём из ячейки [0])
                cursor.execute(
                    """SELECT quantity FROM inventory WHERE item_name = ?""", (product,))

                old_quantity = cursor.fetchone()[0]

                # Обработка ошибки
                new_amount = ask_int("Сколько единиц прибыло? \n")

                # Обновляем в базе
                cursor.execute(
                    """UPDATE inventory SET quantity = quantity + ?
                                WHERE item_name = ?""", (new_amount, product))

                # Считаем и выводим итог
                total = old_quantity + new_amount
                print(f"Запасы обновлены. Теперь на складе: {total} шт.")
            else:
                # Запрашиваем у пользователя категорию
                category_ans = input("Введите название категории: \n").lower()

                # Находим id этой категории
                cursor.execute(
                    "SELECT id FROM categories WHERE category_name = ?", (category_ans,))
                category_result = cursor.fetchone()

                # Если категории нет - добавляем, иначе - берём id этой категории
                if category_result == None:
                    # Добавляем название этой категории в таблицу
                    cursor.execute(
                        "INSERT INTO categories (category_name) VALUES (?)", (category_ans,))

                    # Записываем айди этой категории в переменную
                    category_ans_id = cursor.lastrowid
                else:
                    category_ans_id = category_result[0]

                # Обработка ошибки
                amount = ask_int("Количество товара: \n")

                # Обработка ошибки
                cost = ask_int("Цена: \n")

                cursor.execute(
                    """INSERT INTO inventory (item_name, quantity, price,
                                category_id) VALUES (?, ?, ?, ?)""", (product, amount, cost, category_ans_id))
                
                print(f"Товар {product} добавлен. Общая стоимость на складе: {cost * amount}")

            db.commit()

        # Поиск товара
        elif choice == "2":
            # Запрашиваем у пользователя название товара для поиска в базе
            search_product = input("Желаете найти товар? Введите его название: \n").lower()

            # Объединяем таблицы, чтобы вместо category_id показать название товара
            cursor.execute(
                """SELECT inventory.item_name, inventory.price, categories.category_name
            FROM inventory
            JOIN categories ON inventory.category_id = categories.id
            WHERE inventory.item_name = ?""", (search_product,))

            # Сохраняем результат в переменную
            search_result = cursor.fetchone()

            # Если товар не найден, то выводим вежливое сообщение, иначе - выводим результат
            if search_result == None:
                print("\n" + "-"*30) # Линия сверху
                print("Упс! Такого товара ещё не существует...")
                print("-"*30 + "\n") # Линия снизу
            else:
                print("\n" + "="*30)
                print(f"Товар: {search_result[0]}\nЦена: {search_result[1]}\nКатегория: {search_result[2]}")
                print("="*30 + "\n")


        # Отчёт по дефициту
        elif choice == "3":
            # Объединяем таблицы, чтобы сделать отчёт красивым
            cursor.execute("""SELECT inventory.item_name, categories.category_name, inventory.quantity
            FROM inventory
            JOIN categories ON inventory.category_id = categories.id
            WHERE inventory.quantity < 5""")

            # Сохраняем результат в переменную
            deficit_result = cursor.fetchall()

            print("\n" + "!"*30) # Сделаем линию из восклицательных знаков для привлечения внимания

            # Выводим результат
            if not deficit_result:
                print("На складе полно товара, дефицита нет!")
            else:
                for row in deficit_result:
                    print(f"ВНИМАНИЕ! {row[0]} (Категория: {row[1]}) - осталось всего {row[2]} шт.\n")
                print("!"*30 + "\n")


        # Завершение работы программы
        elif choice == "4":
            print("\nРабота завершена. До свидания! ")
            break

        # Обработка другого пункта (случайного нажатия)
        else:
            print("\nОШИБКА! Выберите другой пункт!")

    # Закрываем базу данных
    db.close()


# Если этот файл запустили как главный, то начинаем выполнять main()
if __name__ == "__main__":
    main()
