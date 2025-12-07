# Copyright (c) 2023, Karama kcsc and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe, datetime
from frappe import _, scrub, ValidationError
from frappe.utils import flt, comma_or, nowdate, getdate
from erpnext.setup.utils import get_exchange_rate
from erpnext.controllers.accounts_controller import AccountsController
from frappe.model.document import Document
from erpnext.accounts.general_ledger import make_gl_entries, process_gl_map, make_reverse_gl_entries
from masar_savingfund.custom.employee.employee import get_employee_savefund_balance

class InvalidEmployeeResignation(ValidationError):
    pass

class EmployeeResignation(AccountsController):
    def __init__(self, *args, **kwargs):
         super(EmployeeResignation, self).__init__(*args, **kwargs)
    
    def validate(self):
        self.set_default_accounts()
        self.fetch_employee_balances()
        self.calculate_equity_and_income()
    
    def on_cancel(self):
        self.delete_linked_gl_entries()
        employee = frappe.get_doc("Employee", self.employee)
        employee.relieving_date = None
        employee.status = "Active"
        employee.save()
      
    def on_submit(self):
        employee = frappe.get_doc("Employee", self.employee)
        employee.relieving_date = self.resignation_date
        employee.status = "Left"
        employee.save()
        self.make_gl()

    def before_submit(self):
        exists = frappe.db.exists(
            'Employee Resignation',
            {
                'employee': self.employee,
                'docstatus': 1,
                'status': ('=', self.status),
            },
        )
        if exists:
            frappe.throw('This Employee Has Resigned')
    
    def set_default_accounts(self):
        if not self.liability_account:
            self.liability_account = get_liability_account()
        if not self.employee_equity:
            self.employee_equity = get_employee_equity_account()
        if not self.bank_equity:
            self.bank_equity = get_bank_equity_account()
        if not self.income_account:
            self.income_account = get_income_account()
        if not self.staff_withdrawal_account:
            self.staff_withdrawal_account = get_staff_withdraw_account()
        if not self.retained_earning:
            self.retained_earning = get_retained_earning()
    
    def fetch_employee_balances(self):
        if not self.employee or not self.posting_date:
            return
        
        balances = get_employee_savefund_balance(
            selected_employees=json.dumps([self.employee]),
            date_to=self.posting_date
        )
        
        if balances and len(balances) > 0:
            balance = balances[0]
            self.employee_contr = flt(balance.get('total_employee_contr', 0))
            self.bank_contr = flt(balance.get('total_bank_contr', 0))
            self.pl_employee_contr = flt(balance.get('total_employee_pl', 0))
            self.pl_bank_contr = flt(balance.get('total_bank_pl', 0))
            self.total_right = flt(balance.get('total_right', 0))
            self.deserved_amount = flt(balance.get('deserved_amount', 0))
            self.withdraw_amount = flt(balance.get('total_paid_amount', 0))
    
    def calculate_equity_and_income(self):
        if not self.resignation_date or not self.date_of_joining:
            return
        
        res_date = getdate(self.resignation_date)
        join_date = getdate(self.date_of_joining)
        delta = res_date - join_date
        number_of_years = delta.days / 365.25
        self.number_of_years = number_of_years
        
        emp_contr_perc = flt(frappe.db.get_single_value('Saving Fund Settings', 'employee_contr_per')) / 100
        bank_contr_perc = flt(frappe.db.get_single_value('Saving Fund Settings', 'bank_contr_per')) / 100
        
        employee_equity = flt(self.employee_contr)
        bank_equity = flt(self.bank_contr)
        emp_income = flt(self.pl_employee_contr)
        bank_income = flt(self.pl_bank_contr)
        withdraw_amount = flt(self.withdraw_amount)
        
        if number_of_years < 1:
            self.employee_equity_amount = employee_equity
            self.bank_equity_amount = 0
            self.emp_income_amount = 0
            self.bank_income_amount = 0
        elif number_of_years >= 1 and number_of_years < 3:
            self.employee_equity_amount = employee_equity
            self.bank_equity_amount = 0
            self.emp_income_amount = emp_income
            self.bank_income_amount = 0
        else:
            self.employee_equity_amount = employee_equity
            self.bank_equity_amount = bank_equity
            self.emp_income_amount = emp_income
            self.bank_income_amount = bank_income
        
        if withdraw_amount > 0:
            total_before_withdrawal = (
                flt(self.employee_contr) + 
                flt(self.bank_contr) + 
                flt(self.pl_employee_contr) + 
                flt(self.pl_bank_contr)
            )
            
            if total_before_withdrawal > 0:
                emp_equity_ratio = flt(self.employee_contr) / total_before_withdrawal
                bank_equity_ratio = flt(self.bank_contr) / total_before_withdrawal
                emp_income_ratio = flt(self.pl_employee_contr) / total_before_withdrawal
                bank_income_ratio = flt(self.pl_bank_contr) / total_before_withdrawal
                
                self.employee_equity_amount = max(0, flt(self.employee_contr) - (withdraw_amount * emp_equity_ratio))
                self.bank_equity_amount = max(0, flt(self.bank_contr) - (withdraw_amount * bank_equity_ratio))
                self.emp_income_amount = max(0, flt(self.pl_employee_contr) - (withdraw_amount * emp_income_ratio))
                self.bank_income_amount = max(0, flt(self.pl_bank_contr) - (withdraw_amount * bank_income_ratio))
        
        income_emp = flt(self.employee_equity_amount) - flt(self.employee_contr)
        income_emp_pl = flt(self.emp_income_amount) - flt(self.pl_employee_contr)
        income_bank = flt(self.bank_equity_amount) - flt(self.bank_contr)
        income_bank_pl = flt(self.bank_income_amount) - flt(self.pl_bank_contr)
        
        self.income_emp_amount = abs(income_emp)
        self.income_emp_amount_pl = abs(income_emp_pl)
        self.income_bank_amount = abs(income_bank)
        self.income_bank_amount_pl = abs(income_bank_pl)
        
        total_income = income_emp + income_bank + income_emp_pl + income_bank_pl
        self.income_amount = abs(total_income)
        
    def make_gl(self):
        if self.resignation_date and self.date_of_joining:
            gl_entries = []
            if self.deserved_amount:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.liability_account,
                        "against": self.employee_equity,
                        "credit_in_account_currency": self.deserved_amount,
                        "credit": self.deserved_amount,
                        "employee": self.employee,
                        "cost_center": cost_center(self.company),
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
            if self.employee_equity_amount:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.employee_equity,
                        "against": self.liability_account,
                        "debit_in_account_currency": self.employee_equity_amount,
                        "debit": self.employee_equity_amount,
                        "employee": self.employee,
                        "cost_center": cost_center(self.company),
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
            if self.bank_equity_amount:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.bank_equity,
                        "against": self.liability_account,
                        "debit_in_account_currency": self.bank_equity_amount,
                        "debit": self.bank_equity_amount,
                        "employee": self.employee,
                        "cost_center": cost_center(self.company),
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
            if self.bank_income_amount:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.retained_earning,
                        "against": self.liability_account,
                        "debit_in_account_currency": self.bank_income_amount,
                        "debit": self.bank_income_amount,
                        "employee": self.employee,
                        "cost_center": cost_center(self.company),
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
            if self.emp_income_amount:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.retained_earning,
                        "against": self.liability_account,
                        "debit_in_account_currency": self.emp_income_amount,
                        "debit": self.emp_income_amount,
                        "employee": self.employee,
                        "cost_center": cost_center(self.company),
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
            if self.income_emp_amount:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.employee_equity,
                        "against": self.liability_account,
                        "debit_in_account_currency": self.income_emp_amount,
                        "debit": self.income_emp_amount,
                        "employee": self.employee,
                        "cost_center": cost_center(self.company),
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
            if self.income_emp_amount_pl:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.retained_earning,
                        "against": self.liability_account,
                        "debit_in_account_currency": self.income_emp_amount_pl,
                        "debit": self.income_emp_amount_pl,
                        "employee": self.employee,
                        "cost_center": cost_center(self.company),
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
            if self.income_bank_amount:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.bank_equity,
                        "against": self.liability_account,
                        "debit_in_account_currency": self.income_bank_amount,
                        "debit": self.income_bank_amount,
                        "employee": self.employee,
                        "cost_center": cost_center(self.company),
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
            if self.income_bank_amount_pl:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.retained_earning,
                        "against": self.liability_account,
                        "debit_in_account_currency": self.income_bank_amount_pl,
                        "debit": self.income_bank_amount_pl,
                        "employee": self.employee,
                        "cost_center": cost_center(self.company),
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
            if self.income_amount:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.staff_withdrawal_account if flt(self.number_of_years) > 3 else self.income_account,
                        "against": self.liability_account,
                        "credit_in_account_currency": self.income_amount,
                        "credit": self.income_amount,
                        "employee": self.employee,
                        "cost_center": cost_center(self.company),
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))

            if gl_entries:
                make_gl_entries(gl_entries, cancel=0, adv_adj=0)

    def delete_linked_gl_entries(self):
        cancelled_doc = frappe.db.sql_list("""select name from `tabEmployee Resignation` 
        where docstatus = 2 """)
        if cancelled_doc:
            frappe.db.sql("""delete from `tabGL Entry` 
                        where voucher_type = 'Employee Resignation' and voucher_no in (%s)""" 
                        % (', '.join(['%s']*len(cancelled_doc))), tuple(cancelled_doc))


### Default Accounts and Cost Center ###
@frappe.whitelist()
def get_employee_equity_account():
    return frappe.db.get_single_value('Saving Fund Settings', 'employee_equity')

@frappe.whitelist()
def get_bank_equity_account():
    return frappe.db.get_single_value('Saving Fund Settings', 'bank_equity')

@frappe.whitelist()
def get_liability_account():
    return frappe.db.get_single_value('Saving Fund Settings', 'liability_account')

@frappe.whitelist()
def get_income_account():
    return frappe.db.get_single_value('Saving Fund Settings', 'income_account')

@frappe.whitelist()
def get_retained_earning():
    return frappe.db.get_single_value('Saving Fund Settings', 'retained_earning')

@frappe.whitelist()
def get_staff_withdraw_account():
    return frappe.db.get_single_value('Saving Fund Settings', 'withdrawal')

@frappe.whitelist()
def cost_center(company):
    doc = frappe.get_doc('Company', company)
    return doc.cost_center