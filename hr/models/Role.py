from __future__ import division

from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode
from sqlalchemy.orm import relationship, backref

from hr.db import db_utc_now
from hr.models import Base


class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('account.id'))

    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)

    name = Column(Unicode(40), nullable=False)

    department_id = Column(Integer, ForeignKey('department.id'))
    users = relationship('User', backref='role', foreign_keys="User.role_id")
    skillsets = relationship('Skillset', backref='role')
    #reviews = relationship('Review',backref='role',foreign_keys="Review.role_id")

    salary_low = Column(Integer, nullable=False)
    salary_high = Column(Integer, nullable=False)

    job_history_of_role = relationship('JobHistoryEntry', backref='role')

    next_role_id = Column(Integer, ForeignKey('role.id'), nullable=True)
    previous_roles = relationship('Role', backref=backref('next_role', remote_side=[id]))

    freelancers = relationship('Freelancer', backref='role')
    ghost_users = relationship('GhostUser', backref='role')

    def __init__(self, account, name, department, salary_high, salary_low):
        self.account = account
        self.name = name.lower()
        self.department = department
        self.created_at = db_utc_now()
        self.salary_high = salary_high
        self.salary_low = salary_low
        self.is_active = True

    def _active_users_count(self):
        count = 0
        for user in self.users:
            if user.is_active:
                count = count + 1
        return count

    active_users_count = property(_active_users_count)

    def _skillset_count(self):
        try:
            return len(self.skillsets)
        except:
            return 0

    skillset_count = property(_skillset_count)

    # eventually this should not be used and instead use an average of the actual people in this role
    def _salary_middle(self):
        return (self.salary_high + self.salary_low) / 2

    salary_middle = property(_salary_middle)

    def _loaded_salary_per_day(self):
        return (self.salary_middle + (self.salary_middle * self.account.benefits_and_bonus / 100)) / 365

    loaded_salary_per_day = property(_loaded_salary_per_day)
        
        