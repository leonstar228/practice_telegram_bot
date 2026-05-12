from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def main_menu(is_admin: bool = False) -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(text="📝 Створити заявку"),
            KeyboardButton(text="📋 Мої заявки")
        ],
        [
            KeyboardButton(text="🌦 Погода"),
            KeyboardButton(text="📎 Надіслати файл")
        ],
        [
            KeyboardButton(text="📂 Мої файли"),
            KeyboardButton(text="ℹ️ Допомога")
        ]
    ]

    if is_admin:
        buttons.append([
            KeyboardButton(text="🛠 Адмін-панель")
        ])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )


def request_actions(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Редагувати",
                    callback_data=f"edit:{request_id}"
                ),
                InlineKeyboardButton(
                    text="🗑 Видалити",
                    callback_data=f"delete:{request_id}"
                )
            ]
        ]
    )


def admin_request_actions(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Виконано",
                    callback_data=f"status:{request_id}:done"
                ),
                InlineKeyboardButton(
                    text="⏳ В роботі",
                    callback_data=f"status:{request_id}:processing"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Відхилено",
                    callback_data=f"status:{request_id}:rejected"
                )
            ]
        ]
    )

def file_actions(file_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Перейменувати",
                    callback_data=f"file_edit:{file_id}"
                ),
                InlineKeyboardButton(
                    text="🗑 Видалити",
                    callback_data=f"file_delete:{file_id}"
                )
            ]
        ]
    )