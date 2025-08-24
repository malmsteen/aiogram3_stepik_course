from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_lang_settings_kb(i18n: dict, locales: list[str], checked: str) -> InlineKeyboardMarkup:
    buttons = []
    for locale in sorted(locales):
        if locale == "default":
            continue
        if locale == checked:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"🔘 {i18n.get(locale)}", callback_data=locale
                    )
                ]
            )
        else:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"⚪️ {i18n.get(locale)}", callback_data=locale
                    )
                ]
            )
    buttons.append(
        [
            InlineKeyboardButton(
                text=i18n.get("cancel_lang_button_text"), 
                callback_data="cancel_lang_button_data"
            ),
            InlineKeyboardButton(
                text=i18n.get("save_lang_button_text"), 
                callback_data="save_lang_button_data"
            ),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)

sections = [
    "Планиметрия. Часть I",
    "Векторы",
    "Стереометрия. Часть I",
    "Теория вероятности",    
    "Уравнения. Часть I",
    "Вычисление выражений",
    "Производная и первообразная",
    "Прикладные задачи",
    "Текстовые задачи",
    "Графики функций",
    "Экстремумы функций",
    "Уравнения",
    "Стереометрия. Часть II",
    "Неравенства",
    "Планиметрия. Часть II",
    "Экономические задачи",    
    "Задачи с параметрами",
    "Задачи по теории чисел",    
]

def create_sections_keyboard() -> InlineKeyboardMarkup:    
    buttons = [InlineKeyboardButton(text=text, callback_data=str(data+1)) for data, text in enumerate(sections)]
    kb_builder = InlineKeyboardBuilder()
    

    # Распаковываем список с кнопками в билдер методом `row`
    kb_builder.row(*buttons, width=2)    
    return kb_builder.as_markup()
