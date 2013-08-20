from __future__ import division
from hr.models.OfficeFinancials import OfficeFinancials

class GlobalFinancials(object):
    
    account = None
    year = 0
    user = None
    
    office_financials = []
    
    expense_salary_billable = [0,0,0,0,0]
    expense_salary_non_billable = [0,0,0,0,0]
    expense_salary_bench = [0,0,0,0,0]
    expense_open_req_billable = [0,0,0,0,0]
    expense_open_req_non_billable = [0,0,0,0,0]
    expense_open_req_bench = [0,0,0,0,0]
    expense_salary_prospects = [0,0,0,0,0]
    expense_open_req_prospects = [0,0,0,0,0]
    expense_freelance_billable = [0,0,0,0,0]
    expense_freelance_non_billable = [0,0,0,0,0]
    
    non_billable_expenses = [0,0,0,0,0]
    
    expense_salary_global = [0,0,0,0,0]
    expense_sga = [0,0,0,0,0]
    expense_total = [0,0,0,0,0]
    
    revenue_closed = [0,0,0,0,0]
    revenue_client_opportunities = [0,0,0,0,0]
    revenue_prospects = [0,0,0,0,0]
    revenue_tbg = [0,0,0,0,0]
    revenue_total = [0,0,0,0,0]
    
    profit = [0,0,0,0,0]
    margin = [0,0,0,0,0]
    
    potential_revenue = [0,0,0,0,0]
    potential_profit = [0,0,0,0,0]
    potential_margin = [0,0,0,0,0]

    #TODO: ADD DISCRETIONARY PER OFFICE AMOUNT THAT PEOPLE CAN ADD IN
    def __init__(self,account,year,user):
        self.year = year
        self.account = account
        self.user = user

        self.calculateFinancials()
    
    def initializeVariables(self):
        self.office_financials = []
        self.expense_salary_billable = [0,0,0,0,0]
        self.expense_salary_non_billable = [0,0,0,0,0]
        self.expense_salary_bench = [0,0,0,0,0]
        self.expense_open_req_billable = [0,0,0,0,0]
        self.expense_open_req_non_billable = [0,0,0,0,0]
        self.expense_open_req_bench = [0,0,0,0,0]
        self.expense_salary_prospects = [0,0,0,0,0]
        self.expense_open_req_prospects = [0,0,0,0,0]
        self.expense_freelance_billable = [0,0,0,0,0]
        self.expense_freelance_non_billable = [0,0,0,0,0]

        self.non_billable_expenses = [0,0,0,0,0]
        
        self.expense_salary_global = [0,0,0,0,0]
        self.expense_sga = [0,0,0,0,0]
        self.expense_total = [0,0,0,0,0]

        self.revenue_closed = [0,0,0,0,0]
        self.revenue_client_opportunities = [0,0,0,0,0]
        self.revenue_prospects = [0,0,0,0,0]
        self.revenue_tbg = [0,0,0,0,0]
        self.revenue_total = [0,0,0,0,0]

        self.profit = [0,0,0,0,0]
        self.margin = [0,0,0,0,0]
        
        self.potential_revenue = [0,0,0,0,0]
        self.potential_profit = [0,0,0,0,0]
        self.potential_margin = [0,0,0,0,0]
        
    def calculateFinancials(self):
        self.initializeVariables()
        
        for office in self.account.offices:
            if office.is_active:
                office_finances = OfficeFinancials(office,self.year,self.user)
                self.office_financials.append(office_finances)
            
                for x in range(0, 5):
                    self.expense_salary_billable[x] += office_finances.expense_salary_billable[x]
                    self.expense_salary_non_billable[x] += office_finances.expense_salary_non_billable[x]
                    self.expense_salary_bench[x] += office_finances.expense_salary_bench[x]
                    self.expense_open_req_billable[x] += office_finances.expense_open_req_billable[x]
                    self.expense_open_req_non_billable[x] += office_finances.expense_open_req_non_billable[x]
                    self.expense_open_req_bench[x] += office_finances.expense_open_req_bench[x]
                    self.expense_salary_prospects[x] += office_finances.expense_salary_prospects[x]
                    self.expense_open_req_prospects[x] += office_finances.expense_open_req_prospects[x]
                    self.expense_freelance_billable[x] += office_finances.expense_freelance_billable[x]
                    self.expense_freelance_non_billable[x] += office_finances.expense_freelance_non_billable[x]

                    self.non_billable_expenses[x] += office_finances.non_billable_expenses[x]
                    self.expense_salary_global[x] += office_finances.expense_salary_global[x]
                    self.expense_sga[x] += office_finances.expense_sga[x]
                    self.expense_total[x] += office_finances.expense_total[x]

                    self.revenue_closed[x] += office_finances.revenue_closed[x]
                    self.revenue_client_opportunities[x] += office_finances.revenue_client_opportunities[x]
                    self.revenue_prospects[x] += office_finances.revenue_prospects[x]
                    self.revenue_tbg[x] += office_finances.revenue_tbg[x]
                    self.revenue_total[x] += office_finances.revenue_total[x]
                
                    self.profit[x] = self.revenue_total[x] - self.expense_total[x]
                
                    if self.revenue_total[x] > 0: 
                        self.margin[x] = int((self.profit[x] / self.revenue_total[x]) * 100)
                    else:
                        self.margin[x] = 0
                        
                    self.potential_revenue[x] += office_finances.potential_revenue[x]
                    self.potential_profit[x] += office_finances.potential_revenue[x]
                    
                    if self.potential_profit[x] > 0: 
                        self.potential_margin[x] = int((self.potential_profit[x] / self.potential_revenue[x]) * 100)
                    else:
                        self.potential_margin[x] = 0