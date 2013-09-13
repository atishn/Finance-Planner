from __future__ import division
import datetime
import traceback

from hr.utilities import quarterly_money,quarterly_salary
from hr.models.ClientFinancials import ClientFinancials
from hr.models.GhostClientFinancials import GhostClientFinancials


class OfficeFinancials(object):
    
    office = None
    
    year = 0
    user = None
    usd_to_local = 1
    
    client_financials = []
    prospect_financials = []
    tbg_financials = []
    
    expense_salary_billable = [0,0,0,0,0]
    expense_salary_non_billable = [0,0,0,0,0]
    expense_salary_bench = [0,0,0,0,0]
    expense_salary_prospects = [0,0,0,0,0]
    
    #really should not be used
    expense_salary_tbg = [0,0,0,0,0]
    
    expense_open_req_salary_billable = [0,0,0,0,0]
    expense_open_req_salary_non_billable = [0,0,0,0,0]
    expense_open_req_salary_bench = [0,0,0,0,0]
    expense_open_req_salary_prospects = [0,0,0,0,0]
    
    #really should not be used
    expense_open_req_salary_tbg = [0,0,0,0,0]
    
    expense_freelance_billable = [0,0,0,0,0]
    expense_freelance_billable_if_employee = [0,0,0,0,0]
    expense_freelance_non_billable = [0,0,0,0,0]
    expense_freelance_non_billable_if_employee = [0,0,0,0,0]
    
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
    
    #potential revenue and margin
    potential_revenue = [0,0,0,0,0]
    potential_profit = [0,0,0,0,0]
    potential_margin = [0,0,0,0,0]

    def __init__(self,office,year,user):
        self.office = office
        self.year = int(year)
        self.user = user

        if user.currency is not None:
            self.usd_to_local = user.currency.usd_to_currency
            
        self.calculateFinancials()
    
    def initializeVariables(self):
        self.client_financials = []
        self.prospect_financials = []
        self.tbg_financials = []
        
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
        self.expense_freelance_billable_if_employee = [0,0,0,0,0]
        self.expense_freelance_non_billable = [0,0,0,0,0]
        self.expense_freelance_non_billable_if_employee = [0,0,0,0,0]
        
        self.expense_salary_global = [0,0,0,0,0]
        self.expense_sga = [0,0,0,0,0]
        
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
        
        self.potential_revenue = [0,0,0,0,0]
        self.potential_profit = [0,0,0,0,0]
        self.potential_margin = [0,0,0,0,0]
        
    def calculateFinancials(self):
        self.initializeVariables()
        
        try:
            for client in self.office.clients:
                if client.is_active:
                    client_financials = ClientFinancials(client,self.year,self.user)
                    for x in range(0, 5):
                        self.expense_salary_billable[x] += client_financials.expense_salary[x]
                        self.expense_open_req_billable[x] += client_financials.expense_ghost[x]
                        self.expense_freelance_billable[x] += client_financials.expense_freelance[x]
                        self.expense_freelance_billable_if_employee[x] += client_financials.expense_freelance_if_employee[x]
                        self.revenue_closed[x] += client_financials.revenue_projects[x]
                        self.revenue_client_opportunities[x] += client_financials.revenue_client_opportunities[x]
                        self.non_billable_expenses[x] += client_financials.non_billable_expenses[x]
                    if client_financials.revenue_total[x] > 0:
                        self.client_financials.append(client_financials)
            
            for ghost_client in self.office.ghost_clients:
                if ghost_client.is_active:
                    tbg_financials = None
                    prospect_financials = None
            
                    if ghost_client.is_tbg:
                        tbg_financials = GhostClientFinancials(ghost_client,self.year,self.user)
                    else:
                        prospect_financials = GhostClientFinancials(ghost_client,self.year,self.user)
            
                    for x in range(0,5):
                        if prospect_financials is not None:
                            self.expense_salary_prospects[x] += prospect_financials.expense_salary[x]
                            self.expense_open_req_prospects[x] += prospect_financials.expense_ghost[x]
                            self.revenue_prospects[x] += prospect_financials.revenue[x]
                            self.revenue_prospects_weighted[x] += prospect_financials.weighted_revenue[x]
                        if tbg_financials is not None:
                            self.revenue_tbg[x] += tbg_financials.revenue[x]
            
                    if prospect_financials is not None and prospect_financials.revenue[x] > 0:
                        self.prospect_financials.append(prospect_financials)
                    if tbg_financials is not None and tbg_financials.revenue[x] > 0:
                        self.tbg_financials.append(tbg_financials)
          
            for user in self.office.users:
                total_salary_for_user = quarterly_salary(self.year,user,user.start_date,datetime.datetime(int(self.year) + 1,1,1))
                expense_salary_non_billable_for_user = quarterly_salary(self.year,user,user.start_date,datetime.datetime(int(self.year) + 1,1,1),"non-billable")
                full_billable_salary_for_user = quarterly_salary(self.year,user,user.start_date,datetime.datetime(int(self.year) + 1,1,1),"billable")
                
                for x in range(0,4):
                    self.total_salary[x] += total_salary_for_user[x]
                    self.expense_salary_non_billable[x] += expense_salary_non_billable_for_user[x]
                    self.full_billable_salary[x] += full_billable_salary_for_user[x]
            
            for freelancer in self.office.freelancers:
                comp_per_freelancer = quarterly_money(self.year,freelancer.start_date,freelancer.end_date,freelancer.rate_per_day)
                comp_per_freelancer_if_employee = quarterly_money(self.year,freelancer.start_date,freelancer.end_date,freelancer.rate_per_day_if_employee)

                for x in range(0,4):
                    self.expense_freelance_non_billable[x] += comp_per_freelancer[x]
                    self.expense_freelance_non_billable[4] += comp_per_freelancer[x]
                    self.expense_freelance_non_billable_if_employee[x] += comp_per_freelancer_if_employee[x]
                    self.expense_freelance_non_billable_if_employee[4] += comp_per_freelancer_if_employee[x]
            
            for ghost_user in self.office.ghost_users:
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
            
            for actual_expense in self.office.actual_expenses:
                if actual_expense.quarter_end_date.year == self.year:
                    if actual_expense.quarter_end_date.month == 3:
                        if actual_expense.expense_local is not None:
                            self.expense_sga[0] = actual_expense.expense_local * self.usd_to_local
                        if actual_expense.expense_global is not None:
                            self.expense_salary_global[0] = actual_expense.expense_global * self.usd_to_local
                    elif actual_expense.quarter_end_date.month == 6:
                        if actual_expense.expense_local is not None:
                            self.expense_sga[1] = actual_expense.expense_local * self.usd_to_local
                        if actual_expense.expense_global is not None:
                            self.expense_salary_global[1] = actual_expense.expense_global * self.usd_to_local
                    elif actual_expense.quarter_end_date.month == 9:
                        if actual_expense.expense_local is not None:
                            self.expense_sga[2] = actual_expense.expense_local * self.usd_to_local
                        if actual_expense.expense_global is not None:
                            self.expense_salary_global[2] = actual_expense.expense_global * self.usd_to_local
                    elif actual_expense.quarter_end_date.month == 12:
                        if actual_expense.expense_local is not None:
                            self.expense_sga[3] = actual_expense.expense_local * self.usd_to_local
                        if actual_expense.expense_global is not None:
                            self.expense_salary_global[3] = actual_expense.expense_global * self.usd_to_local
                         
            for x in range(0,5):
                # not totally accurate; does not account for people billed out to clients in other offices - fix
                self.expense_salary_bench[x] = self.full_billable_salary[x] - (self.expense_salary_billable[x] + self.expense_salary_prospects[x])
                # hack because of the qarterly money quirk
                if self.expense_salary_bench[x] < 0:
                    self.expense_salary_bench[x] = 0
                    # end hack
                self.expense_open_req_bench[x] = self.full_open_req_billable[x] - (self.expense_open_req_billable[x] + self.expense_open_req_prospects[x])
        
                if self.expense_sga[x] == 0:
                    if x == 4:
                        self.expense_sga[x] = self.office.sga_expense * self.usd_to_local
                    elif self.office.allocated_salary_expense is not None:
                        self.expense_sga[x] = (self.office.sga_expense * self.usd_to_local) / 4
                
                if self.expense_salary_global[x] == 0:
                    if x == 4:
                        self.expense_salary_global[x] = self.office.allocated_salary_expense * self.usd_to_local
                    elif self.office.allocated_salary_expense is not None:
                        self.expense_salary_global[x] = (self.office.allocated_salary_expense * self.usd_to_local) / 4
            
                self.expense_total[x] = self.non_billable_expenses[x] + self.expense_salary_billable[x] + self.expense_salary_non_billable[x] + self.expense_salary_prospects[x] + self.expense_salary_bench[x]+self.expense_open_req_billable[x]+self.expense_open_req_non_billable[x]+self.expense_open_req_prospects[x]+self.expense_open_req_bench[x]+self.expense_freelance_billable[x]+self.expense_freelance_non_billable[x]
                self.revenue_total[x] = self.revenue_closed[x] + self.revenue_client_opportunities[x] + self.revenue_prospects[x] + self.revenue_tbg[x]
             
                self.profit[x] = self.revenue_total[x] - self.expense_total[x]
            
                if self.revenue_total[x] > 0: 
                    self.margin[x] = int((self.profit[x] / self.revenue_total[x]) * 100)
                else:
                    self.margin[x] = 0
            
            # calculate potential revenue and margin, which is based on ratios from last full quarter applied moving forward
            
            if datetime.datetime.now().year > self.year:
                for x in range(0,4):
                    if (self.expense_salary_billable[x] + self.expense_freelance_billable_if_employee[x]) > 0:
                        revenue_per_dollar_salary_freelance = self.revenue_total[x] / (self.expense_salary_billable[x] + self.expense_freelance_billable_if_employee[x])
                    else:
                        revenue_per_dollar_salary_freelance = 0
                    self.potential_revenue[x] = self.revenue_total[x] + ((self.expense_salary_bench[x] + self.expense_salary_prospects[x] + self.expense_salary_tbg[x]) * revenue_per_dollar_salary_freelance)
            elif datetime.datetime.now().month < 4:
                old_office_financials = OfficeFinancials(self.office,self.year-1,self.user)
                if (old_office_financials.expense_salary_billable[4] + old_office_financials.expense_freelance_billable_if_employee[4]) > 0:
                    revenue_per_dollar_salary_freelance = old_office_financials.revenue_total[4] / (old_office_financials.expense_salary_billable[4] + old_office_financials.expense_freelance_billable_if_employee[4])
                else:
                    revenue_per_dollar_salary_freelance = 0
                for x in range(0,4):
                    self.potential_revenue[x] = self.revenue_total[x] + ((self.expense_salary_bench[x] + self.expense_salary_prospects[x] + self.expense_salary_tbg[x]) * revenue_per_dollar_salary_freelance)
            elif datetime.datetime.now().month < 7:
                revenue_per_dollar_salary_freelance = self.revenue_total[0] / (self.expense_salary_billable[0] + self.expense_freelance_billable_if_employee[0])
                for x in range(0,4):
                    self.potential_revenue[x] = self.revenue_total[x] + ((self.expense_salary_bench[x] + self.expense_salary_prospects[x] + self.expense_salary_tbg[x]) * revenue_per_dollar_salary_freelance)
            elif datetime.datetime.now().month < 10:
                if (self.expense_salary_billable[0] + self.expense_freelance_billable_if_employee[0]) > 0:
                    revenue_per_dollar_salary_freelance = self.revenue_total[0] / (self.expense_salary_billable[0] + self.expense_freelance_billable_if_employee[0])
                else:
                    revenue_per_dollar_salary_freelance = 0
                self.potential_revenue[0] = self.revenue_total[0] + ((self.expense_salary_bench[0] + self.expense_salary_prospects[0] + self.expense_salary_tbg[0]) * revenue_per_dollar_salary_freelance)
                if (self.expense_salary_billable[1] + self.expense_freelance_billable_if_employee[1]) > 0:
                    revenue_per_dollar_salary_freelance = self.revenue_total[1] / (self.expense_salary_billable[1] + self.expense_freelance_billable_if_employee[1])
                else:
                    revenue_per_dollar_salary_freelance = 0
                self.potential_revenue[1] = self.revenue_total[1] + ((self.expense_salary_bench[1] + self.expense_salary_prospects[1] + self.expense_salary_tbg[1]) * revenue_per_dollar_salary_freelance)
                self.potential_revenue[2] = self.revenue_total[2] + ((self.expense_salary_bench[2] + self.expense_salary_prospects[2] + self.expense_salary_tbg[2]) * revenue_per_dollar_salary_freelance)
                self.potential_revenue[3] = self.revenue_total[3] + ((self.expense_salary_bench[3] + self.expense_salary_prospects[3] + self.expense_salary_tbg[3]) * revenue_per_dollar_salary_freelance)
            else:
                if (self.expense_salary_billable[0] + self.expense_freelance_billable_if_employee[0]) > 0:
                    revenue_per_dollar_salary_freelance = self.revenue_total[0] / (self.expense_salary_billable[0] + self.expense_freelance_billable_if_employee[0])
                else:
                    revenue_per_dollar_salary_freelance = 0
                self.potential_revenue[0] = self.revenue_total[0] + ((self.expense_salary_bench[0] + self.expense_salary_prospects[0] + self.expense_salary_tbg[0]) * revenue_per_dollar_salary_freelance)
                if (self.expense_salary_billable[1] + self.expense_freelance_billable_if_employee[1]) > 0:
                    revenue_per_dollar_salary_freelance = self.revenue_total[1] / (self.expense_salary_billable[1] + self.expense_freelance_billable_if_employee[1])
                else:
                    revenue_per_dollar_salary_freelance = 0
                self.potential_revenue[1] = self.revenue_total[1] + ((self.expense_salary_bench[1] + self.expense_salary_prospects[1] + self.expense_salary_tbg[1]) * revenue_per_dollar_salary_freelance)
                if (self.expense_salary_billable[2] + self.expense_freelance_billable_if_employee[2]) > 0:
                    revenue_per_dollar_salary_freelance = self.revenue_total[2] / (self.expense_salary_billable[2] + self.expense_freelance_billable_if_employee[2])
                else:
                    revenue_per_dollar_salary_freelance = 0
                self.potential_revenue[2] = self.revenue_total[2] + ((self.expense_salary_bench[2] + self.expense_salary_prospects[2] + self.expense_salary_tbg[2]) * revenue_per_dollar_salary_freelance)
                self.potential_revenue[3] = self.revenue_total[3] + ((self.expense_salary_bench[3] + self.expense_salary_prospects[3] + self.expense_salary_tbg[3]) * revenue_per_dollar_salary_freelance)   
            self.potential_revenue[4] = self.potential_revenue[0] + self.potential_revenue[1] + self.potential_revenue[2] + self.potential_revenue[3]
            
            for x in range(0,5):
                self.potential_profit[x] = self.potential_revenue[x] - (self.expense_total[x] - (self.expense_freelance_billable[x] + self.expense_freelance_non_billable[x] - (self.expense_freelance_billable_if_employee[x] + self.expense_freelance_non_billable_if_employee[x])))
                
                if self.potential_revenue[x] > 0: 
                    self.potential_margin[x] = int((self.potential_profit[x] / self.potential_revenue[x]) * 100)
                else:
                    self.potential_margin[x] = 0
        except:
            traceback.print_exc()
                
    def _likelihood(self):
        if self.revenue_prospects[4] == 0:
            return 0
        return int((self.revenue_prospects_weighted[4]/self.revenue_prospects[4])*100)
    
    likelihood = property(_likelihood)