from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, PositiveInt


class DonationBase(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str]

    class Config:
        extra = Extra.forbid


class DonationCreateRequest(DonationBase):
    pass


class DonationDBResponse(DonationBase):
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class DonationAdminDBResponse(DonationDBResponse):
    user_id: int
    invested_amount: int = 0
    fully_invested: bool = False
    close_date: datetime = None
