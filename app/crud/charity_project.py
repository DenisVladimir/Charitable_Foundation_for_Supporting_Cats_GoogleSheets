from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import CharityProject


from app.crud.base import CRUDBase


class CRUDCharityProject(CRUDBase):

    async def exist_by_name(
        self,
        project_name: str,
        session: AsyncSession,
    ) -> bool:
        """Проверяет существование полученного имени в БД, возвращает True/False."""
        db_project_id = await session.execute(
            select(select(self._model).where(self._model.name == project_name).exists())
        )
        return db_project_id.scalar()

        # Функция сортировки проектов по времени закрытия
    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession,
    ) -> list[dict]:
        close_projects = await session.execute(
            select(
                CharityProject.name,
                func.julianday(CharityProject.close_date) -
                func.julianday(CharityProject.create_date),
                CharityProject.description).where(
                    CharityProject.fully_invested == 1
            ).order_by(CharityProject.close_date - CharityProject.create_date)
        )
        close_projects = close_projects.all()
        return close_projects

charity_project_crud = CRUDCharityProject(CharityProject)
