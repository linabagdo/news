# code.py
import json
from datetime import datetime

def get_books():
    # Пример: возвращает список книг
    return [
        {
            "title": "1984",
            "author": "George Orwell",
            "purchase_date": "2024-10-05",
            "description": "Dystopian novel about totalitarianism."
        },
        {
            "title": "Animal Farm",
            "author": "George Orwell",
            "purchase_date": "2024-11-01",
            "description": "Allegorical novella about Soviet communism."
        },
        {
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "purchase_date": "2025-01-15",
            "description": "Fantasy adventure novel."
        }
    ]

# Пусть будет основная функция, которую можно вызывать с параметрами
def hello(author=None, start_date=None, end_date=None):
    books = get_books()

    # Фильтрация по автору
    if author:
        books = [b for b in books if b["author"].lower() == author.lower()]

    # Фильтрация по дате
    def parse_date(d):
        return datetime.strptime(d, "%Y-%m-%d").date()

    if start_date or end_date:
        filtered = []
        for book in books:
            try:
                pd = parse_date(book["purchase_date"])
                if start_date and pd < parse_date(start_date):
                    continue
                if end_date and pd > parse_date(end_date):
                    continue
                filtered.append(book)
            except ValueError:
                continue  # пропускаем некорректные даты
        books = filtered

    return books
