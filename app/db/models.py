from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.db import Base


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    wishes: Mapped[str | None] = mapped_column(Text, nullable=True)
    registered_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    paired_to_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("participants.id"), nullable=True
    )

    def __repr__(self) -> str:
        return f"<Participant id={self.id} tg={self.telegram_id} name={self.first_name} {self.last_name}>"
