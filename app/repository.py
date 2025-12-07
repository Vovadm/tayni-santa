from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Participant


class ParticipantRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, tg_id: int) -> Optional[Participant]:
        q = select(Participant).where(Participant.telegram_id == tg_id)
        res = await self.session.execute(q)
        return res.scalars().first()

    async def create(
        self,
        tg_id: int,
        first_name: str,
        last_name: str,
        wishes: Optional[str] = None,
    ) -> Participant:
        p = Participant(
            telegram_id=tg_id,
            first_name=first_name,
            last_name=last_name,
            wishes=wishes,
            registered_at=datetime.now(timezone.utc),
        )
        self.session.add(p)
        await self.session.commit()
        await self.session.refresh(p)
        return p

    async def update_wishes(
        self, tg_id: int, wishes: Optional[str]
    ) -> Optional[Participant]:
        q = (
            update(Participant)
            .where(Participant.telegram_id == tg_id)
            .values(wishes=wishes)
        )
        await self.session.execute(q)
        await self.session.commit()
        return await self.get_by_telegram_id(tg_id)

    async def list_all(self) -> List[Participant]:
        q = select(Participant)
        res = await self.session.execute(q)
        return list(res.scalars().all())

    async def set_pairs(self, pairs: dict[int, int]) -> None:
        for giver_id, receiver_id in pairs.items():
            participant = await self.session.get(Participant, giver_id)
            if participant:
                participant.paired_to_id = receiver_id
                await self.session.flush()

        await self.session.commit()

    async def delete_by_telegram_id(self, tg_id: int) -> None:
        participant = await self.get_by_telegram_id(tg_id)
        if not participant:
            return
        q_update = (
            update(Participant)
            .where(Participant.paired_to_id == participant.id)
            .values(paired_to_id=None)
        )
        await self.session.execute(q_update)

        q_delete = delete(Participant).where(Participant.id == participant.id)
        await self.session.execute(q_delete)

        await self.session.commit()
