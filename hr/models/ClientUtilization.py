from __future__ import division
from hr.models.UserUtilization import UserUtilization


class ClientUtilization(object):
    client = None

    year = 0
    ### fix this so multiple users and ghosts are supported - start with dict
    users = {}
    ghosts = {}
    freelancers = {}
    user_utilization = []
    ghost_utilization = []
    freelance_utilization = []

    def __init__(self, client, year):
        self.client = client
        self.year = year

        self.calculateUtilization()

    def initializeVariables(self):
        self.users = {}
        self.ghosts = {}
        self.freelancers = {}
        self.user_utilization = []
        self.ghost_utilization = []
        self.freelance_utilization = []

    def calculateUtilization(self):
        self.initializeVariables()
        for user_allocation in self.client.team:
            try:
                old_user_utilization = self.users[user_allocation.user.id]
            except:
                old_user_utilization = None
            user_utilization = UserUtilization(user_allocation.user.name, user_allocation.user.role,
                                               user_allocation.user_id, self.year, user_allocation.start_date,
                                               user_allocation.end_date, user_allocation.utilization)
            if user_utilization.is_active:
                if old_user_utilization is None:
                    self.users[user_allocation.user_id] = user_utilization
                else:
                    old_user_utilization.addUtilization(user_utilization)
                    self.users[user_allocation.user.id] = old_user_utilization

        for ghost_allocation in self.client.ghost_team:
            try:
                old_ghost_utilization = self.ghosts[ghost_allocation.ghost_user_id]
            except:
                old_ghost_utilization = None
            ghost_utilization = UserUtilization(ghost_allocation.ghost_user.role, ghost_allocation.ghost_user.role.name,
                                                ghost_allocation.ghost_user_id, self.year, ghost_allocation.start_date,
                                                ghost_allocation.end_date, ghost_allocation.utilization)
            if ghost_utilization.is_active:
                if old_ghost_utilization is None:
                    self.ghosts[ghost_allocation.ghost_user_id] = ghost_utilization
                else:
                    old_ghost_utilization.addUtilization(ghost_utilization)
                    self.ghosts[ghost_allocation.ghost_user_id] = old_ghost_utilization

        for freelancer in self.client.freelancers:
            try:
                old_freelancer_utilization = self.freelancers[freelancer.id]
            except:
                old_freelancer_utilization = None
            freelancer_utilization = UserUtilization(freelancer.name, freelancer.role, freelancer.id, self.year,
                                                     freelancer.start_date, freelancer.end_date, freelancer.utilization)
            if freelancer_utilization.is_active:
                if old_freelancer_utilization is None:
                    self.freelancers[freelancer.id] = freelancer_utilization
                else:
                    old_freelancer_utilization.addUtilization(freelancer_utilization)
                    self.freelancers[freelancer.id] = old_freelancer_utilization

        self.user_utilization = self.users.values()
        self.ghost_utilization = self.ghosts.values()
        self.freelancer_utilization = self.freelancers.values()
        
       
            