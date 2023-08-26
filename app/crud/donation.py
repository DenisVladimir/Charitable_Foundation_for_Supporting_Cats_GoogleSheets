from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Donation, User
from app.crud.base import CRUDBase


class CRUDDonation(CRUDBase):
    async def get_by_user(
        self,
        user: User,
        session: AsyncSession,
    ) -> List[Donation]:
        """Возвращает все пожертвования текущего пользователя."""
        donations = await session.execute(
            select(self._model).where(self._model.user_id == user.id)
        )
        return donations.scalars().all()


donation_crud = CRUDDonation(Donation)
