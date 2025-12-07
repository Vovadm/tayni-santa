import random

from aiogram import Bot, Router, types
from aiogram.filters import Command

from config import settings
from db.db import get_session
from repository import ParticipantRepository

router = Router()


def make_pairs(participants: list):
    n = len(participants)
    k = random.randint(1, n - 1)
    receivers = participants[k:] + participants[:k]
    return {g.id: r.id for g, r in zip(participants, receivers)}


@router.message(Command("pair"))
async def pair_command(message: types.Message, bot: Bot):
    user = message.from_user
    if user is None:
        await message.answer("Ошибка: не удалось определить пользователя.")
        return

    if user.id != settings.ADMIN_ID:
        await message.answer("Команда только для администратора.")
        return

    async for session in get_session():
        repo = ParticipantRepository(session)
        participants = await repo.list_all()

        if len(participants) < 2:
            await message.answer("Недостаточно участников.")
            return

        participants_sorted = sorted(participants, key=lambda x: x.id)
        pairs_map = make_pairs(participants_sorted)

        await repo.set_pairs(pairs_map)

        sent = 0
        for giver in participants_sorted:
            receiver = next(
                p for p in participants_sorted if p.id == pairs_map[giver.id]
            )

            text = (
                "🎁 Тайный Санта!\n\n"
                f"Ты даришь: *{receiver.first_name} {receiver.last_name}*\n"
            )
            if receiver.wishes:
                text += f"\nПожелания: {receiver.wishes}"

            else:
                text += "\nПожелания: нету"

            try:
                await bot.send_message(giver.telegram_id, text, parse_mode="Markdown")
                sent += 1
            except Exception:
                pass

        await message.answer(f"Готово! Рассылок успешно отправлено: {sent}")
