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
def get_exist_income_allocation_in_month(selected_employees,date_to):
	selected_employees = json.loads(selected_employees)
	employees_tuple = tuple(selected_employees)
	emp = employees_tuple[0]
	trans_date = datetime.datetime.strptime(date_to, '%Y-%m-%d')
	month_to = trans_date.month
	year_to = trans_date.year
	up_to = month_to + ((year_to - 1) * 12)

	if len(selected_employees) != 1:
		return frappe.db.sql(f"""
		Select tial.employee,tial.employee_name
		From `tabIncome Allocation Line` tial
		Inner Join `tabIncome Allocation` tia on tial.parent =tia.name
		Where tial.employee  in {employees_tuple} and month(tia.posting_date) + ((year(tia.posting_date) - 1) * 12) = {up_to}
			  and tia.docstatus = 1""",as_dict=True)
	else:

		return frappe.db.sql(f"""
		Select tial.employee,tial.employee_name
		From `tabIncome Allocation Line` tial
		Inner Join `tabIncome Allocation` tia on tial.parent =tia.name
		Where tial.employee  = '{emp}' and month(tia.posting_date) + ((year(tia.posting_date) - 1) * 12) = {up_to}
			  and tia.docstatus = 1""",as_dict=True)




@frappe.whitelist()
def get_interim_revenue_account():
	return frappe.db.get_single_value('Saving Fund Settings', 'interim_revenue')

@frappe.whitelist()
def get_current_year_profit_account():
	return frappe.db.get_single_value('Saving Fund Settings', 'current_year_profit')

class InvalidIncomeAllocation(ValidationError):
	pass

class IncomeAllocation(AccountsController):
	def __init__(self, *args, **kwargs):
		super(IncomeAllocation, self).__init__(*args, **kwargs)

	def validate(self):
		pass

	def on_submit(self):
		self.make_gl()

	def on_cancel(self):
		self.delete_linked_gl_entries()
		
	def make_gl(self):
		gl_entries = []
		for d in self.get("employees"):
			gl_entries.append(
					self.get_gl_dict({
						"account": self.current_year_profit,
						#"account_currency": d.paid_from_account_currency,
						"against": self.interim_revenue,
						"credit_in_account_currency": d.pl_employee_contr,
						"credit": d.pl_employee_contr,
						"employee": d.employee,
						"remarks": d.employee + ' : ' + d.employee_name,
						"cost_center": self.cost_center
						}))
			gl_entries.append(
					self.get_gl_dict({
						"account": self.interim_revenue,
						#"account_currency": d.paid_to_account_currency,
						"against": self.current_year_profit,
						"debit_in_account_currency": d.pl_employee_contr,
						"debit": d.pl_employee_contr,
						"employee": d.employee,
						"remarks": d.employee + ' : ' + d.employee_name,
						"cost_center": self.cost_center
						}))
			gl_entries.append(
					self.get_gl_dict({
						"account": self.current_year_profit,
						#"account_currency": d.paid_from_account_currency,
						"against": self.interim_revenue,
						"credit_in_account_currency": d.pl_bank_contr,
						"credit": d.pl_bank_contr,
						"employee": d.employee,
						"remarks": d.employee + ' : ' + d.employee_name,
						"cost_center": self.cost_center
						}))
			gl_entries.append(
					self.get_gl_dict({
							"account": self.interim_revenue,
							#"account_currency": d.paid_to_account_currency,
							"against": self.current_year_profit,
							"debit_in_account_currency": d.pl_bank_contr,
							"debit": d.pl_bank_contr,
							"employee": d.employee,
							"remarks": d.employee + ' : ' + d.employee_name,
							"cost_center": self.cost_center
						}))
		if gl_entries:
			make_gl_entries(gl_entries, cancel=0, adv_adj=0)


####### Mohammad_Khalil ########
	@frappe.whitelist()
	def fill_employee_details(self):
		cond  = "1=1 "
		if self.status:
			cond += f" AND te.status= '{self.status}'"

		results = frappe.db.sql(f"""
			SELECT 
				te.employee,
				te.employee_name,
				te.status,
				IFNULL(te.relieving_date, '') AS relieving_date
			FROM 
				tabEmployee te
			WHERE 
				{cond}
			""" , as_dict = True)
		

		self.set("employees", [])
		fill_emp = []
		for result in results:
	
			fill_emp.append({
				"employee":result.get('employee'), 
				"employee_name":  result.get('employee_name'), 
				"status" : result.get('status'),
				"resignation_date" : result.get('relieving_date')

				# "pl_bank_contr" : result.get('pl_bank_contr'),
				# "employee_contr" : result.get('employee_contr'),
				# "total_right" : result.get('total_right')					
					
				})
		self.set("employees", fill_emp)
		self.number_of_employees = len(results)
		# self.save()
		return 'ok'
		
####### Mohammad_Khalil ########

	def delete_linked_gl_entries(self):
		cancelled_doc = frappe.db.sql_list("""select name from `tabIncome Allocation` 
		where docstatus = 2 """)
		frappe.db.sql("""delete from `tabGL Entry` 
					where voucher_type = 'Income Allocation' and voucher_no in (%s)""" 
					% (', '.join(['%s']*len(cancelled_doc))), tuple(cancelled_doc))