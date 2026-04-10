from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_lang_settings_kb(
    i18n: dict, locales: list[str], checked: str
) -> InlineKeyboardMarkup:
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
                callback_data="cancel_lang_button_data",
            ),
            InlineKeyboardButton(
                text=i18n.get("save_lang_button_text"),
                callback_data="save_lang_button_data",
            ),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


sections = [
    "Планиметрия. Часть I",
    "Векторы",
    "Стереометрия. Часть I",
    "Теория вероятности I",
    "Теория вероятности II",
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

all = "Все типы задач"
gen_variant = "Сгенерировать вариант"


def sections_keyboard() -> InlineKeyboardMarkup:

    buttons = [
        InlineKeyboardButton(text=text, callback_data=str(data + 1))
        for data, text in enumerate(sections)
    ]

    all_btn = InlineKeyboardButton(text=all, callback_data=str(len(sections) + 1))
    gen_btn = InlineKeyboardButton(
        text=gen_variant, callback_data=str(len(sections) + 2)
    )

    buttons.extend([all_btn, gen_btn])
    kb_builder = InlineKeyboardBuilder()

    # Распаковываем список с кнопками в билдер методом `row`
    kb_builder.row(*buttons, width=2)
    return kb_builder.as_markup()


def web_sections_keyboard(webapp_url: str = None) -> InlineKeyboardMarkup:

    buttons = [
        InlineKeyboardButton(
            text=text,
            web_app=WebAppInfo(url=f"{webapp_url}/{data + 1}"),
        )
        for data, text in enumerate(sections)
    ]

    all_btn = InlineKeyboardButton(text=all, callback_data=str(len(sections) + 1))
    gen_btn = InlineKeyboardButton(
        text=gen_variant, callback_data=str(len(sections) + 2)
    )

    buttons.extend([all_btn, gen_btn])
    kb_builder = InlineKeyboardBuilder()

    # Распаковываем список с кнопками в билдер методом `row`
    kb_builder.row(*buttons, width=2)
    return kb_builder.as_markup()


def answer_keyboard(i18n: dict) -> InlineKeyboardMarkup:
    cancel_btn = InlineKeyboardButton(
        text=i18n.get("cancel_ans"), callback_data="cancel_ans"
    )
    send_ans_btn = InlineKeyboardButton(
        text=i18n.get("send_ans"), callback_data="send_ans"
    )
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(cancel_btn, send_ans_btn, widh=2)

    return kb_builder.as_markup()


def webapp_keyboard(webapp_url: str) -> InlineKeyboardMarkup:
    web_btn = InlineKeyboardButton(
        text="📋 Выбрать задачи", web_app=WebAppInfo(url=webapp_url)
    )

    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(web_btn, width=2)
    return kb_builder.as_markup()
