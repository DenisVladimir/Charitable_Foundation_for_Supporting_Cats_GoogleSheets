from typing import List

from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import validators
from app.core.db import get_async_session
from app.services import investing_services
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.schemas.charity_project import (
    CharityProjectDBResponse,
    CharityProjectUpdateRequest,
    CharityProjectCreateRequest,
)

router = APIRouter(prefix="/charity_project", tags=["charity_projects"])


@cbv(router)
class CharityProjectCBV:
    session: AsyncSession = Depends(get_async_session)

    @router.get(
        "/",
        response_model=List[CharityProjectDBResponse],
        response_model_exclude_none=True,
        summary="Получить список всех проектов.",
    )
    async def get_all_charity_projects(
        self,
    ) -> List[CharityProjectDBResponse]:
        """Возвращает список всех проектов"""
        all_projects = await charity_project_crud.get_all(self.session)
        return all_projects

    @router.post(
        "/",
        response_model=CharityProjectDBResponse,
        dependencies=[Depends(current_superuser)],
        response_model_exclude_none=True,
        summary="Создать проект.",
    )
    async def create_charity_project(
        self,
        new_project: CharityProjectCreateRequest,
    ) -> CharityProjectDBResponse:
        """
        Только для суперюзеров.\n
        Создает благотворительный проект.
        """
        await validators.check_name_duplicate(new_project, self.session)
        new_project = await charity_project_crud.create(new_project, self.session)
        donations = await donation_crud.get_open_objects(self.session)
        donations = investing_services.investment(
            new_project,
            donations
        )
        self.session.add_all(donations)
        await self.session.commit()
        await self.session.refresh(new_project)
        return new_project

    @router.patch(
        "/{project_id}",
        response_model=CharityProjectDBResponse,
        dependencies=[Depends(current_superuser)],
        summary="Изменить проект.",
    )
    async def update_charity_project(
        self,
        project_id: int,
        project_request: CharityProjectUpdateRequest,
    ) -> CharityProjectDBResponse:
        """
        Только для суперюзеров.\n
        Закрытый проект нельзя редактировать,
        также нельзя установить требуемую сумму меньше уже вложенной.
        """
        project = await charity_project_crud.get_by_id(project_id, self.session)
        await validators.update_charity_project(project, project_request, self.session)
        project = await charity_project_crud.update(
            project, project_request, self.session
        )
        return project

    @router.delete(
        "/{project_id}",
        response_model=CharityProjectDBResponse,
        dependencies=[Depends(current_superuser)],
        summary="Удалить проект.",
    )
    async def delete_charity_project(
        self,
        project_id: int,
    ) -> CharityProjectDBResponse:
        """
        Только для суперюзеров.\n
        Удаляет проект. Нельзя удалить проект, в который уже были инвестированы средства, его можно только закрыть.
        """
        project = await charity_project_crud.get_by_id(project_id, self.session)
        validators.delete_charity_project(project)
        project = await charity_project_crud.remove(project, self.session)
        return project
