from datetime import datetime
from typing import Optional

from app.models import User
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDBase:
    def __init__(self, model):
        self._model = model

    async def get_all(
        self,
        session: AsyncSession,
    ):
        """Возвращает все объекты из БД текущей модели."""
        db_objs = await session.execute(select(self._model))
        return db_objs.scalars().all()

    async def get_open_objects(
            self,
            session: AsyncSession,
    ):
        db_objs = await session.execute(
            select(self._model).where(
                self._model.fully_invested.is_(False)
            )
        )
        return db_objs.scalars().all()

    async def get(
        self,
        charity_id: int,
        session: AsyncSession,
    ):
        """Возвращает объект CharityProject из БД по его id, либо возвращает None."""
        db_obj = await session.execute(
            select(self._model).where(self._model.id == charity_id)
        )
        return db_obj.scalars().first()

    async def create(
        self,
        request_obj,
        session: AsyncSession,
        user: Optional[User] = None,
        commit: bool = True,
    ):

        """Создает объект текущей модели."""
        request_object = request_obj.dict()
        if user is not None:
            request_object["user_id"] = user.id
        db_obj = self._model(**request_object)
        session.add(db_obj)

        if commit:
            await session.commit()
            await session.refresh(db_obj)
        return db_obj

    async def get_by_id(
        self,
        project_id: int,
        session: AsyncSession
    ):
        """Возвращает объект CharityProject по его id, либо выбрасывает ошибку"""
        project = await self.get(project_id, session)
        if project is None:
            raise HTTPException(status_code=404, detail="Проект не найден!")
        return project

    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession,
    ):
        """Обновляет объект CharityProject и возвращает обновленный объект."""
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict()
        for field in obj_data:
            if field in update_data and update_data[field] is not None:
                setattr(db_obj, field, update_data[field])
        #db_obj = investing_sevice.set_close(db_obj)
        if db_obj.invested_amount == db_obj.full_amount:
            db_obj.fully_invested = True
            db_obj.close_date = datetime.now()
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db_obj,
        session: AsyncSession,
    ):
        """Удаляет объект CharityProject по его id."""
        await session.delete(db_obj)
        await session.commit()
        return db_obj
