from __future__ import division
from hr.models.UserUtilization import UserUtilization


class GhostClientUtilization(object):
    ghost_client = None

    year = 0

    users = {}
    ghosts = {}

    user_utilization = []
    ghost_utilization = []

    def __init__(self, ghost_client, year):
        self.ghost_client = ghost_client
        self.year = year

        self.calculateUtilization()

    def initializeVariables(self):
        self.users = {}
        self.ghosts = {}
        self.user_utilization = []
        self.ghost_utilization = []

    def calculateUtilization(self):
        self.initializeVariables()
        for user_allocation in self.ghost_client.team:
            try:
                old_user_utilization = self.users[user_allocation.user.id]
            except:
                old_user_utilization = None
            user_utilization = UserUtilization(user_allocation.user.name, user_allocation.user.role.name,
                                               user_allocation.user_id, self.year, user_allocation.start_date,
                                               user_allocation.end_date, user_allocation.utilization)
            if user_utilization.is_active:
                if old_user_utilization is None:
                    self.users[user_allocation.user_id] = user_utilization
                else:
                    old_user_utilization.addUtilization(user_utilization)
                    self.users[user_allocation.user.id] = old_user_utilization

        for ghost_allocation in self.ghost_client.ghost_team:
            try:
                old_ghost_utilization = self.ghosts[ghost_allocation.ghost_user_id]
            except:
                old_ghost_utilization = None
            ghost_utilization = UserUtilization(ghost_allocation.ghost_user.role.name,
                                                ghost_allocation.ghost_user.role.name, ghost_allocation.ghost_user_id,
                                                self.year, ghost_allocation.start_date, ghost_allocation.end_date,
                                                ghost_allocation.utilization)
            if ghost_utilization.is_active:
                if old_ghost_utilization is None:
                    self.ghosts[ghost_allocation.ghost_user_id] = ghost_utilization
                else:
                    old_ghost_utilization.addUtilization(ghost_utilization)
                    self.ghosts[ghost_allocation.ghost_user_id] = old_ghost_utilization

        self.user_utilization = self.users.values()
        self.ghost_utilization = self.ghosts.values()
        
       
