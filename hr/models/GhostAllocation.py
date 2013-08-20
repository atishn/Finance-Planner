from sqlalchemy import Column, ForeignKey, Integer, DateTime
from hr.models import Base


class GhostAllocation(Base):
    __tablename__ = 'ghost_allocation'
    id = Column(Integer, primary_key=True)

    ghost_user_id = Column(Integer, ForeignKey('ghost_user.id'))
    client_id = Column(Integer, ForeignKey('client.id'))
    ghost_client_id = Column(Integer, ForeignKey('ghost_client.id'))
    utilization = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    def __init__(self, ghost_user, client, ghost_client, utilization, start_date, end_date):
        self.ghost_user = ghost_user
        self.client = client
        self.ghost_client = ghost_client
        self.utilization = utilization
        self.start_date = start_date
        self.end_date = end_date
