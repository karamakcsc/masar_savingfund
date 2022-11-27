# Copyright (c) 2022, Karama kcsc and contributors
# For license information, please see license.txt

# import frappe
from __future__ import unicode_literals
from frappe import _
import frappe, erpnext, json,datetime

def execute(filters=None):
	return get_columns(), get_data(filters)

def get_data(filters):
	date_to = filters.get('date_to') #date range
	trans_date = datetime.datetime.strptime(date_to, '%Y-%m-%d')
	# month_to = trans_date.month
	# year_to = trans_date.year
	# up_to = month_to + ((year_to - 1) * 12)
	# date_prev = frappe.utils.add_months(date_to, -1)

	#Conditions
	# conditions = " "
	# if(filters.get('employee')):conditions += f" AND tial.employee LIKE '%{filters.get('employee')}' "
	# if(filters.get('item_group')):conditions += f" AND tsii.item_group='{filters.get('item_group')}' "
	# if(filters.get('customer_name')):conditions += f" AND tsi.customer_name LIKE '%{filters.get('customer_name')}' "

	#SQL Query

	return frappe.db.sql(f"""
							With pl
						as (Select tial.employee,tial.employee_name ,SUM(tial.pl_employee_contr) as total_employee_pl,
						SUM(tial.pl_bank_contr) as total_bank_pl,
							   SUM(tial.pl_employee_contr) + SUM(tial.pl_bank_contr) as total_pl
						From `tabIncome Allocation Line` tial
						Inner Join `tabIncome Allocation` tia on tial.parent =tia.name
						Where tia.posting_date < '{date_to}'
							  and tia.docstatus = 1
						Group By tial.employee,tial.employee_name),

						contr as (Select tecl.employee,tecl.employee_name ,SUM(tecl.employee_contr) total_employee_contr,SUM(tecl.bank_contr) total_bank_contr,
						(SUM(tecl.employee_contr)+SUM(tecl.bank_contr)) total_contr
						From `tabEmployee Contribution Line` tecl
						Inner Join `tabEmployee Contribution` tec on tecl.parent =tec.name
						Where tec.posting_date <= '{date_to}'
							  and tec.docstatus = 1
						Group By tecl.employee,tecl.employee_name
						)

						Select c.employee,c.employee_name,total_employee_contr,total_bank_contr,total_contr,
							   IFNULL(p.total_employee_pl,0)as total_employee_pl ,IFNULL(total_bank_pl,0) total_bank_pl,IFNULL(total_pl,0) total_pl,
							   (IFNULL(total_contr,0) + IFNULL(total_pl,0) ) as total_right
						from contr as c
						Left Join pl as p on c.employee = p.employee;""")




def get_columns():
	return [
	   "Employee #: Link/Employee:200",
	   "Employee Name: Data:120",
	   "Total Employee Contr: Data:200",
	   "Total Bank Contr: Data:200",
	   "Total Contr: Data:200",
	   "Total Employee P&L: Data:200",
	   "Total Bank P&L: Data:200",
	   "Total P&L: Data:200",
	   "Total Rights: Data:200"

	]
