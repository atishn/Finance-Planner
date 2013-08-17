from __future__ import division
import bcrypt, locale, datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base
from hr.models.OfficeFinancials import OfficeFinancials
from hr.models.OfficeUtilization import OfficeUtilization
from hr.utilities import days_employed_per_year, quarterly_money


class Office(Base):
    __tablename__ = 'office'
    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)
    account_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    #currency = Column(Unicode(40),nullable=False)

    name = Column(Unicode(40), nullable=False)

    users = relationship('User', backref='office')
    clients = relationship('Client', backref='office')
    ghost_users = relationship('GhostUser', backref='office')
    ghost_clients = relationship('GhostClient', backref='office')

    allocated_salary_expense = Column(Integer, nullable=False)
    sga_expense = Column(Integer, nullable=False)

    freelancers = relationship('Freelancer', backref='office')

    actual_expenses = relationship('ActualExpense', backref='office')

    def __init__(self, name, account):
        self.name = name.lower()
        self.account = account
        self.created_at = db_utc_now()
        self.is_active = True
        self.allocated_salary_expense = 0
        self.sga_expense = 0


    # old -- unclear if it works properly or is used
    def _expense_overhead(self):
        total_salary = 0
        for user in self.users:
            total_salary = total_salary + (user.salary * user.percent_billable / 100)

        try:
            return int(((self.allocated_salary_expense + self.sga_expense) / total_salary) * 100)
        except:
            return 0

    expense_overhead = property(_expense_overhead)

    def getFinancials(self, year, user):
        return OfficeFinancials(self, year, user)

    def getUtilization(self, year):
        return OfficeUtilization(self, year)

    def getTotalBillableCompPerQuarter(self, year):
        total_comp = [0, 0, 0, 0, 0]
        for u in self.users:
            end_date = u.end_date
            if end_date is None:
                next_year = int(year) + 1
                end_date = datetime.datetime(next_year, 1, 1)
            quarterly_comp = quarterly_money(year, u.start_date, end_date, u.loaded_billable_salary_per_day)
            for x in range(0, 4):
                total_comp[x] += quarterly_comp[x]
                total_comp[4] += quarterly_comp[x]
        return total_comp


    def getTotalOverheadPerQuarter(self, year):
        per_quarter_overhead = (self.allocated_salary_expense + self.sga_expense) / 4
        total_overhead = [per_quarter_overhead, per_quarter_overhead, per_quarter_overhead, per_quarter_overhead,
                          self.allocated_salary_expense + self.sga_expense]
        for u in self.users:
            if u.end_date is None:
                u.end_date = datetime.datetime(int(year), 12, 31)
            if u.percent_billable < 100:
                quarterly_non_billable = quarterly_money(year, u.start_date, u.end_date,
                                                         u.loaded_non_billable_salary_per_day)
                for x in range(0, 4):
                    total_overhead[x] += quarterly_non_billable[x]
                    total_overhead[4] += quarterly_non_billable[x]
        for f in self.freelancers:
            quarterly_nb_freelancers = quarterly_money(year, f.start_date, f.end_date, f.rate_per_day)
            for x in range(0, 4):
                total_overhead[x] += quarterly_nb_freelancers[x]
                total_overhead[4] += quarterly_nb_freelancers[x]
        return total_overhead
            
        
        
    