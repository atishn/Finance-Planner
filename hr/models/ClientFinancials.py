from __future__ import division
import bcrypt, locale, datetime, traceback
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base
from hr.models.JobHistoryEntry import JobHistoryEntry
from hr.utilities import money_formatted_micro,money_formatted,quarterly_money,quarterly_salary
from hr.models.GhostProjectRevenue import GhostProjectRevenue
from hr.models.ProjectRevenue import ProjectRevenue

class ClientFinancials(object):
    
    client = None
    
    year = 0
    usd_to_local = 1
    
    # per project or ghost project revenue
    project_revenues = []
    ghost_project_revenues = []
    
    expense_salary = [0,0,0,0,0]
    expense_ghost = [0,0,0,0,0]
    expense_freelance = [0,0,0,0,0]
    expense_freelance_if_employee = [0,0,0,0,0]
    expense_overhead = [0,0,0,0,0]
    expense_total = [0,0,0,0,0]
    
    #aggregate totals
    revenue_projects = [0,0,0,0,0]
    revenue_client_opportunities = [0,0,0,0,0]
    
    non_billable_expenses = [0,0,0,0,0]
    
    ### TODO: fix so that total revenue does not include ghost for historical--same elsewhere
    revenue_total = [0,0,0,0,0]
    
    profit = [0,0,0,0,0]
    margin = [0,0,0,0,0]

    #TODO: ADD DISCRETIONARY PER OFFICE AMOUNT THAT PEOPLE CAN ADD IN
    def __init__(self,client,year,user):
        self.client = client
        self.year=year

        self.calculateFinancials()
        
        if user.currency is not None:
            self.usd_to_local = user.currency.usd_to_currency
            self.convertToLocal()
            
    def initializeVariables(self):
        self.project_revenues = []
        self.ghost_project_revenues = []

        self.expense_salary = [0,0,0,0,0]
        self.expense_ghost = [0,0,0,0,0]
        self.expense_freelance = [0,0,0,0,0]
        self.expense_freelance_if_employee = [0,0,0,0,0]
        self.expense_overhead = [0,0,0,0,0]
        
        self.non_billable_expenses = [0,0,0,0,0]
        
        self.expense_total = [0,0,0,0,0]

        self.revenue_projects = [0,0,0,0,0]
        self.revenue_client_opportunities = [0,0,0,0,0]
        self.revenue_total = [0,0,0,0,0]

        self.profit = [0,0,0,0,0]
        self.margin = [0,0,0,0,0]
        
    def calculateFinancials(self):
        try:
            self.initializeVariables()
            for project in self.client.projects:
                if project.is_active == True:
                    revenue = quarterly_money(self.year,project.start_date,project.end_date,project.revenue_per_day,project.actual_revenues)
                    project_revenue = ProjectRevenue(project,self.year)
                    project_revenue.Q1 = revenue[0]
                    project_revenue.Q2 = revenue[1]
                    project_revenue.Q3 = revenue[2]
                    project_revenue.Q4 = revenue[3]
                    if project_revenue.Q1 > 0 or project_revenue.Q2 > 0 or project_revenue.Q3 > 0 or project_revenue.Q4 > 0:
                        self.project_revenues.append(project_revenue)
            
            for project_revenue in self.project_revenues:
                self.revenue_projects[0] += project_revenue.Q1
                self.revenue_projects[1] += project_revenue.Q2
                self.revenue_projects[2] += project_revenue.Q3
                self.revenue_projects[3] += project_revenue.Q4
    
            for ghost_project in self.client.ghost_projects:
                if ghost_project.is_active == True:
                    revenue = quarterly_money(self.year,ghost_project.start_date,ghost_project.end_date,ghost_project.revenue_per_day,None,"ghost_revenue")
                    ghost_project_revenue = GhostProjectRevenue(ghost_project,self.year)
                    ghost_project_revenue.Q1 = revenue[0]
                    ghost_project_revenue.Q2 = revenue[1]
                    ghost_project_revenue.Q3 = revenue[2]
                    ghost_project_revenue.Q4 = revenue[3]
                    if ghost_project_revenue.Q1 > 0 or ghost_project_revenue.Q2 > 0 or ghost_project_revenue.Q3 > 0 or ghost_project_revenue.Q4 > 0:
                        self.ghost_project_revenues.append(ghost_project_revenue)
        
            for ghost_project_revenue in self.ghost_project_revenues:
                self.revenue_client_opportunities[0] += ghost_project_revenue.Q1
                self.revenue_client_opportunities[1] += ghost_project_revenue.Q2
                self.revenue_client_opportunities[2] += ghost_project_revenue.Q3
                self.revenue_client_opportunities[3] += ghost_project_revenue.Q4
        
            for user_allocation in self.client.team:
                user_salary = quarterly_salary(self.year,user_allocation.user,user_allocation.start_date,user_allocation.end_date,"total",user_allocation.utilization)
                
                for x in range(0, 4):
                    self.expense_salary[x] += user_salary[x]
                    self.expense_salary[4] += user_salary[x]
                
            for ghost_allocation in self.client.ghost_team:
                salary_per_day = (ghost_allocation.ghost_user.role.loaded_salary_per_day * ghost_allocation.utilization/100) * self.usd_to_local
                ghost_salary = quarterly_money(self.year,ghost_allocation.start_date,ghost_allocation.end_date,salary_per_day,None,"ghost_salary")
                for x in range(0, 4):
                    self.expense_ghost[x] += ghost_salary[x]
                    self.expense_ghost[4] += ghost_salary[x]
        
            for freelancer in self.client.freelancers:
                comp_per_freelancer = quarterly_money(self.year,freelancer.start_date,freelancer.end_date,freelancer.rate_per_day)
                comp_per_freelancer_if_employee = quarterly_money(self.year,freelancer.start_date,freelancer.end_date,freelancer.rate_per_day_if_employee)
                
                for x in range(0,4):
                    self.expense_freelance[x] += comp_per_freelancer[x]
                    self.expense_freelance[4] += comp_per_freelancer[x]
                    self.expense_freelance_if_employee[x] += comp_per_freelancer_if_employee[x]
                    self.expense_freelance_if_employee[4] += comp_per_freelancer_if_employee[x]
                    
            percent_allocated = [0,0,0,0,0]
            total_office_salaries = self.client.office.getTotalBillableCompPerQuarter(self.year)
            total_office_overhead = self.client.office.getTotalOverheadPerQuarter(self.year)
               
            for actual_expense in self.client.actual_expenses:
                if actual_expense.quarter_end_date.year == self.year:
                    if actual_expense.quarter_end_date.month == 3:
                        self.non_billable_expenses[0] = actual_expense.expense_local
                    elif actual_expense.quarter_end_date.month == 6:
                        self.non_billable_expenses[1] = actual_expense.expense_local
                    elif actual_expense.quarter_end_date.month == 9:
                        self.non_billable_expenses[2] = actual_expense.expense_local
                    elif actual_expense.quarter_end_date.month == 12:
                        self.non_billable_expenses[3] = actual_expense.expense_local
            
            self.non_billable_expenses[4] = self.non_billable_expenses[0] + self.non_billable_expenses[1] + self.non_billable_expenses[2] + self.non_billable_expenses[3]
                 
            for x in range(0,5):
                if total_office_salaries[x] > 0:
                    percent_allocated[x] = self.expense_salary[x] / total_office_salaries[x]
                else:
                    percent_allocated[x] = 0
                if percent_allocated[x] > 0:
                    self.expense_overhead[x] = total_office_overhead[x] * percent_allocated[x]
                else:
                    self.expense_overhead[x] = 0
                self.expense_total[x] += self.non_billable_expenses[x] + self.expense_ghost[x] + self.expense_freelance[x] + self.expense_salary[x] + self.expense_overhead[x]
        
            for x in range(0,4):
                self.revenue_client_opportunities[4] += self.revenue_client_opportunities[x]
                self.revenue_projects[4] += self.revenue_projects[x]
                self.revenue_total[x] = self.revenue_projects[x] + self.revenue_client_opportunities[x]
                self.revenue_total[4] += self.revenue_total[x]
            
                self.profit[x] = self.revenue_total[x] - self.expense_total[x]
                self.profit[4] += self.profit[x]
          
                if self.revenue_total[x] > 0: 
                    self.margin[x] = int((self.profit[x] / self.revenue_total[x]) * 100)
                else:
                    self.margin[x] = 0
        
            if self.revenue_total[4] > 0:
                self.margin[4] = int((self.profit[4] / self.revenue_total[4]) * 100)
            else:
                self.margin[4] = 0
        except:
            traceback.print_exc()

    def convertToLocal(self):
        if usd_to_local == 1:
            return
        
        try:
            project_revenues_temp = []
            for project_revenue in self.project_revenues:
                project_revenue.Q1 = project_revenue.Q1 * self.usd_to_local
                project_revenue.Q2 = project_revenue.Q2 * self.usd_to_local
                project_revenue.Q3 = project_revenue.Q3 * self.usd_to_local
                project_revenue.Q4 = project_revenue.Q4 * self.usd_to_local
                project_revenues_temp.append(project_revenue)
            self.project_revenues = project_revenues_temp
        
            ghost_project_revenues_temp = []
            for ghost_project_revenue in self.ghost_project_revenues:
                ghost_project_revenue.Q1 = ghost_project_revenue.Q1 * self.usd_to_local
                ghost_project_revenue.Q2 = ghost_project_revenue.Q2 * self.usd_to_local
                ghost_project_revenue.Q3 = ghost_project_revenue.Q3 * self.usd_to_local
                ghost_project_revenue.Q4 = ghost_project_revenue.Q4 * self.usd_to_local
                ghost_project_revenues_temp.append(project_revenue)
            self.ghost_project_revenues = ghost_project_revenues_temp
        
            for x in range(0,5):
                self.expense_salary[x] = self.expense_salary[x] * self.usd_to_local
                self.expense_ghost[x] = self.expense_ghost[x] * self.usd_to_local
                self.expense_freelance[x] = self.expense_freelance[x] * self.usd_to_local
                self.expense_overhead[x] = self.expense_overhead[x] * self.usd_to_local
                self.non_billable_expenses[x] = self.non_billable_expenses[x] * self.usd_to_local
                self.expense_total[x] = self.expense_total[x] * self.usd_to_local

                self.revenue_projects[x] = self.revenue_projects[x] * self.usd_to_local
                self.revenue_client_opportunities[x] = self.revenue_client_opportunities[x] * self.usd_to_local
                self.revenue_total[x] = self.revenue_total[x] * self.usd_to_local

                self.profit[x] = self.profit[x] * self.usd_to_local
        except:
            traceback.print_exc()
            
            