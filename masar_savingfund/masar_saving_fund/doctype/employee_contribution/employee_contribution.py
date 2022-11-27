# Copyright (c) 2022, Karama kcsc and contributors
# For license information, please see license.txt

# import frappe
from __future__ import unicode_literals
import frappe, erpnext, json,datetime
from frappe import _, scrub, ValidationError
from frappe.utils import flt, comma_or, nowdate, getdate
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from frappe.model.document import Document

@frappe.whitelist()
def get_exist_employee_in_month(selected_employees,date_to):
	selected_employees = json.loads(selected_employees)
	employees_tuple = tuple(selected_employees)
	emp = employees_tuple[0]
	trans_date = datetime.datetime.strptime(date_to, '%Y-%m-%d')
	month_to = trans_date.month
	year_to = trans_date.year
	up_to = month_to + ((year_to - 1) * 12)

	if len(selected_employees) != 1:
		return frappe.db.sql(f"""
		Select tecl.employee,tecl.employee_name
			From `tabEmployee Contribution Line` tecl
			Inner Join `tabEmployee Contribution` tec on tecl.parent =tec.name
			Where tecl.employee  in {employees_tuple} and month(tec.posting_date) + ((year(tec.posting_date) - 1) * 12) = {up_to}
				  and tec.docstatus = 1""",as_dict=True)
	else:

		return frappe.db.sql(f"""
		Select tecl.employee,tecl.employee_name
			From `tabEmployee Contribution Line` tecl
			Inner Join `tabEmployee Contribution` tec on tecl.parent =tec.name
			Where tecl.employee  = '{emp}' and month(tec.posting_date) + ((year(tec.posting_date) - 1) * 12) = {up_to}
				  and tec.docstatus = 1""",as_dict=True)

@frappe.whitelist()
def get_employee_contr_perc():
	return frappe.db.get_single_value('Saving Fund Settings', 'employee_contr_per')

@frappe.whitelist()
def get_bank_contr_perc():
	return frappe.db.get_single_value('Saving Fund Settings', 'bank_contr_per')

@frappe.whitelist()
def get_cash_account():
	return frappe.db.get_single_value('Saving Fund Settings', 'cash_account')

@frappe.whitelist()
def get_employee_equity_account():
	return frappe.db.get_single_value('Saving Fund Settings', 'employee_equity')

@frappe.whitelist()
def get_bank_equity_account():
	return frappe.db.get_single_value('Saving Fund Settings', 'bank_equity')

class InvalidEmployeeContribution(ValidationError):
	pass

class EmployeeContribution(AccountsController):
	def __init__(self, *args, **kwargs):
		super(EmployeeContribution, self).__init__(*args, **kwargs)

	def validate(self):
		pass

	def on_submit(self):
		self.make_gl()

	# def on_cancel(self, method):
	#     delete_cheque(self)

	def make_gl(self):
		gl_entries = []
		for d in self.get("employee_contr_lines"):
			gl_entries.append(
					self.get_gl_dict({
						"account": self.cash_account,
						#"account_currency": d.paid_from_account_currency,
						"against": self.employee_equity,
						"credit_in_account_currency": d.employee_contr,
						"credit": d.employee_contr,
						"employee": d.employee,
						"remarks": d.employee + ' : ' + d.employee_name
						}))
			gl_entries.append(
					self.get_gl_dict({
						"account": self.employee_equity,
						#"account_currency": d.paid_to_account_currency,
						"against": self.cash_account,
						"debit_in_account_currency": d.employee_contr,
						"debit": d.employee_contr,
						"employee": d.employee,
						"remarks": d.employee + ' : ' + d.employee_name
						}))
			gl_entries.append(
					self.get_gl_dict({
						"account": self.cash_account,
						#"account_currency": d.paid_from_account_currency,
						"against": self.bank_equity,
						"credit_in_account_currency": d.bank_contr,
						"credit": d.bank_contr,
						"employee": d.employee,
						"remarks": d.employee + ' : ' + d.employee_name
						}))
			gl_entries.append(
					self.get_gl_dict({
							"account": self.bank_equity,
							#"account_currency": d.paid_to_account_currency,
							"against": self.cash_account,
							"debit_in_account_currency": d.bank_contr,
							"debit": d.bank_contr,
							"employee": d.employee,
							"remarks": d.employee + ' : ' + d.employee_name
						}))
		if gl_entries:
			make_gl_entries(gl_entries, cancel=0, adv_adj=0)
