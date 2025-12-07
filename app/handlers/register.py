from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from db.db import get_session
from repository import ParticipantRepository

router = Router()


class RegisterStates(StatesGroup):
    first_name = State()
    last_name = State()
    wishes = State()


@router.message(Command(commands=["start"]))
async def start_handler(message: types.Message, state: FSMContext):
    user = message.from_user
    if user is None:
        await message.answer("Ошибка: не удалось определить пользователя.")
        return

    user_id = user.id

    async for session in get_session():
        repo = ParticipantRepository(session)
        existing = await repo.get_by_telegram_id(user_id)

        if existing:
            await message.answer(
                "Вы уже зарегистрированы. Спасибо! Если хотите — можете обновить пожелания через /change_data"
            )
            return

    await message.answer(
        "Привет! Давай зарегистрируемся для Тайного Санты. Как тебя зовут? (имя)"
    )
    await state.set_state(RegisterStates.first_name)


@router.message(RegisterStates.first_name)
async def first_name_handler(message: types.Message, state: FSMContext):
    text = message.text or ""
    await state.update_data(first_name=text.strip())

    await message.answer("Фамилия?")
    await state.set_state(RegisterStates.last_name)


@router.message(RegisterStates.last_name)
async def last_name_handler(message: types.Message, state: FSMContext):
    text = message.text or ""
    await state.update_data(last_name=text.strip())

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Пропустить")]], resize_keyboard=True
    )

    await message.answer(
        "Пожелания (по желанию). Можете написать что хотите получить или нажать Пропустить.",
        reply_markup=kb,
    )
    await state.set_state(RegisterStates.wishes)


@router.message(RegisterStates.wishes)
async def wishes_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()

    text = message.text or ""
    wishes_text = None if text == "Пропустить" else text.strip()

    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        await message.answer("Ошибка: не удалось определить ваш Telegram ID.")
        return

    async for session in get_session():
        repo = ParticipantRepository(session)
        await repo.create(
            tg_id=user_id,
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            wishes=wishes_text,
        )

    await message.answer(
        "Вы успешно зарегистрированы! Спасибо.",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.clear()


@router.message(Command(commands=["change_data"]))
async def change_data_handler(message: types.Message, state: FSMContext):
    user = message.from_user
    if user is None:
        await message.answer("Ошибка: не удалось определить пользователя.")
        return

    user_id = user.id

    async for session in get_session():
        repo = ParticipantRepository(session)
        existing = await repo.get_by_telegram_id(user_id)

        if existing:
            await repo.delete_by_telegram_id(user_id)
            await message.answer(
                "Ваша предыдущая регистрация удалена. Давайте заново зарегистрируемся."
            )

    await message.answer(
        "Привет! Давай зарегистрируемся для Тайного Санты. Как тебя зовут? (имя)"
    )
    await state.set_state(RegisterStates.first_name)
