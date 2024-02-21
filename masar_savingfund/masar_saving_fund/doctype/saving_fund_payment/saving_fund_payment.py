# Copyright (c) 2022, Karama kcsc and contributors
# For license information, please see license.txt
# import frappe
# Copyright (c) 2022, Karama kcsc and contributors
# For license information, please see license.txt

# import frappe
from __future__ import unicode_literals
import frappe, erpnext, json, datetime
from frappe import _, scrub, ValidationError
from frappe.utils import flt, comma_or, nowdate, getdate
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from frappe.model.document import Document

class InvalidSavingFundPayment(ValidationError):
    pass

class SavingFundPayment(AccountsController):
    def __init__(self, *args, **kwargs):
        super(SavingFundPayment, self).__init__(*args, **kwargs)

    def validate(self):
        pass

    def on_submit(self):
        self.make_gl()

    def on_cancel(self):
        self.delete_linked_gl_entries()

    def make_gl(self):
        # if self.paid_amount > self.deserved_amount:
        #     frappe.throw('The paid amount can not be greater than deserved amount !')

        if  self.date_of_joining:
            res_date = frappe.utils.today()
            res_date = datetime.datetime.strptime(res_date, '%Y-%m-%d')
            if self.status =="Left":
                 res_date = datetime.datetime.strptime(self.resignation_date, '%Y-%m-%d')

            join_date = datetime.datetime.strptime(self.date_of_joining, '%Y-%m-%d')
            delta = res_date - join_date
            number_year = delta.days / 365.0
            emp_contr_perc = frappe.db.get_single_value('Saving Fund Settings', 'employee_contr_per')/100
            bank_contr_perc = frappe.db.get_single_value('Saving Fund Settings', 'bank_contr_per')/100
            total_amount_contr = self.employee_contr + self.bank_contr
            total_amount_pl = self.pl_employee_contr + self.pl_bank_contr
            gl_entries = []
            if number_year < 1:
                if self.status =="Left":
                    gl_entries.append(
                        self.get_gl_dict({
                            "account": self.cash_account,
                            # "account_currency": d.paid_from_account_currency,
                            "against": self.liability_account,
                            "credit_in_account_currency": self.paid_amount,
                            "credit": self.paid_amount,
                            "employee": self.employee,
                            "remarks": self.employee + ' : ' + self.employee_name
                        }))
                    gl_entries.append(
                        self.get_gl_dict({
                        "account": self.liability_account,
                        #"account_currency": d.paid_to_account_currency,
                        "against": self.cash_account,
                        "debit_in_account_currency": self.paid_amount,
                        "debit": self.paid_amount,
                        "employee": self.employee,
                        "remarks": self.employee + ' : ' + self.employee_name
                        }))

                else: 

                    gl_entries.append(
                        self.get_gl_dict({
                            "account": self.cash_account,
                            # "account_currency": d.paid_from_account_currency,
                            "against": self.employee_equity,
                            "credit_in_account_currency": self.paid_amount,
                            "credit": self.paid_amount,
                            "employee": self.employee,
                            "remarks": self.employee + ' : ' + self.employee_name
                        }))
                    gl_entries.append(
                        self.get_gl_dict({
                        "account": self.employee_equity,
                        #"account_currency": d.paid_to_account_currency,
                        "against": self.cash_account,
                        "debit_in_account_currency": self.paid_amount,
                        "debit": self.paid_amount,
                        "employee": self.employee,
                        "remarks": self.employee + ' : ' + self.employee_name
                        }))

            if number_year >= 1 and number_year < 3:
                if self.status =="Left":
                    gl_entries.append(
                        self.get_gl_dict({
                            "account": self.cash_account,
                            # "account_currency": d.paid_from_account_currency,
                            "against": self.liability_account,
                            "credit_in_account_currency": self.paid_amount,
                            "credit": self.paid_amount,
                            "employee": self.employee,
                            "remarks": self.employee + ' : ' + self.employee_name
                        }))
                    gl_entries.append(
                        self.get_gl_dict({
                        "account": self.liability_account,
                        #"account_currency": d.paid_to_account_currency,
                        "against": self.cash_account,
                        "debit_in_account_currency": self.paid_amount,
                        "debit": self.paid_amount,
                        "employee": self.employee,
                        "remarks": self.employee + ' : ' + self.employee_name
                        }))                  
                else:   
                    gl_entries.append(
                        self.get_gl_dict({
                            "account": self.cash_account,
                            # "account_currency": d.paid_from_account_currency,
                            "against": self.employee_equity,
                            "credit_in_account_currency": self.paid_amount,
                            "credit": self.paid_amount ,
                            "employee": self.employee,
                            "remarks": self.employee + ' : ' + self.employee_name
                        }))
                    gl_entries.append(
                        self.get_gl_dict({
                            "account": self.employee_equity,
                            # "account_currency": d.paid_to_account_currency,
                            "against": self.cash_account,
                            "debit_in_account_currency": self.paid_amount ,
                            "debit": self.paid_amount ,
                            "employee": self.employee,
                            "remarks": self.employee + ' : ' + self.employee_name
                        }))

            if number_year >= 3:
                if self.status =="Left":               
                    gl_entries.append(
                        self.get_gl_dict({
                            "account": self.cash_account,
                            # "account_currency": d.paid_from_account_currency,
                            "against": self.liability_account,
                            "credit_in_account_currency": self.paid_amount,
                            "credit": self.paid_amount,
                            "employee": self.employee,
                            "remarks": self.employee + ' : ' + self.employee_name
                        }))
                    gl_entries.append(
                        self.get_gl_dict({
                        "account": self.liability_account,
                        #"account_currency": d.paid_to_account_currency,
                        "against": self.cash_account,
                        "debit_in_account_currency": self.paid_amount,
                        "debit": self.paid_amount,
                        "employee": self.employee,
                        "remarks": self.employee + ' : ' + self.employee_name
                        }))
                    

                else:
                    gl_entries.append(
                        self.get_gl_dict({
                            "account": self.cash_account,
                            # "account_currency": d.paid_from_account_currency,
                            "against": self.employee_equity,
                            "credit_in_account_currency":self.paid_amount * (1/3.0),
                            "credit": self.paid_amount * (1/3.0),
                            "employee": self.employee,
                            "remarks": self.employee + ' : ' + self.employee_name
                        }))
                    gl_entries.append(
                        self.get_gl_dict({
                            "account": self.employee_equity,
                            # "account_currency": d.paid_to_account_currency,
                            "against": self.cash_account,
                            "debit_in_account_currency": self.paid_amount * (1/3.0),
                            "debit":self.paid_amount * (1/3.0),
                            "employee": self.employee,
                            "remarks": self.employee + ' : ' + self.employee_name
                        }))
                    
                                            
                    gl_entries.append(
                        self.get_gl_dict({
                            "account": self.cash_account,
                            # "account_currency": d.paid_from_account_currency,
                            "against": self.bank_equity,
                            "credit_in_account_currency": self.paid_amount * (2/3.0),
                            "credit": self.paid_amount * (2/3.0),
                            "employee": self.employee,
                            "remarks": self.employee + ' : ' + self.employee_name
                        }))
                    gl_entries.append(
                        self.get_gl_dict({
                            "account": self.bank_equity,
                            # "account_currency": d.paid_to_account_currency,
                            "against": self.cash_account,
                            "debit_in_account_currency": self.paid_amount * (2/3.0),
                            "debit": self.paid_amount * (2/3.0),
                            "employee": self.employee,
                            "remarks": self.employee + ' : ' + self.employee_name
                        }))


            if gl_entries:
                make_gl_entries(gl_entries, cancel=0, adv_adj=0)


    def delete_linked_gl_entries(self):
        cancelled_doc = frappe.db.sql_list("""select name from `tabSaving Fund Payment` 
		where docstatus = 2 """)
        frappe.db.sql("""delete from `tabGL Entry` 
                    where voucher_type = 'Saving Fund Payment' and voucher_no in (%s)""" 
                    % (', '.join(['%s']*len(cancelled_doc))), tuple(cancelled_doc))