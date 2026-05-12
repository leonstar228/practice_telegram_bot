# Practice Telegram Bot

Telegram-бот для автоматизації задач підприємства-бази практики.

## Функції

- Реєстрація користувача
- Меню з кнопками
- Створення заявок
- Перегляд власних заявок
- Редагування та видалення заявок
- Адмін-перегляд усіх заявок
- Зміна статусу заявки адміністратором
- Інтеграція API погоди
- Приймання файлів від користувачів
- Зберігання даних у SQLite

## Встановлення

1. Створити бота через BotFather і отримати токен.
2. Створити файл `.env` на основі `.env.example`.
3. Встановити залежності:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

4. Запустити:

```bash
python main.py
```

## Команди

- `/start` – запуск і реєстрація
- `/menu` – головне меню
- `/cancel` – скасування поточної дії
- `/admin` – адмін-панель

## Розгортання на Render

1. Завантажити проєкт на GitHub.
2. На Render створити Background Worker.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python main.py`
5. Додати змінні середовища:
   - `BOT_TOKEN`
   - `ADMIN_IDS`
   - `WEATHER_API_KEY`
   - `DB_PATH`
