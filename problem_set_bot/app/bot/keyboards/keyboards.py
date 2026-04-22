from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
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


def web_sections_keyboard(base_url: str, cart: list = None) -> InlineKeyboardMarkup:
    """
    Клавиатура с WebApp-кнопками для каждой темы.
    :param base_url: базовый URL для WebApp (например, https://domain.com/tasks)
    :param cart: список source_id уже выбранных задач (для передачи в URL)
    """
    cart_str = ",".join(cart) if cart else ""
    buttons = []
    for idx, text in enumerate(sections):
        position = idx + 1
        url = f"{base_url}/{position}"
        if cart_str:
            url += f"?cart={cart_str}"

        buttons.append(InlineKeyboardButton(text=text, web_app=WebAppInfo(url=url)))
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(*buttons, width=2)
    return kb_builder.as_markup()


def web_sections_reply_keyboard(
    base_url: str, cart: list = None, width: int = 2
) -> ReplyKeyboardMarkup:
    """
    Reply-клавиатура с WebApp-кнопками для каждой темы.
    """
    cart_str = ",".join(cart) if cart else ""
    buttons = []
    for idx, text in enumerate(sections):
        position = idx + 1
        url = f"{base_url}/{position}"
        if cart_str:
            url += f"?cart={cart_str}"
        buttons.append(KeyboardButton(text=text, web_app=WebAppInfo(url=url)))

    rows = [buttons[i : i + width] for i in range(0, len(buttons), width)]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


# def cart_management_keyboard(
#     cart_size: int, base_cart_url: str, cart: list = None
# ) -> InlineKeyboardMarkup:
#     """
#     Клавиатура для команды /cart.
#     :param cart_size: количество задач в корзине
#     :param base_cart_url: URL для редактирования корзины (например, https://domain.com/cart)
#     :param cart: список source_id задач в корзине (для передачи в URL)
#     """
#     cart_str = ",".join(cart) if cart else ""
#     url = base_cart_url
#     if cart_str:
#         url += f"?cart={cart_str}"
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text=f"✏️ Редактировать корзину ({cart_size})",
#                     web_app=WebAppInfo(url=url),
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text="🖨️ Отправить на печать", callback_data="print_cart"
#                 )
#             ],
#         ]
#     )
#     return keyboard


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


def cart_management_keyboard(
    base_cart_url: str, cart: list = None
) -> InlineKeyboardMarkup:
    cart_size = len(cart)
    cart_str = ",".join(cart) if cart else ""
    url = base_cart_url
    if cart_str:
        url += f"?cart={cart_str}"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"✏️ Смотреть/редактировать корзину ({cart_size})",
                    web_app=WebAppInfo(url=url),
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑️ Очистить корзину", callback_data="clear_cart"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🖨️ Отправить на печать", callback_data="print_cart"
                )
            ],
        ]
    )
    return keyboard


def test_keyboard(url: str):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🧪 Тест WebApp", web_app=WebAppInfo(url=url))]]
    )

    return keyboard


def choose_reply_keyboard(url: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📋 Выбрать задачи (WebApp)", web_app=WebAppInfo(url=url)
                )
            ]
        ],
        resize_keyboard=True,
    )
