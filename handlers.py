from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import settings
from database import (
    register_user,
    get_user_by_telegram_id,
    create_request,
    get_user_requests,
    get_all_requests,
    get_request_by_id,
    update_request,
    update_request_status,
    delete_request,
    save_file,
    get_user_files,
    get_file_by_id,
    update_file_name,
    delete_file
)
from keyboards import (
    main_menu,
    request_actions,
    admin_request_actions,
    file_actions
)
from states import RequestState, WeatherState, FileState
from services import get_weather, STATUS_NAMES

router = Router()


def is_admin(telegram_id: int) -> bool:
    return telegram_id in settings.admin_ids


async def ensure_user(message: Message):
    role = "admin" if is_admin(message.from_user.id) else "user"

    await register_user(
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username,
        role=role
    )

    return await get_user_by_telegram_id(message.from_user.id)


@router.message(Command("start"))
async def start(message: Message):
    user = await ensure_user(message)

    text = (
        "Вітаю! Я бот для автоматизації задач підприємства.\n\n"
        "Через мене можна створювати заявки, переглядати їх статус, "
        "надсилати файли та отримувати додаткову інформацію через API."
    )

    await message.answer(text, reply_markup=main_menu(user["role"] == "admin"))


@router.message(Command("menu"))
async def menu(message: Message):
    user = await ensure_user(message)
    await message.answer("Головне меню:", reply_markup=main_menu(user["role"] == "admin"))


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Дію скасовано.", reply_markup=main_menu(is_admin(message.from_user.id)))


@router.message(F.text == "ℹ️ Допомога")
async def help_text(message: Message):
    await ensure_user(message)

    await message.answer(
        "Доступні функції:\n"
        "📝 Створити заявку – подати нову заявку до підприємства.\n"
        "📋 Мої заявки – переглянути власні заявки.\n"
        "🌦 Погода – отримати інформацію через сторонній API.\n"
        "📎 Надіслати файл – передати документ або зображення.\n"
        "📂 Мої файли – переглянути раніше надіслані файли.\n"
        "/cancel – скасувати поточну дію."
    )


@router.message(F.text == "📝 Створити заявку")
async def request_title(message: Message, state: FSMContext):
    await ensure_user(message)
    await state.set_state(RequestState.waiting_for_title)
    await message.answer("Введіть коротку тему заявки:")


@router.message(RequestState.waiting_for_title)
async def request_description(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 3:
        await message.answer("Тема заявки має містити мінімум 3 символи.")
        return

    await state.update_data(title=message.text.strip())
    await state.set_state(RequestState.waiting_for_description)
    await message.answer("Опишіть заявку детальніше:")


@router.message(RequestState.waiting_for_description)
async def save_request(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 5:
        await message.answer("Опис заявки має містити мінімум 5 символів.")
        return

    user = await ensure_user(message)
    data = await state.get_data()

    await create_request(user["id"], data["title"], message.text.strip())

    await state.clear()
    await message.answer("Заявку успішно створено.", reply_markup=main_menu(user["role"] == "admin"))


@router.message(F.text == "📋 Мої заявки")
async def my_requests(message: Message):
    user = await ensure_user(message)
    requests = await get_user_requests(user["id"])

    if not requests:
        await message.answer("У вас поки немає заявок.")
        return

    status_icons = {
        "new": "🆕",
        "processing": "⏳",
        "done": "✅",
        "rejected": "❌"
    }

    for item in requests:
        status = STATUS_NAMES.get(item["status"], item["status"])
        icon = status_icons.get(item["status"], "📌")

        text = (
            f"Заявка #{item['id']}\n\n"
            f"Тема: {item['title']}\n"
            f"Опис: {item['description']}\n"
            f"Статус: {status}{icon}\n"
            f"Створено: {item['created_at']} 🕒"
        )

        await message.answer(
            text,
            reply_markup=request_actions(item["id"])
        )

@router.callback_query(F.data.startswith("delete:"))
async def delete_request_callback(callback: CallbackQuery):
    user = await get_user_by_telegram_id(callback.from_user.id)
    request_id = int(callback.data.split(":")[1])

    await delete_request(request_id, user["id"])

    await callback.message.edit_text("Заявку видалено.")
    await callback.answer()


@router.callback_query(F.data.startswith("edit:"))
async def edit_request_callback(callback: CallbackQuery, state: FSMContext):
    request_id = int(callback.data.split(":")[1])

    await state.update_data(edit_request_id=request_id)
    await state.set_state(RequestState.waiting_for_edit_text)

    await callback.message.answer("Введіть новий опис заявки:")
    await callback.answer()


@router.message(RequestState.waiting_for_edit_text)
async def save_edited_request(message: Message, state: FSMContext):
    data = await state.get_data()
    request_id = data["edit_request_id"]

    request_item = await get_request_by_id(request_id)
    user = await get_user_by_telegram_id(message.from_user.id)

    if not request_item or request_item["user_id"] != user["id"]:
        await state.clear()
        await message.answer("Заявку не знайдено або немає доступу.")
        return

    await update_request(request_id, message.text.strip())

    await state.clear()
    await message.answer("Заявку оновлено.", reply_markup=main_menu(user["role"] == "admin"))


@router.message(F.text == "🌦 Погода")
async def weather_start(message: Message, state: FSMContext):
    await ensure_user(message)
    await state.set_state(WeatherState.waiting_for_city)
    await message.answer("Введіть назву міста:")


@router.message(WeatherState.waiting_for_city)
async def weather_result(message: Message, state: FSMContext):
    result = await get_weather(message.text.strip())

    await state.clear()
    await message.answer(result, reply_markup=main_menu(is_admin(message.from_user.id)))


@router.message(F.text == "📎 Надіслати файл")
async def file_instruction(message: Message):
    await ensure_user(message)
    await message.answer("Надішліть документ або фото одним повідомленням.")


@router.message(F.document)
async def document_handler(message: Message):
    user = await ensure_user(message)
    document = message.document

    await save_file(user["id"], document.file_id, document.file_name, document.mime_type)

    await message.answer("Документ збережено в базі даних.")


@router.message(F.photo)
async def photo_handler(message: Message):
    user = await ensure_user(message)
    photo = message.photo[-1]

    await save_file(user["id"], photo.file_id, "photo.jpg", "image/jpeg")

    await message.answer("Фото збережено в базі даних.")


@router.message(F.text == "📂 Мої файли")
async def show_my_files(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)

    if not user:
        await message.answer("Спочатку натисніть /start.")
        return

    files = await get_user_files(user["id"])

    if not files:
        await message.answer("Ви ще не надсилали файли.")
        return

    for file in files:
        caption = (
            f"Файл #{file['id']}\n"
            f"Назва: {file['file_name'] or 'Без назви'}\n"
            f"Дата: {file['created_at']}"
        )

        try:
            await message.answer_photo(
                photo=file["telegram_file_id"],
                caption=caption,
                reply_markup=file_actions(file["id"])
            )

        except:
            await message.answer_document(
                document=file["telegram_file_id"],
                caption=caption,
                reply_markup=file_actions(file["id"])
            )


@router.callback_query(F.data.startswith("file_delete:"))
async def delete_file_callback(callback: CallbackQuery):
    user = await get_user_by_telegram_id(callback.from_user.id)

    if not user:
        await callback.answer("Спочатку натисніть /start.", show_alert=True)
        return

    file_id = int(callback.data.split(":")[1])

    await delete_file(file_id, user["id"])

    await callback.answer("Файл видалено.", show_alert=True)
    await callback.message.answer("Файл успішно видалено.")


@router.callback_query(F.data.startswith("file_edit:"))
async def edit_file_callback(callback: CallbackQuery, state: FSMContext):
    user = await get_user_by_telegram_id(callback.from_user.id)

    if not user:
        await callback.answer("Спочатку натисніть /start.", show_alert=True)
        return

    file_id = int(callback.data.split(":")[1])
    file = await get_file_by_id(file_id)

    if not file or file["user_id"] != user["id"]:
        await callback.answer("Файл не знайдено або немає доступу.", show_alert=True)
        return

    await state.update_data(edit_file_id=file_id)
    await state.set_state(FileState.waiting_for_new_file_name)

    await callback.message.answer("Введіть нову назву файлу:")
    await callback.answer()


@router.message(FileState.waiting_for_new_file_name)
async def save_new_file_name(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("Назва файлу має містити мінімум 2 символи.")
        return

    user = await get_user_by_telegram_id(message.from_user.id)
    data = await state.get_data()
    file_id = data["edit_file_id"]

    await update_file_name(file_id, user["id"], message.text.strip())

    await state.clear()
    await message.answer("Назву файлу оновлено.")

@router.message(Command("admin"))
@router.message(F.text == "🛠 Адмін-панель")
async def admin_panel(message: Message):
    user = await ensure_user(message)

    if user["role"] != "admin":
        await message.answer("У вас немає доступу до адмін-панелі.")
        return

    requests = await get_all_requests()

    if not requests:
        await message.answer("Активних заявок поки немає.")
        return

    for item in requests:
        status = STATUS_NAMES.get(item["status"], item["status"])
        username = f"@{item['username']}" if item["username"] else "без username"

        text = (
            f"Заявка #{item['id']}\n"
            f"Користувач: {item['full_name']} ({username})\n"
            f"Тема: {item['title']}\n"
            f"Опис: {item['description']}\n"
            f"Статус: {status}\n"
            f"Створено: {item['created_at']}"
        )

        await message.answer(text, reply_markup=admin_request_actions(item["id"]))


@router.callback_query(F.data.startswith("status:"))
async def status_callback(callback: CallbackQuery):
    user = await get_user_by_telegram_id(callback.from_user.id)

    if not user or user["role"] != "admin":
        await callback.answer("Немає доступу.", show_alert=True)
        return

    _, request_id, status = callback.data.split(":")

    await update_request_status(int(request_id), status)

    await callback.message.edit_text(
        f"Статус заявки #{request_id} змінено на: {STATUS_NAMES.get(status, status)}"
    )

    await callback.answer()


@router.message()
async def unknown_message(message: Message):
    user = await ensure_user(message)

    await message.answer(
        "Я не розумію цю команду. Скористайтесь меню.",
        reply_markup=main_menu(user["role"] == "admin")
    )