# Copyright (c) 2023, Karama kcsc and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext, json,datetime
from frappe import _, scrub, ValidationError
from frappe.utils import flt, comma_or, nowdate, getdate
from erpnext.setup.utils import get_exchange_rate
from erpnext.controllers.accounts_controller import AccountsController
from frappe.model.document import Document
from erpnext.accounts.general_ledger import make_gl_entries, process_gl_map, make_reverse_gl_entries

class InvalidEmployeeResignation(ValidationError):
	pass

class EmployeeResignation(AccountsController):
    def __init__(self, *args, **kwargs):
         super(EmployeeResignation, self).__init__(*args, **kwargs)
    
    def validate(self):
          pass
    
    def on_cancel(self):
          pass
       
    def on_submit(self):
        employee = frappe.get_doc("Employee", self.employee)
        employee.relieving_date = self.resignation_date
        employee.status = "Left"
        employee.save()
        self.make_gl()
        
        
    def make_gl(self):
        if self.resignation_date and self.date_of_joining:
            res_date = datetime.datetime.strptime(self.resignation_date, '%Y-%m-%d')
            join_date = datetime.datetime.strptime(self.date_of_joining, '%Y-%m-%d')
            delta = res_date - join_date
            number_year = delta.days / 365.0
            gl_entries = []
            
            if number_year < 1:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.liability_account,
                        # "account_currency": d.paid_from_account_currency,
                        "against": self.employee_equity,
                        "credit_in_account_currency": self.employee_contr,
                        "credit": self.employee_contr,
                        "employee": self.employee,
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.employee_equity,
                        # "account_currency": d.paid_to_account_currency,
                        "against": self.liability_account,
                        "debit_in_account_currency": self.employee_contr,
                        "debit": self.employee_contr,
                        "employee": self.employee,
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
                
            if number_year >= 1 and number_year < 3:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.liability_account,
                        # "account_currency": d.paid_from_account_currency,
                        "against": self.employee_equity,
                        "credit_in_account_currency": self.employee_contr + self.pl_employee_contr,
                        "credit": self.employee_contr + self.pl_employee_contr,
                        "employee": self.employee,
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.employee_equity,
                        # "account_currency": d.paid_to_account_currency,
                        "against": self.liability_account,
                        "debit_in_account_currency": self.employee_contr + self.pl_employee_contr,
                        "debit": self.employee_contr + self.pl_employee_contr,
                        "employee": self.employee,
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
                
            if number_year >= 3:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.liability_account,
                        # "account_currency": d.paid_from_account_currency,
                        "against": self.employee_equity,
                        "credit_in_account_currency": self.employee_contr + self.pl_employee_contr,
                        "credit": self.employee_contr + self.pl_employee_contr,
                        "employee": self.employee,
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.employee_equity,
                        # "account_currency": d.paid_to_account_currency,
                        "against": self.liability_account,
                        "debit_in_account_currency": self.employee_contr + self.pl_employee_contr,
                        "debit": self.employee_contr + self.pl_employee_contr,
                        "employee": self.employee,
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
                
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.liability_account,
                        # "account_currency": d.paid_from_account_currency,
                        "against": self.bank_equity,
                        "credit_in_account_currency": self.bank_contr + self.pl_bank_contr,
                        "credit": self.bank_contr + self.pl_bank_contr,
                        "employee": self.employee,
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.bank_equity,
                        # "account_currency": d.paid_to_account_currency,
                        "against": self.liability_account,
                        "debit_in_account_currency": self.bank_contr + self.pl_bank_contr,
                        "debit": self.bank_contr + self.pl_bank_contr,
                        "employee": self.employee,
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))                
            if gl_entries:
                make_gl_entries(gl_entries, cancel=0, adv_adj=0)
   
@frappe.whitelist()
def get_employee_equity_account():
	return frappe.db.get_single_value('Saving Fund Settings', 'employee_equity')

@frappe.whitelist()
def get_bank_equity_account():
	return frappe.db.get_single_value('Saving Fund Settings', 'bank_equity')

@frappe.whitelist()
def get_liability_account():
	return frappe.db.get_single_value('Saving Fund Settings', 'liability_account')