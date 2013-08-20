from __future__ import division
from sqlalchemy import Column, Float, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship
from hr.models import Base


class Currency(Base):
    __tablename__ = 'currency'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    name = Column(Unicode(3), nullable=False)
    currency_to_usd = Column(Float, nullable=False)

    users = relationship('User', backref='currency')

    def __init__(self, name, account, currency_to_usd):
        self.name = name.lower()
        self.account = account
        self.currency_to_usd = currency_to_usd

    def _usd_to_currency(self):
        return 1 / self.currency_to_usd

    usd_to_currency = property(_usd_to_currency)