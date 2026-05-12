from aiogram.fsm.state import State, StatesGroup

class RequestState(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_edit_text = State()

class WeatherState(StatesGroup):
    waiting_for_city = State()

class FileState(StatesGroup):
    waiting_for_new_file_name = State()
