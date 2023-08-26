
# Класс «обёртки»
from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser

from app.crud.charity_project import charity_project_crud
from app.services.google_api import (set_user_permissions, spreadsheets_create,
                                     spreadsheets_update_value)
# Создаём экземпляр класса APIRouter
router = APIRouter()


@router.get(
    '/',
    # Тип возвращаемого эндпоинтом ответа
    response_model=list[dict],
    # Определяем зависимости
    dependencies=[Depends(current_superuser)],
)
async def get_report(
        # Сессия
        session: AsyncSession = Depends(get_async_session),
        # «Обёртка»
        wrapper_services: Aiogoogle = Depends(get_service)

):
    """Только для суперюзеров."""
    close_projects = await charity_project_crud.get_projects_by_completion_rate(
        session
    )
    spreedsheet_id = await spreadsheets_create(wrapper_services)
    await set_user_permissions(spreedsheet_id, wrapper_services)
    await spreadsheets_update_value(spreedsheet_id,
                                    close_projects,
                                    wrapper_services)
    return close_projects
