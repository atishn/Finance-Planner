from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean
from hr.db import db_utc_now
from hr.models import Base


class SkillsetEntry(Base):
    __tablename__ = 'skillset_entry'
    id = Column(Integer, primary_key=True)

    created_at = Column(DateTime, nullable=False)

    review_id = Column(Integer, ForeignKey('review.id'))
    skillset_id = Column(Integer, ForeignKey('skillset.id'))
    is_midyear = Column(Boolean)
    ranking = Column(Integer, nullable=True)

    def __init__(self, review, is_midyear, skillset, ranking):
        self.review = review
        self.is_midyear = is_midyear
        self.skillset = skillset
        self.ranking = ranking
        self.created_at = db_utc_now()

    def _ranking_as_text(self):
        if self.ranking == 4:
            return "Always"
        if self.ranking == 3:
            return "Often"
        if self.ranking == 2:
            return "Sometimes"
        if self.ranking == 1:
            return "Never"
        return "None"

    ranking_as_text = property(_ranking_as_text)
