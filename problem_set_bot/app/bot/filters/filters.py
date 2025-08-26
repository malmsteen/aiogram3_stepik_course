import string
import json

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message
from psycopg import AsyncConnection

from app.bot.enums.roles import UserRole
from app.infrastructure.database.db import get_user_role

import regex as re

class LocaleFilter(BaseFilter):
    async def __call__(self, callback: CallbackQuery, locales: list):
        if not isinstance(callback, CallbackQuery):
            raise ValueError(
                f"LocaleFilter: expected `CallbackQuery`, got `{type(callback).__name__}`"
            )
        return callback.data in locales


class UserRoleFilter(BaseFilter):
    def __init__(self, *roles: str | UserRole):
        if not roles:
            raise ValueError("At least one role must be provided to UserRoleFilter.")

        self.roles = frozenset(
            UserRole(role) if isinstance(role, str) else role
            for role in roles
            if isinstance(role, (str, UserRole))
        )

        if not self.roles:
            raise ValueError("No valid roles provided to `UserRoleFilter`.")

    async def __call__(self, event: Message | CallbackQuery, conn: AsyncConnection) -> bool:
        user = event.from_user
        if not user:
            return False

        role = await get_user_role(conn, user_id=user.id)
        if role is None:
            return False
        
        return role in self.roles
    

class IsDigitCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.data.isdigit()
    
class HexIdsInMessage(BaseFilter):
    async def __call__(self, message: Message) -> bool | dict[str, list[int]]:
        hexids = []        
        if message.text:
            text = message.text
        elif message.caption:
            text = message.caption  
        else:
            return False
        
        for word in text.split():
            normalized_word = word.replace('.', '').replace(',', '').strip()
            if all(c in string.hexdigits for c in normalized_word):
                hexids.append(normalized_word)
        if hexids:
            return {'source_ids': hexids}
        
    
class FloatAns(BaseFilter):
    async def __call__(self, message: Message) -> bool | dict[str, list[int]]:
        msg = message.text.split()
        if len(msg) == 2 and re.search('-?\d+[.,]?\d+?', msg[-1]):
            float_num = msg[-1]
            return {'float_num': float_num}
        else:
            return False

