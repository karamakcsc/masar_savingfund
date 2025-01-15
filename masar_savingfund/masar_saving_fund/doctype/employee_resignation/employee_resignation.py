# Copyright (c) 2023, Karama kcsc and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
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
                # check for submitted documents
                'docstatus': 1,
                # check if the membership's end date is later than this membership's start date
                'status': ('=', self.status),
            },
        )
        if exists:
            frappe.throw('This Employee Has Resigned')      
        
    def make_gl(self):
        if self.resignation_date and self.date_of_joining:
            diff_balance = self.total_right - self.cont_up_to_date
            gl_entries = []
            
            if self.employee_equity_amount > 0:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.liability_account,
                        # "account_currency": d.paid_from_account_currency,
                        "against": self.employee_equity,
                        "credit_in_account_currency": self.employee_equity_amount,
                        "credit": self.employee_equity_amount,
                        "employee": self.employee,
                        "cost_center":cost_center(self.company),
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.employee_equity,
                        # "account_currency": d.paid_to_account_currency,
                        "against": self.liability_account,
                        "debit_in_account_currency": self.employee_equity_amount,
                        "debit": self.employee_equity_amount,
                        "employee": self.employee,
                        "cost_center":cost_center(self.company),
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
                ############################

                # gl_entries.append(
                #     self.get_gl_dict({
                #         "account": self.income_account,
                #         # "account_currency": d.paid_from_account_currency,
                #         "against": self.bank_equity,
                #         "credit_in_account_currency": float(diff_balance),
                #         "credit": float(diff_balance),
                #         "employee": self.employee,
                #         "cost_center":cost_center(self.company),
                #         "remarks": self.employee + ' : ' + self.employee_name
                #     }))
                # gl_entries.append(
                #     self.get_gl_dict({
                #         "account": self.bank_equity,
                #         # "account_currency": d.paid_to_account_currency,
                #         "against": self.income_account,
                #         "debit_in_account_currency": float(diff_balance),
                #         "debit": float(diff_balance),
                #         "employee": self.employee,
                #         "cost_center":cost_center(self.company),
                #         "remarks": self.employee + ' : ' + self.employee_name
                #     }))

                ############################

            if self.income_emp_amount > 0:                
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.income_account,
                        # "account_currency": d.paid_from_account_currency,
                        "against": self.employee_equity,
                        "credit_in_account_currency": self.income_emp_amount,
                        "credit": self.income_emp_amount,
                        "cost_center":cost_center(self.company),
                        "employee": self.employee,
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.employee_equity,
                        # "account_currency": d.paid_to_account_currency,
                        "against": self.income_account,
                        "debit_in_account_currency": self.income_emp_amount,
                        "debit": self.income_emp_amount,
                        "cost_center":cost_center(self.company),
                        "employee": self.employee,
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
                               ############################

                # gl_entries.append(
                #     self.get_gl_dict({
                #         "account": self.income_account,
                #         # "account_currency": d.paid_from_account_currency,
                #         "against": self.bank_equity,
                #         "credit_in_account_currency": float(diff_balance),
                #         "credit": float(diff_balance),
                #         "employee": self.employee,
                #         "cost_center":cost_center(self.company),
                #         "remarks": self.employee + ' : ' + self.employee_name
                #     }))
                # gl_entries.append(
                #     self.get_gl_dict({
                #         "account": self.bank_equity,
                #         # "account_currency": d.paid_to_account_currency,
                #         "against": self.income_account,
                #         "debit_in_account_currency": float(diff_balance),
                #         "debit": float(diff_balance),
                #         "employee": self.employee,
                #         "cost_center":cost_center(self.company),
                #         "remarks": self.employee + ' : ' + self.employee_name
                #     }))

                ############################

            if self.bank_equity_amount > 0:            
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.liability_account,
                        # "account_currency": d.paid_from_account_currency,
                        "against": self.bank_equity,
                        "credit_in_account_currency":self.bank_equity_amount,
                        "credit": self.bank_equity_amount,
                        "employee": self.employee,
                        "cost_center":cost_center(self.company),
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.bank_equity,
                        # "account_currency": d.paid_to_account_currency,
                        "against": self.liability_account,
                        "debit_in_account_currency": self.bank_equity_amount,
                        "debit": self.bank_equity_amount,
                        "employee": self.employee,
                        "cost_center":cost_center(self.company),
                        "remarks": self.employee + ' : ' + self.employee_name
                    })) 
            if self.income_bank_amount > 0:                            
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.income_account,
                        # "account_currency": d.paid_from_account_currency,
                        "against": self.bank_equity,
                        "credit_in_account_currency":self.income_bank_amount # + float(diff_balance),
                        "credit": self.income_bank_amount # + float(diff_balance),
                        "cost_center":cost_center(self.company),
                        "employee": self.employee,
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.bank_equity,
                        # "account_currency": d.paid_to_account_currency,
                        "against": self.income_account,
                        "debit_in_account_currency": self.income_bank_amount # + float(diff_balance),
                        "debit": self.income_bank_amount # + float(diff_balance),
                        "cost_center":cost_center(self.company),
                        "employee": self.employee,
                        "remarks": self.employee + ' : ' + self.employee_name
                    }))                    
            if gl_entries:
                make_gl_entries(gl_entries, cancel=0, adv_adj=0)

    def cancel_linked_gl_entries(self):
        gl_entries = frappe.get_all("GL Entry",filters={"voucher_type": self.doctype, "voucher_no": self.name, "docstatus": 1},pluck="parent",distinct=True,)
        for gl_entry in gl_entries:
            gl_entry_doc = frappe.get_doc("GL Entry", gl_entry.name)
            gl_entry_doc.docstatus = 2
            gl_entry_doc.save()
            self.db_set("gl_entries_created", 0)
            self.db_set("gl_entries_submitted", 0)
            self.set_status(update=True, status="Cancelled")
            self.db_set("error_message", "")

    def delete_linked_gl_entries(self):
        cancelled_doc = frappe.db.sql_list("""select name from `tabEmployee Resignation` 
		where docstatus = 2 """)
        frappe.db.sql("""delete from `tabGL Entry` 
                    where voucher_type = 'Employee Resignation' and voucher_no in (%s)""" 
                    % (', '.join(['%s']*len(cancelled_doc))), tuple(cancelled_doc))



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
def cost_center(company):
    doc=  frappe.get_doc('Company',company)
    return doc.cost_center

@frappe.whitelist()
def get_employee_equity_balance(dict_doc):
        dict_doc = json.loads(dict_doc)
        #resignation_date =datetime.datetime.strptime(dict_doc["resignation_date"], '%Y-%m-%d')
        resignation_date = str(dict_doc["resignation_date"]) 
        date_of_joining = str(dict_doc["date_of_joining"])    
        employee_name = dict_doc["employee"]
        employee_contr = flt(dict_doc["employee_contr"])
        pl_employee_contr = flt(dict_doc["pl_employee_contr"])
        bank_contr = flt(dict_doc["bank_contr"])
        pl_bank_contr = flt(dict_doc["pl_bank_contr"])
        withdraw_amount = flt(dict_doc["withdraw_amount"])                
        total_right = flt(dict_doc["total_right"])                
        deserved_amount = flt(dict_doc["deserved_amount"])                                
       
        if resignation_date and date_of_joining:
            res_date = datetime.datetime.strptime(resignation_date, '%Y-%m-%d')
            join_date = datetime.datetime.strptime(date_of_joining, '%Y-%m-%d')
            delta = res_date - join_date
            emp_contr_perc = frappe.db.get_single_value('Saving Fund Settings', 'employee_contr_per')/100
            bank_contr_perc = frappe.db.get_single_value('Saving Fund Settings', 'bank_contr_per')/100
            number_year = delta.days / 365.0
            emp_amount = 0
            bank_amount = 0
            income_amount = 0
            income_emp_amount = 0
            income_bank_amount = 0

            if number_year < 1:
                 if employee_contr - withdraw_amount > 0 :
                      emp_amount = employee_contr - withdraw_amount
                      income_emp_amount = pl_employee_contr
                      income_bank_amount = bank_contr + pl_bank_contr

            if number_year >= 1 and number_year < 3:
                 if (employee_contr + pl_employee_contr) - (withdraw_amount) > 0:
                      emp_amount = (employee_contr + pl_employee_contr) - (withdraw_amount)
                      income_bank_amount = bank_contr + pl_bank_contr
            if number_year >= 3:
                 if (employee_contr + pl_employee_contr) - (emp_contr_perc * withdraw_amount) > 0:
                      emp_amount = (employee_contr + pl_employee_contr) - ((1/3.0) * withdraw_amount)
                 if (bank_contr + pl_bank_contr) - (bank_contr_perc * withdraw_amount) > 0:
                      bank_amount = (bank_contr + pl_bank_contr) - ((2/3.0) * withdraw_amount)
            if total_right - deserved_amount > 0:
                 income_amount = total_right - deserved_amount
            data = {
                'emp_amount': emp_amount,
                'bank_amount': bank_amount,
                'income_amount': income_amount,
                'income_emp_amount': income_emp_amount,
                'income_bank_amount': income_bank_amount,
            }

            return json.dumps(data)
        return 
           