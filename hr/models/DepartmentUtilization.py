from __future__ import division
import bcrypt, locale, datetime, traceback
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base
from hr.utilities import money_formatted_micro, money_formatted, quarterly_money
from hr.models.UserUtilization import UserUtilization
from hr.models.UserFullUtilization import UserFullUtilization
from hr.models.UserFullUtilizationEntry import UserFullUtilizationEntry


class DepartmentUtilization(object):
    department = None

    year = 0
    users = {}
    users_aggregate = {}
    ghosts = {}
    freelancers = {}
    department_freelancers = {}
    user_utilization = []
    user_aggregate_utilization = []
    ghost_utilization = []
    freelance_utilization = []
    bench = []
    non_billable = []
    ghosts_not_allocated = []

    user_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    utilization_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    total = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def __init__(self, department, year):
        self.department = department
        self.year = year

        self.calculateUtilization()

    def initializeVariables(self):
        self.users = {}
        self.users_aggregate = {}
        self.ghosts = {}
        self.freelancers = {}
        self.department_freelancers = {}
        self.user_utilization = []
        self.user_aggregate_utilization = []
        self.ghost_utilization = []
        self.freelance_utilization = []
        self.bench = []
        self.non_billable = []
        self.ghosts_not_allocated = []
        self.user_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.utilization_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.total = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def calculateUtilization(self):
        try:
            self.initializeVariables()
            for client in self.department.account.clients:
                client_utilization = client.getUtilization(self.year)
                for user_utilization in client_utilization.user_utilization:
                    if user_utilization.role.department_id != self.department.id:
                        continue
                    try:
                        ufu = self.users[user_utilization.id]
                    except:
                        ufu = None
                    try:
                        uau = self.users_aggregate[user_utilization.id]
                    except:
                        uau = None
                    if ufu == None:
                        ufu = UserFullUtilization(user_utilization.name, user_utilization.role, user_utilization.id)
                    if uau == None:
                        uau = user_utilization
                    for x in range(0, 12):
                        if user_utilization.utilization[x] is not 0:
                            if not ufu.utilization[x]:
                                ufu.utilization[x] = [UserFullUtilizationEntry(client, user_utilization.utilization[x])]
                            else:
                                ufu.utilization[x].append(
                                    UserFullUtilizationEntry(client, user_utilization.utilization[x]))
                                #if not uau.utilization[x] or uau.utilization[x] == 0:
                                #    uau.utilization[x] = user_utilization.utilization[x]
                                #else:
                                #    uau.utilization[x] += user_utilization.utilization[x]

                    self.users[user_utilization.id] = ufu
                    self.users_aggregate[user_utilization.id] = uau

                for ghost_utilization in client_utilization.ghost_utilization:
                    if ghost_utilization.role.department_id != self.department.id:
                        continue
                    try:
                        ufu = self.ghosts[ghost_utilization.id]
                    except:
                        ufu = None
                    if ufu == None:
                        ufu = UserFullUtilization(ghost_utilization.name, ghost_utilization.role, ghost_utilization.id)
                    for x in range(0, 12):
                        if ghost_utilization.utilization[x] is not 0:
                            if not ufu.utilization[x]:
                                ufu.utilization[x] = [
                                    UserFullUtilizationEntry(client, ghost_utilization.utilization[x])]
                            else:
                                ufu.utilization[x].append(
                                    UserFullUtilizationEntry(client, ghost_utilization.utilization[x]))

                    self.ghosts[ghost_utilization.id] = ufu

                for freelance_utilization in client_utilization.freelancer_utilization:
                    if freelance_utilization.role.department_id != self.department.id:
                        continue
                    try:
                        ufu = self.freelancers[freelance_utilization.id]
                    except:
                        ufu = None
                    if ufu == None:
                        ufu = UserFullUtilization(freelance_utilization.name, freelance_utilization.role,
                                                  freelance_utilization.id)
                    for x in range(0, 12):
                        if freelance_utilization.utilization[x] is not 0:
                            if not ufu.utilization[x]:
                                ufu.utilization[x] = [
                                    UserFullUtilizationEntry(client, freelance_utilization.utilization[x])]
                            else:
                                ufu.utilization[x].append(
                                    UserFullUtilizationEntry(client, freelance_utilization.utilization[x]))

                    self.freelancers[freelance_utilization.id] = ufu

            for ghost_client in self.department.account.ghost_clients:
                ghost_client_utilization = ghost_client.getUtilization(self.year)
                for user_utilization in ghost_client_utilization.user_utilization:
                    if user_utilization.role.department_id != self.department.id:
                        continue
                    try:
                        ufu = self.users[user_utilization.id]
                    except:
                        ufu = None
                    try:
                        uau = self.users_aggregate[user_utilization.id]
                    except:
                        uau = None
                    if ufu == None:
                        ufu = UserFullUtilization(user_utilization.name, user_utilization.role, user_utilization.id)
                    if uau == None:
                        uau = user_utilization
                    for x in range(0, 12):
                        if user_utilization.utilization[x] is not 0:
                            ufu.utilization[x].append(
                                UserFullUtilizationEntry(None, user_utilization.utilization[x], ghost_client))
                            if not uau.utilization[x] or uau.utilization[x] == 0:
                                uau.utilization[x] = user_utilization.utilization[x]
                            else:
                                uau.utilization[x] += user_utilization.utilization[x]

                    self.users[user_utilization.id] = ufu
                    self.users_aggregate[user_utilization.id] = uau
                for ghost_utilization in ghost_client_utilization.ghost_utilization:
                    if ghost_utilization.role.department_id != self.department.id:
                        continue
                    try:
                        ufu = self.ghosts[ghost_utilization.id]
                    except:
                        ufu = None
                    if ufu == None:
                        ufu = UserFullUtilization(ghost_utilization.name, ghost_utilization.role, ghost_utilization.id)
                    for x in range(0, 12):
                        if ghost_utilization.utilization[x] is not 0:
                            if not ufu.utilization[x]:
                                ufu.utilization[x] = [
                                    UserFullUtilizationEntry(None, ghost_utilization.utilization[x], ghost_client)]
                            else:
                                ufu.utilization[x].append(
                                    UserFullUtilizationEntry(None, ghost_utilization.utilization[x], ghost_client))
                    self.ghosts[ghost_utilization.id] = ufu

            for freelancer in self.department.account.freelancers:
                if freelancer.role.department_id != self.department.id:
                    continue
                try:
                    old_freelancer_utilization = self.department_freelancers[freelancer.id]
                except:
                    old_freelancer_utilization = None
                freelancer_utilization = UserUtilization(freelancer.name, freelancer.role.name, freelancer.id,
                                                         self.year, freelancer.start_date, freelancer.end_date,
                                                         freelancer.utilization)
                if freelancer_utilization.is_active:
                    if old_freelancer_utilization is None:
                        self.department_freelancers[freelancer.id] = freelancer_utilization
                    else:
                        old_freelancer_utilization.addUtilization(freelancer_utilization)
                        self.department_freelancers[freelancer.id] = old_freelancer_utilization

            department_freelancer_utilization = self.department_freelancers.values()
            for freelance_utilization in department_freelancer_utilization:
                if freelance_utilization.role.department_id != self.department.id:
                    continue
                try:
                    ufu = self.freelancers[freelance_utilization.id]
                except:
                    ufu = None
                if ufu == None:
                    ufu = UserFullUtilization(freelance_utilization.name, freelance_utilization.role,
                                              freelance_utilization.id)
                for x in range(0, 12):
                    if freelance_utilization.utilization[x] is not 0:
                        if not ufu.utilization[x]:
                            ufu.utilization[x] = [UserFullUtilizationEntry(None, freelance_utilization.utilization[x])]
                        else:
                            ufu.utilization[x].append(
                                UserFullUtilizationEntry(None, freelance_utilization.utilization[x]))
                    self.freelancers[freelance_utilization.id] = ufu

            self.user_utilization = self.users.values()
            self.user_aggregate_utilization = self.users_aggregate.values()
            self.ghost_utilization = self.ghosts.values()
            self.freelance_utilization = self.freelancers.values()

            for uau in self.user_aggregate_utilization:
                for x in range(0, 12):
                    self.utilization_count[x] += uau.utilization[x]
                    self.user_count[x] += 1

            for x in range(0, 12):
                if self.user_count[x] == 0:
                    self.total[x] = 0
                elif self.utilization_count[x] == 0:
                    self.total[x] = 0
                else:
                    self.total[x] = self.utilization_count[x] / self.user_count[x]

            for user in self.department.account.users:
                if user.id not in self.users and user in self.department.users:
                    if user.percent_billable > 0:
                        self.bench.append(user)
                    else:
                        self.non_billable.append(user)

            for ghost_user in self.department.account.ghost_users:
                if ghost_user in self.department.ghost_users:
                    try:
                        ghost_is_allocated = self.ghosts[ghost_user.id]
                    except:
                        self.ghosts_not_allocated.append(ghost_user)
        except:
            traceback.print_exc()
            
                    
