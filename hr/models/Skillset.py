from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode
from sqlalchemy.orm import relationship

from hr.db import db_utc_now
from hr.models import Base


class Skillset(Base):
    __tablename__ = 'skillset'
    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)

    name = Column(Unicode(140), nullable=False)

    skillset_category_id = Column(Integer, ForeignKey('skillset_category.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False)
    skillset_entrys = relationship('SkillsetEntry', backref='skillset')

    def __init__(self, name, role, skillset_category):
        self.name = name
        self.skillset_category = skillset_category
        self.role = role
        self.created_at = db_utc_now()
        self.is_active = True