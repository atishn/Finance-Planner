from __future__ import division
import bcrypt, locale, datetime, traceback
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base
from hr.utilities import money_formatted_micro,money_formatted,quarterly_money,quarterly_salary
from hr.models.ClientFinancials import ClientFinancials
from hr.models.GhostClientFinancials import GhostClientFinancials
from hr.models.ProjectRevenue import ProjectRevenue

class DepartmentFinancials(object):
    
    user = None
    department = None
    usd_to_local = 1
    year = 0
    
    # salary of every user across departments
    all_salary = [0,0,0,0,0]
    
    project_revenues = []
    ghost_project_revenues = []
    ghost_project_revenues_from_ghost_clients = []
    ghost_project_revenues_from_tbg = []

    expense_salary_billable = [0,0,0,0,0]
    expense_salary_non_billable = [0,0,0,0,0]
    expense_salary_bench = [0,0,0,0,0]
    expense_salary_prospects = [0,0,0,0,0]
    expense_salary_tbg = [0,0,0,0,0]
    expense_open_req_salary_billable = [0,0,0,0,0]
    expense_open_req_salary_non_billable = [0,0,0,0,0]
    expense_open_req_salary_bench = [0,0,0,0,0]
    expense_open_req_salary_prospects = [0,0,0,0,0]
    expense_open_req_salary_tbg = [0,0,0,0,0]
    
    expense_freelance_billable = [0,0,0,0,0]
    expense_freelance_non_billable = [0,0,0,0,0]
    
    non_billable_expenses = [0,0,0,0,0]
    
    expense_salary_global = [0,0,0,0,0]
    expense_sga = [0,0,0,0,0]
    expense_total = [0,0,0,0,0]
    
    revenue_closed = [0,0,0,0,0]
    revenue_client_opportunities = [0,0,0,0,0]
    revenue_prospects = [0,0,0,0,0]
    revenue_prospects_weighted = [0,0,0,0,0]
    revenue_tbg = [0,0,0,0,0]
    revenue_total = [0,0,0,0,0]
    
    profit = [0,0,0,0,0]
    margin = [0,0,0,0,0]
    
    # temp variables:
    full_open_req_billable = [0,0,0,0,0] 
    total_open_req_salary = [0,0,0,0,0]
    total_salary = [0,0,0,0,0]
    full_billable_salary = [0,0,0,0,0]

    #TODO: ADD DISCRETIONARY PER OFFICE AMOUNT THAT PEOPLE CAN ADD IN
    def __init__(self,department,year,user):
        self.department = department
        self.year = year
        self.user = user

        if user.currency is not None:
            self.usd_to_local = user.currency.usd_to_currency
            
        self.calculateFinancials()
    
    def initializeVariables(self):
        
        self.project_revenues = []
        self.ghost_project_revenues = []
        self.ghost_project_revenues_from_ghost_clients = []
        self.ghost_project_revenues_from_tbg = []
        
        self.expense_salary_billable = [0,0,0,0,0]
        self.expense_salary_non_billable = [0,0,0,0,0]
        self.expense_salary_bench = [0,0,0,0,0]
        self.expense_salary_prospects = [0,0,0,0,0]
        self.expense_salary_tbg = [0,0,0,0,0]
        self.expense_open_req_billable = [0,0,0,0,0]
        self.expense_open_req_non_billable = [0,0,0,0,0]
        self.expense_open_req_bench = [0,0,0,0,0]
        self.expense_open_req_prospects = [0,0,0,0,0]
        self.expense_open_req_tbg = [0,0,0,0,0]

        self.expense_freelance_billable = [0,0,0,0,0]
        self.expense_freelance_non_billable = [0,0,0,0,0]

        self.expense_salary_global = [0,0,0,0,0]
        self.expense_sga = [0,0,0,0,0]

        # total across all offices
        self.all_expense_salary_global = [0,0,0,0,0]
        self.all_expense_sga = [0,0,0,0,0]
               
        self.non_billable_expenses = [0,0,0,0,0]
        self.expense_total = [0,0,0,0,0]

        self.revenue_closed = [0,0,0,0,0]
        self.revenue_client_opportunities = [0,0,0,0,0]
        self.revenue_prospects = [0,0,0,0,0]
        self.revenue_prospects_weighted = [0,0,0,0,0]
        self.revenue_tbg = [0,0,0,0,0]
        self.revenue_total = [0,0,0,0,0]

        self.profit = [0,0,0,0,0]
        self.margin = [0,0,0,0,0]
        
        # temp variables:
        self.full_open_req_billable = [0,0,0,0,0] 
        self.total_open_req = [0,0,0,0,0]
        self.total_salary = [0,0,0,0,0]
        self.full_billable_salary = [0,0,0,0,0]
        
    def calculateFinancials(self):
        self.initializeVariables()
        
        try:
            for project in self.user.account.projects:
                if project.is_active and project.client.is_active:
                    for budget_allocation in project.budget_allocations:
                        if budget_allocation.department_id == self.department.id:
                            revenue = quarterly_money(self.year,project.start_date,project.end_date,project.revenue_per_day,project.actual_revenues)
                            project_revenue = ProjectRevenue(project,self.year)
                            project_revenue.Q1 = revenue[0] * (budget_allocation.percent_allocation/100)
                            project_revenue.Q2 = revenue[1] * (budget_allocation.percent_allocation/100)
                            project_revenue.Q3 = revenue[2] * (budget_allocation.percent_allocation/100)
                            project_revenue.Q4 = revenue[3] * (budget_allocation.percent_allocation/100)
                            if project_revenue.Q1 > 0 or project_revenue.Q2 > 0 or project_revenue.Q3 > 0 or project_revenue.Q4 > 0:
                                self.project_revenues.append(project_revenue)
                  
            for project_revenue in self.project_revenues:
                self.revenue_closed[0] += project_revenue.Q1
                self.revenue_closed[1] += project_revenue.Q2
                self.revenue_closed[2] += project_revenue.Q3
                self.revenue_closed[3] += project_revenue.Q4
            
            self.revenue_closed[4] = self.revenue_closed[0] + self.revenue_closed[1] + self.revenue_closed[2] + self.revenue_closed[3]
            
            for ghost_project in self.user.account.ghost_projects:
                if ghost_project.is_active == True and (ghost_project.client is not None and ghost_project.client.is_active):
                    for budget_allocation in ghost_project.budget_allocations:
                        if budget_allocation.department_id == self.department.id:
                            revenue = quarterly_money(self.year,ghost_project.start_date,ghost_project.end_date,ghost_project.revenue_per_day,None,"ghost_revenue")
                            ghost_project_revenue = GhostProjectRevenue(ghost_project,self.year)
                            ghost_project_revenue.Q1 = revenue[0] * (budget_allocation.percent_allocation/100)
                            ghost_project_revenue.Q2 = revenue[1] * (budget_allocation.percent_allocation/100)
                            ghost_project_revenue.Q3 = revenue[2] * (budget_allocation.percent_allocation/100)
                            ghost_project_revenue.Q4 = revenue[3] * (budget_allocation.percent_allocation/100)
                            if ghost_project_revenue.Q1 > 0 or ghost_project_revenue.Q2 > 0 or ghost_project_revenue.Q3 > 0 or ghost_project_revenue.Q4 > 0:
                                self.ghost_project_revenues.append(ghost_project_revenue)
                elif ghost_project.is_active == True and (ghost_project.ghost_client is not None and ghost_project.ghost_client.is_active and ghost_project.ghost_client.is_tbg == False):
                    for budget_allocation in ghost_project.budget_allocations:
                        if budget_allocation.department_id == self.department.id:
                            revenue = quarterly_money(self.year,ghost_project.start_date,ghost_project.end_date,ghost_project.revenue_per_day,None,"ghost_revenue")
                            ghost_project_revenue = GhostProjectRevenue(ghost_project,self.year)
                            ghost_project_revenue.Q1 = revenue[0] * (budget_allocation.percent_allocation/100)
                            ghost_project_revenue.Q2 = revenue[1] * (budget_allocation.percent_allocation/100)
                            ghost_project_revenue.Q3 = revenue[2] * (budget_allocation.percent_allocation/100)
                            ghost_project_revenue.Q4 = revenue[3] * (budget_allocation.percent_allocation/100)
                            if ghost_project_revenue.Q1 > 0 or ghost_project_revenue.Q2 > 0 or ghost_project_revenue.Q3 > 0 or ghost_project_revenue.Q4 > 0:
                                self.ghost_project_revenues_from_ghost_clients.append(ghost_project_revenue)
                elif ghost_project.is_active == True and (ghost_project.ghost_client is not None and ghost_project.ghost_client.is_active and ghost_project.ghost_client.is_tbg == True):
                    for budget_allocation in ghost_project.budget_allocations:
                        if budget_allocation.department_id == self.department.id:
                            revenue = quarterly_money(self.year,ghost_project.start_date,ghost_project.end_date,ghost_project.revenue_per_day,None,"ghost_revenue")
                            ghost_project_revenue = GhostProjectRevenue(ghost_project,self.year)
                            ghost_project_revenue.Q1 = revenue[0] * (budget_allocation.percent_allocation/100)
                            ghost_project_revenue.Q2 = revenue[1] * (budget_allocation.percent_allocation/100)
                            ghost_project_revenue.Q3 = revenue[2] * (budget_allocation.percent_allocation/100)
                            ghost_project_revenue.Q4 = revenue[3] * (budget_allocation.percent_allocation/100)
                            if ghost_project_revenue.Q1 > 0 or ghost_project_revenue.Q2 > 0 or ghost_project_revenue.Q3 > 0 or ghost_project_revenue.Q4 > 0:
                                self.ghost_project_revenues_from_tbg.append(ghost_project_revenue)
                     
            for ghost_project_revenue in self.ghost_project_revenues:
                self.revenue_client_opportunities[0] += ghost_project_revenue.Q1
                self.revenue_client_opportunities[1] += ghost_project_revenue.Q2
                self.revenue_client_opportunities[2] += ghost_project_revenue.Q3
                self.revenue_client_opportunities[3] += ghost_project_revenue.Q4   
            
            for ghost_project_revenue in self.ghost_project_revenues_from_ghost_clients:
                self.revenue_prospects[0] += ghost_project_revenue.Q1
                self.revenue_prospects[1] += ghost_project_revenue.Q2
                self.revenue_prospects[2] += ghost_project_revenue.Q3
                self.revenue_prospects[3] += ghost_project_revenue.Q4

            for ghost_project_revenue in self.ghost_project_revenues_from_tbg:
                self.revenue_tbg[0] += ghost_project_revenue.Q1
                self.revenue_tbg[1] += ghost_project_revenue.Q2
                self.revenue_tbg[2] += ghost_project_revenue.Q3
                self.revenue_tbg[3] += ghost_project_revenue.Q4
                                
            self.revenue_client_opportunities[4] = self.revenue_client_opportunities[0] + self.revenue_client_opportunities[1] + self.revenue_client_opportunities[2] + self.revenue_client_opportunities[3]
            self.revenue_prospects[4] = self.revenue_prospects[0] + self.revenue_prospects[1] + self.revenue_prospects[2] + self.revenue_prospects[3]
            self.revenue_tbg[4] = self.revenue_tbg[0] + self.revenue_tbg[1] + self.revenue_tbg[2] + self.revenue_tbg[3]
            
            for x in range(0,5):
                self.revenue_total[x] = self.revenue_closed[x] + self.revenue_client_opportunities[x] + self.revenue_prospects[x] + self.revenue_tbg[x]
            
            for user in self.user.account.users:
                all_salary = quarterly_salary(self.year,user,user.start_date,datetime.datetime(int(self.year) + 1,1,1))
                if user.department_id == self.department.id:
                    total_salary_for_user = all_salary
                    expense_salary_non_billable_for_user = quarterly_salary(self.year,user,user.start_date,datetime.datetime(int(self.year) + 1,1,1),"non-billable")
                    full_billable_salary_for_user = quarterly_salary(self.year,user,user.start_date,datetime.datetime(int(self.year) + 1,1,1),"billable")
                
                    for x in range(0,4):
                        self.total_salary[x] += total_salary_for_user[x]
                        self.expense_salary_non_billable[x] += expense_salary_non_billable_for_user[x]
                        self.full_billable_salary[x] += full_billable_salary_for_user[x]
                
                for x in range(0,4):
                    self.all_salary[x] += all_salary[x]
                    
            for ghost_user in self.user.account.ghost_users:
                if ghost_user.department_id == self.department.id:
                    total_open_req = quarterly_money(self.year,ghost_user.start_date,datetime.datetime(int(self.year)+1,1,1),ghost_user.loaded_salary_per_day,None,"ghost_salary")    
                    expense_open_req_non_billable = quarterly_money(self.year,ghost_user.start_date,datetime.datetime(int(self.year)+1,1,1),ghost_user.loaded_non_billable_salary_per_day,None,"ghost_salary")
                    full_open_req_billable = quarterly_money(self.year,ghost_user.start_date,datetime.datetime(int(self.year)+1,1,1),ghost_user.loaded_billable_salary_per_day,None,"ghost_salary")
            
                    for x in range(0,4):
                        self.total_open_req[x] += total_open_req[x]
                        self.expense_open_req_non_billable[x] += expense_open_req_non_billable[x]
                        self.full_open_req_billable[x] += full_open_req_billable[x] 
       
            for x in range(0,4):
                self.total_salary[4] += self.total_salary[x]
                self.expense_salary_non_billable[4] += self.expense_salary_non_billable[x]
                self.full_billable_salary[4] += self.full_billable_salary[x]
                self.total_open_req[4] += self.total_open_req[x]
                self.expense_open_req_non_billable[4] += self.expense_open_req_non_billable[x]
                self.full_open_req_billable[4] += self.full_open_req_billable[x]
            
            for office in self.user.account.offices:
                q1_l_found = False
                q2_l_found = False
                q3_l_found = False
                q4_l_found = False
                q1_g_found = False
                q2_g_found = False
                q3_g_found = False
                q4_g_found = False
                
                for actual_expense in office.actual_expenses:
                    if actual_expense.quarter_end_date.year == self.year:
                        if actual_expense.quarter_end_date.month == 3:
                            if actual_expense.expense_local is not None:
                                q1_l_found = True
                                self.all_expense_sga[0] += actual_expense.expense_local * self.usd_to_local
                            if actual_expense_expense_global is not None:
                                q1_g_found = True
                                self.all_expense_salary_global[0] += actual_expense.expense_global * self.usd_to_local
                        elif actual_expense.quarter_end_date.month == 6:
                            if actual_expense.expense_local is not None:
                                q2_l_found = True
                                self.all_expense_sga[1] += actual_expense.expense_local * self.usd_to_local
                            if actual_expense_expense_global is not None:
                                q2_g_found = True
                                self.all_expense_salary_global[1] += actual_expense.expense_global * self.usd_to_local
                        elif actual_expense.quarter_end_date.month == 9:
                            if actual_expense.expense_local is not None:
                                q3_l_found = True
                                self.all_expense_sga[2] += actual_expense.expense_local * self.usd_to_local
                            if actual_expense_expense_global is not None:
                                q3_g_found = True
                                self.all_expense_salary_global[2] += actual_expense.expense_global * self.usd_to_local
                        elif actual_expense.quarter_end_date.month == 12:
                            if actual_expense.expense_local is not None:
                                q4_l_found = True
                                self.all_expense_sga[3] += actual_expense.expense_local * self.usd_to_local
                            if actual_expense_expense_global is not None:
                                q4_g_found = True
                                self.all_expense_salary_global[3] += actual_expense.expense_global * self.usd_to_local
                    
                if q1_l_found == False:
                    self.all_expense_sga[0] += (office.sga_expense * self.usd_to_local) / 4
                if q2_l_found == False:
                    self.all_expense_sga[1] += (office.sga_expense * self.usd_to_local) / 4
                if q3_l_found == False:
                    self.all_expense_sga[2] += (office.sga_expense * self.usd_to_local) / 4
                if q4_l_found == False:
                    self.all_expense_sga[3] += (office.sga_expense * self.usd_to_local) / 4
                if q1_g_found == False:
                    self.all_expense_salary_global[0] += (office.allocated_salary_expense * self.usd_to_local) / 4
                if q2_g_found == False:
                    self.all_expense_salary_global[1] += (office.allocated_salary_expense * self.usd_to_local) / 4
                if q3_g_found == False:
                    self.all_expense_salary_global[2] += (office.allocated_salary_expense * self.usd_to_local) / 4
                if q4_g_found == False:
                    self.all_expense_salary_global[3] += (office.allocated_salary_expense * self.usd_to_local) / 4
                
            self.all_expense_sga[4] = self.all_expense_sga[0] + self.all_expense_sga[1] + self.all_expense_sga[2] + self.all_expense_sga[3]
            self.all_expense_salary_global[4] = self.all_expense_salary_global[0] + self.all_expense_salary_global[1] + self.all_expense_salary_global[2] + self.all_expense_salary_global[3]
            
            if self.all_salary[4] > 0:
                percent_allocated_to_department = self.total_salary[4] / self.all_salary[4]
            else:
                percent_allocated_to_department = 0
                
            for x in range(0,5):
                self.expense_sga[x] += self.all_expense_sga[x] * percent_allocated_to_department
                self.expense_salary_global[x] += self.expense_salary_global[x] * percent_allocated_to_department
                         
            for x in range(0,5):
                self.expense_salary_bench[x] = self.full_billable_salary[x] - (self.expense_salary_billable[x] + self.expense_salary_prospects[x])
                # hack because of the qarterly money quirk
                if self.expense_salary_bench[x] < 0:
                    self.expense_salary_bench[x] = 0
                # end hack
                self.expense_open_req_bench[x] = self.full_open_req_billable[x] - (self.expense_open_req_billable[x] + self.expense_open_req_prospects[x])
        
                self.expense_total[x] = self.non_billable_expenses[x] + self.expense_salary_billable[x] + self.expense_salary_non_billable[x] + self.expense_salary_prospects[x] + self.expense_salary_bench[x]+self.expense_open_req_billable[x]+self.expense_open_req_non_billable[x]+self.expense_open_req_prospects[x]+self.expense_open_req_bench[x]+self.expense_freelance_billable[x]+self.expense_freelance_non_billable[x]
                self.revenue_total[x] = self.revenue_closed[x] + self.revenue_client_opportunities[x] + self.revenue_prospects[x] + self.revenue_tbg[x]
             
                self.profit[x] = self.revenue_total[x] - self.expense_total[x]
        
                if self.revenue_total[x] > 0 and self.profit[x] > 0: 
                    self.margin[x] = int((self.profit[x] / self.revenue_total[x]) * 100)
            
                else:
                    self.margin[x] = 0
        except:
            traceback.print_exc()
                
    def _likelihood(self):
        if self.revenue_prospects[4] == 0:
            return 0
        return int((self.revenue_prospects_weighted[4]/self.revenue_prospects[4])*100)
    
    likelihood = property(_likelihood)