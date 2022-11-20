# Copyright (c) 2022, Karama kcsc and contributors
# For license information, please see license.txt

# import frappe

#
# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data

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
	conditions = " AND 1=1 "
	if(filters.get('inv_no')):conditions += f" AND tial.employee LIKE '%{filters.get('emp')}' "
	# if(filters.get('item_group')):conditions += f" AND tsii.item_group='{filters.get('item_group')}' "
	# if(filters.get('customer_name')):conditions += f" AND tsi.customer_name LIKE '%{filters.get('customer_name')}' "

	#SQL Query

	data = frappe.db.sql(f""" Select tia.name, tial.employee, tial.employee_name, tia.date, tial.pl_employee_contr, tial.pl_bank_contr, tial.pl_total,
								tial.employee_contr, tial.pl_employee_contr_prev, tial.bank_contr, tial.pl_employee_contr_prev, tial.total_right
								From `tabIncome Allocation` tia
								left JOIN `tabIncome Allocation Line` tial on  tia.name = tial.parent
								Where tia.docstatus =1 AND
							(tia.date BETWEEN '{_from}' AND '{to}')
							 {conditions};""")
	return data





	# return data

def get_columns():
	return [
	   "Document #: Data:200",
	   "Employee #: Data:200",
	   "Employee Name: Data:200",
	   "Date: Date:120",
	   "P&L Employee Contribution: Data:200",
	   "P&L Bank Contribution: Data:200",
	   "P&L Total: Data:200",
	   "Employee Contribution: Data:200",
	   "P&L Employee Contr till Previous Month: Data:200",
	   "Bank Contribution: Data:200",
	   "P&L Bank Contr till Previous Month: Data:200",
	   "Total Right: Data:150"
	   # "Delivery Note QTY: Data:150",
	   # "Sales Rate: Data:200",
	   # "Net Sales Rate Per Unit: Data:200",
	   # "Cost Per Unit: Data:200",
	   # "Sales Amount: Data:200",
	   # "Net Sales Amount: Data:200",
	   # "Invoice Cost: Data:200",
	   # "Cost By Sales Invoice: Data:200",
	   # "Invoice Cost: Data:200",
	   #"Unit Cost: Data:200",
	   # "Gross Profit Amount: Data:200",
	   # "Gross Profit Percentage: Percent:200",
	   # "Discount Per Unit: Data:200",
	   # "Total Discount Amount: Data:200",
	   # "Additional Discount Amount: Data:200"

	]
