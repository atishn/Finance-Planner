from sqlalchemy import Column, ForeignKey, Integer, DateTime, Unicode
from nameparser.parser import HumanName

from hr.models import Base


class Freelancer(Base):
    __tablename__ = 'freelancer'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('account.id'), nullable=False)

    first_name = Column(Unicode(40), nullable=False)
    middle_name = Column(Unicode(40), nullable=True)
    last_name = Column(Unicode(40), nullable=False)

    hourly_rate = Column(Integer, nullable=True)
    utilization = Column(Integer, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    role_id = Column(Integer, ForeignKey('role.id'))
    client_id = Column(Integer, ForeignKey('client.id'))

    #use this only if it is nonbillable
    office_id = Column(Integer, ForeignKey('office.id'))

    def __init__(self, account, name, role, start_date, end_date, hourly_rate, utilization, client, office=None):
        self.role = role
        self.account = account
        parsed_name = HumanName(name.lower())
        self.first_name = parsed_name.first
        self.middle_name = parsed_name.middle
        self.last_name = parsed_name.last

        self.client = client
        self.office = office

        self.start_date = start_date
        self.end_date = end_date
        self.hourly_rate = hourly_rate
        self.utilization = utilization

    def _name(self):
        if len(self.middle_name) > 0:
            return self.first_name + " " + self.middle_name[0] + ". " + self.last_name
        return self.first_name + " " + self.last_name

    name = property(_name)

    def _rate_per_day(self):
        return self.hourly_rate * 8 * (self.utilization / 100.0) * (5 / 7.0)

    rate_per_day = property(_rate_per_day)

    def _rate_per_day_if_employee(self):
        return self.role.loaded_salary_per_day

    rate_per_day_if_employee = property(_rate_per_day_if_employee)