from app.core.db import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, CheckConstraint
from datetime import datetime


class OverallInvestmentPerformance(Base):
    __abstract__ = True
    __table_args__ = (
        CheckConstraint('full_amount > 0'),
        CheckConstraint('invested_amount <= full_amount')
    )
    full_amount = Column(Integer)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    close_date = Column(DateTime)

    def __repr__(self):
        return (
            f'Name: {self.name}, '
            f'full_amount: {self.full_amount}, '
            f'invested_amount: {self.invested_amount}, '
            f'fully_invested: {self.fully_invested}'
        )
