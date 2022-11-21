# Copyright (c) 2022, Karama kcsc and contributors
# For license information, please see license.txt

# import frappe
from __future__ import unicode_literals
import frappe, erpnext, json,datetime
from frappe import _, scrub, ValidationError
from frappe.utils import flt, comma_or, nowdate, getdate
from erpnext.setup.utils import get_exchange_rate
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
			Where tecl.employee  in {employees_tuple} and month(tec.date_transaction) + ((year(tec.date_transaction) - 1) * 12) = {up_to}
				  and tec.docstatus = 1""",as_dict=True)
	else:

		return frappe.db.sql(f"""
		Select tecl.employee,tecl.employee_name
			From `tabEmployee Contribution Line` tecl
			Inner Join `tabEmployee Contribution` tec on tecl.parent =tec.name
			Where tecl.employee  = '{emp}' and month(tec.date_transaction) + ((year(tec.date_transaction) - 1) * 12) = {up_to}
				  and tec.docstatus = 1""",as_dict=True)

@frappe.whitelist()
def get_employee_contr_perc(employee):
	return frappe.db.get_single_value('Saving Fund Settings', 'employee_contr_per')

@frappe.whitelist()
def get_bank_contr_perc(employee):
	return frappe.db.get_single_value('Saving Fund Settings', 'bank_contr_per')	

class EmployeeContribution(Document):
	pass
