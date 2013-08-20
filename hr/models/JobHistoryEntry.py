from sqlalchemy import Column, ForeignKey, Integer, DateTime
from hr.db import db_utc_now
from hr.models import Base
from hr.utilities import money_formatted_micro, money_formatted


class JobHistoryEntry(Base):
    __tablename__ = 'job_history'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False)

    salary = Column(Integer, nullable=True)

    def __init__(self, user, role, salary=None):
        self.user = user
        self.role = role
        self.salary = salary
        self.created_at = db_utc_now()

    def _salary_formatted(self):
        return money_formatted(self.user.office.currency, self.salary)

    salary_formatted = property(_salary_formatted)

    def _salary_formatted_micro(self):
        return money_formatted_micro(self.user.office.currency, self.salary)

    salary_formatted_micro = property(_salary_formatted_micro)
        