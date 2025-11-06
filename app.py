from flask import Flask, request, jsonify
from flask import Flask, request, jsonify
import sqlite3
import re
from datetime import datetime
from happy import hello  # импортируем функцию из code.py

app = Flask(__name__)
DB_PATH = "books.db"

#преобразование имени автора (будет преобразование запроса - lower и т.д.)
def sanitize_table_name(str):
    clean = re.sub(r"[^a-zA-Z0-9_ ]", "", name)
    clean = clean.strip().replace(" ", "_")
    if not clean:
        clean = "unknown"
    return clean.lower()

#создание базы данных (будем делать, если еще не создана)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    conn.close()

def save_books_to_db(author: str, books: list):
    """Сохраняет книги в таблицу по автору, избегая дубликатов"""
    table_name = f"author_{sanitize_table_name(author)}"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Создаём таблицу, если не существует 
    # в title будет заголовок, author = link, UNIQUE(title, link)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} ( 
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, 
            author TEXT NOT NULL,
            purchase_date TEXT NOT NULL,
            description TEXT,
            UNIQUE(title, purchase_date)  -- гарантируем уникальность пары
        )
    """)

    inserted = 0
    for book in books:
        try:
            cursor.execute(f"""
                INSERT OR IGNORE INTO {table_name}
                (title, author, purchase_date, description)
                VALUES (?, ?, ?, ?)
            """, (
                book["title"],
                book["author"],
                book["purchase_date"],
                book.get("description", "") #если есть описание
            ))
            if cursor.rowcount > 0:
                inserted += 1
        except sqlite3.Error as e:
            print(f"⚠️ Ошибка при вставке книги '{book['title']}': {e}")

    conn.commit()
    conn.close()
    return inserted #количество вставленных новостей

@app.route('/search', methods = ["POST"])
def search():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON body is required"}), 400
        author = data.get("author") #потом будет link
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        #преобразование дат:
        if start_date:
            datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            datetime.strptime(end_date, "%Y-%m-%d")
        if start_date and end_date and start_date > end_date:
            return jsonify({"error": "start_date must be <= end_date"}), 400

        #получаем json-список новостей
        books = search_books(author=author, start_date=start_date, end_date=end_date) #отправляем параметры в функцию из кода в другом файле

        if books:
            inserted = save_books_to_db(author, books)
            print(f"✅ Сохранено {inserted} новостей")
        app.logger.info(f"🔍 Найдено {len(books)} книг. Сохранено новых: {inserted}.")


        #отдаем список json и количество записей в бд
        return jsonify({
            "books": books,
            "count": len(books)
        }), 200

    #не знаю, зачем эти исключения:
    except ValueError as e:
        return jsonify({"error": f"Invalid date format: {e}"}), 400
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)


#то что дальше - только для тестов
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "db": DB_PATH}), 200

print("\n🔧 Зарегистрированные маршруты:")
for rule in app.url_map.iter_rules():
    methods = ', '.join(rule.methods)
    print(f"  {rule.rule} [{methods}]")
print()

if __name__ == '__main__':
    init_db()
    print("✅ База данных инициализирована.")
    print("🚀 Запуск сервера на http://localhost:5000")
    print("📌 Доступные эндпоинты:")
    print("   GET  /health     — проверка работоспособности")
    print("   POST /search     — поиск книг (см. примеры ниже)")
    app.run(debug=True, host='127.0.0.1', port=5000)

