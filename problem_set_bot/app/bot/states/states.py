from aiogram.fsm.state import State, StatesGroup


class LangSG(StatesGroup):
    lang = State()


class BroadcastState(StatesGroup):
    waiting_for_content = State()
