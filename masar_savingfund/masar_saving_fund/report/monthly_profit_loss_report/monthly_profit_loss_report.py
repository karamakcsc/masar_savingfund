# Copyright (c) 2022, KCSC and contributors
# For license information, please see license.txt

# import frappe

from __future__ import unicode_literals
from frappe import _
import frappe

def execute(filters=None):
	return get_columns(), get_data(filters)

def get_data(filters):
	_from, to = filters.get('from'), filters.get('to') #date range
	#Conditions
	conditions = "AND 1=1"
	if(filters.get('employee_no')):conditions += f" AND te.name LIKE '%{filters.get('employee_no')}' "
	# if(filters.get('employee')):conditions += f" AND te.employee_name = '{filters.get('employee')}' "
	# if(filters.get('customer_name')):conditions += f" AND tsi.customer_name LIKE '%{filters.get('customer_name')}' "

	#SQL Query
	data = frappe.db.sql(f""" Select te.name, te.employee_name, tia.posting_date, Round(tial.pl_employee_contr,3), Round(tial.pl_bank_contr,3), Round(tial.pl_total,3)
								FROM `tabIncome Allocation Line` tial
								INNER JOIN `tabIncome Allocation` tia on tia.name = tial.parent
								INNER JOIN `tabEmployee` te on te.name = tial.employee
								Where tia.docstatus =1 AND
								(tia.posting_date BETWEEN '{_from}' AND '{to}')
							 	{conditions};""")
	return data

	# return data

def get_columns():
	return [
	   "Employee Number: Link/Employee:100",
	   "Employee Name: Data/Employee:200",
	   "Posting Date: Date/ Posting Date:120",
	   "P&L Employee Contribution:  Data/:200",
	   "P&L Bank Contribution:  Data/:200",
	   "Monthly Profit/Loss Report: Data:200"

	]
