from __future__ import division

import bcrypt
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode
from sqlalchemy.orm import relationship, backref
from nameparser.parser import HumanName

from hr.db import db_utc_now
from hr.models import Base
from hr.models.JobHistoryEntry import JobHistoryEntry
from hr.utilities import money_formatted_micro, money_formatted
from hr.models.ManyToMany import permissions_office_financials, permissions_office_pipeline, permissions_office_utilization, permissions_client_pipeline, permissions_client_financials, permissions_client_utilization, permissions_department_financials, permissions_department_utilization


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)
    account_id = Column(Integer, ForeignKey('account.id'), nullable=False)

    #depricated; used for the reviews tool
    permissions_id = Column(Integer, ForeignKey('permissions.id'), nullable=True)

    start_date = Column(DateTime, nullable=False)

    first_name = Column(Unicode(40), nullable=False)
    middle_name = Column(Unicode(40), nullable=True)
    last_name = Column(Unicode(40), nullable=False)

    password = Column(Unicode(60), nullable=True)
    employee_number = Column(Integer, nullable=True)
    email = Column(Unicode(120), nullable=False)
    salary = Column(Integer, nullable=False)

    salary_history = relationship('Salary', backref='user')

    role_id = Column(Integer, ForeignKey('role.id'))
    #role = relationship("Role",foreign_keys="User.role_id")

    office_id = Column(Integer, ForeignKey('office.id'), nullable=True)
    department_id = Column(Integer, ForeignKey('department.id'), nullable=True)

    manager_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    direct_reports = relationship('User', backref=backref('manager', remote_side=[id]))
    job_history = relationship('JobHistoryEntry', backref='user')
    reviews = relationship('Review', backref='user')
    feedback_given = relationship('Feedback', backref='user')

    next_role_id = Column(Integer, ForeignKey('role.id'), nullable=True)
    next_role = relationship("Role", foreign_keys="User.next_role_id")

    allocations = relationship('UserAllocation', backref='user')

    percent_billable = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)

    is_administrator = Column(Boolean, nullable=False)
    is_hr_administrator = Column(Boolean, nullable=False)

    permissions_office_financials = relationship("Office", secondary=permissions_office_financials)
    permissions_office_pipeline = relationship("Office", secondary=permissions_office_pipeline)
    permissions_office_utilization = relationship("Office", secondary=permissions_office_utilization)

    permissions_client_pipeline = relationship("Client", secondary=permissions_client_pipeline)
    permissions_client_financials = relationship("Client", secondary=permissions_client_financials)
    permissions_client_utilization = relationship("Client", secondary=permissions_client_utilization)

    permissions_department_financials = relationship("Department", secondary=permissions_department_financials)
    permissions_department_utilization = relationship("Department", secondary=permissions_department_utilization)

    permissions_global_pipeline = Column(Boolean, nullable=False)
    permissions_global_financials = Column(Boolean, nullable=False)
    permissions_global_utilization = Column(Boolean, nullable=False)

    currency_id = Column(Integer, ForeignKey('currency.id'))

    def __init__(self, account, name, email, office, role, salary, start_date):
        self.account = account

        parsed_name = HumanName(name.lower())
        self.first_name = parsed_name.first
        self.middle_name = parsed_name.middle
        self.last_name = parsed_name.last

        self.email = email.lower()

        self.is_administrator = False
        self.is_hr_administrator = False
        self.permissions_global_pipeline = False
        self.permissions_global_financials = False
        self.permissions_global_utilization = False

        self.office = office
        self.role = role
        self.salary = salary

        self.is_active = True

        self.created_at = db_utc_now()
        self.start_date = db_utc_now()
        self.percent_billable = 100

        if role.department is not None:
            self.department = self.role.department
        else:
            self.department = None
            #self.next_role = self.role.next_role

        self.employee_number = 0

        self.end_date = None
        self.start_date = start_date

        jh = JobHistoryEntry(self, role, salary)
        self.job_history.append(jh)

    def set_password(self, password):
        if password:
            self.password = bcrypt.hashpw(unicode(password).encode('utf-8'), bcrypt.gensalt())

    def is_valid_password(self, password):
        if not self.password:
            return False
        return bcrypt.hashpw(unicode(password).encode('utf-8'), unicode(self.password).encode('utf-8')) == unicode(self.password).encode('utf-8')

    def _review_status(self):
        return "None Pending"

    review_status = property(_review_status)

    def _is_a_manager(self):
        if self.direct_reports is None:
            return False
        if len(self.direct_reports) == 0:
            return False
        return True

    is_a_manager = property(_is_a_manager)

    def _last_raise(self):
        last_raise = None
        raise_happened = False
        for jh in self.job_history:
            if jh.salary == self.salary:
                if last_raise is None:
                    last_raise = jh.created_at
                elif last_raise > jh.created_at:
                    last_raise = jh.created_at
            else:
                raise_happened = True
        if raise_happened:
            return last_raise
        return None

    last_raise = property(_last_raise)

    def _last_promotion(self):
        last_promotion = None
        for jh in self.job_history:
            if jh.role_id != self.role_id:
                if last_promotion is None:
                    last_promotion = jh.created_at
                elif last_promotion < jh.created_at:
                    last_promotion = jh.created_at
        return last_promotion

    last_promotion = property(_last_promotion)

    manager_is_accessible_to_user = False

    def _salary_formatted(self):
        return money_formatted(self.user.office.currency, self.salary)

    salary_formatted = property(_salary_formatted)

    def _salary_formatted_micro(self):
        return money_formatted_micro(self.office.currency, self.salary)
        return self.salary

    salary_formatted_micro = property(_salary_formatted_micro)

    def _salary_per_day(self):
        return self.salary / 365

    salary_per_day = property(_salary_per_day)

    def _loaded_salary_per_day(self):
        return (self.salary + (self.salary * self.account.benefits_and_bonus / 100)) / 365

    loaded_salary_per_day = property(_loaded_salary_per_day)

    def _loaded_non_billable_salary_per_day(self):
        return ((self.salary + (self.salary * self.account.benefits_and_bonus / 100)) * (
            1 - self.percent_billable / 100)) / 365

    loaded_non_billable_salary_per_day = property(_loaded_non_billable_salary_per_day)

    def _loaded_billable_salary_per_day(self):
        return ((self.salary + self.salary * self.account.benefits_and_bonus / 100) * self.percent_billable / 100) / 365

    loaded_billable_salary_per_day = property(_loaded_billable_salary_per_day)

    def _is_department_head(self):
        for department in self.account.departments:
            if department.manager_id == self.id:
                return True
        return False

    is_department_head = property(_is_department_head)

    def _name(self):
        if len(self.middle_name) > 0:
            return self.first_name + " " + self.middle_name[0] + ". " + self.last_name
        else:
            return self.first_name + " " + self.last_name

    name = property(_name)

    def can_access_office(self, office, kind):
        if self.is_administrator:
            return True
        if kind == "financials":
            if self.permissions_global_financials:
                return True
            for off in self.permissions_office_financials:
                if off.id == office.id:
                    return True
        elif kind == "utilization":
            if self.permissions_global_utilization:
                return True
            for off in self.permissions_office_utilization:
                if off.id == office.id:
                    return True
        elif kind == "pipeline":
            if self.permissions_global_pipeline:
                return True
            for off in self.permissions_office_pipeline:
                if off.id == office.id:
                    return True
        return False

    def can_access_client(self, client, kind):
        if self.can_access_office(client.office, kind):
            return True
        if kind == "financials":
            for c in self.permissions_client_financials:
                if c.id == client.id:
                    return True
        elif kind == "utilization":
            for c in self.permissions_client_utilization:
                if c.id == client.id:
                    return True
        elif kind == "pipeline":
            for c in self.permissions_client_pipeline:
                if c.id == client.id:
                    return True
        return False

    def can_access_department(self, department, kind):
        if self.is_administrator:
            return True
        if kind == "financials":
            if self.permissions_global_financials:
                return True
            for dept in self.permissions_department_financials:
                if dept.id == department.id:
                    return True
        elif kind == "utilization":
            if self.permissions_global_utilization:
                return True
            for dept in self.permissions_department_utilization:
                if dept.id == department.id:
                    return True
        return False
    