from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
)

from app.models.base_model import OverallInvestmentPerformance


class Donation(OverallInvestmentPerformance):
    user_id = Column(Integer, ForeignKey("user.id"))
    comment = Column(Text)

    def repr(self):
        return (
            f'User_id: {self.user_id}, '
            f'{super().__repr__()}'
        )
