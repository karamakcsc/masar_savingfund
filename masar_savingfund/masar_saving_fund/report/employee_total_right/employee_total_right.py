# Copyright (c) 2022, Karama kcsc and contributors
# For license information, please see license.txt

# import frappe
from __future__ import unicode_literals
from frappe import _
import frappe, erpnext, json,datetime
from typing import Dict, List, Optional, Tuple

def execute(filters=None):
	return get_columns(), get_data(filters)

def get_data(filters):
	date_to = filters.get('date_to') #date range
	trans_date = datetime.datetime.strptime(date_to, '%Y-%m-%d')

	#SQL Query

	return frappe.db.sql(f"""
					With pl
						as (Select tial.employee,tial.employee_name ,SUM(tial.pl_employee_contr) as total_employee_pl,SUM(tial.pl_bank_contr) as total_bank_pl,
			            	   SUM(tial.pl_employee_contr) + SUM(tial.pl_bank_contr) as total_pl, pl_total as monthly_profit_loss
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
						),
			            withdraw as (Select tsfp.employee,tsfp.employee_name ,SUM(tsfp.paid_amount) total_paid_amount
			            From `tabSaving Fund Payment` tsfp
			            Where tsfp.posting_date <= '{date_to}'
			                  and tsfp.docstatus = 1
			            Group By tsfp.employee,tsfp.employee_name)

						Select c.employee,c.employee_name,total_employee_contr,total_bank_contr,total_contr,
							   IFNULL(p.total_employee_pl,0)as total_employee_pl ,IFNULL(total_bank_pl,0) total_bank_pl,IFNULL(total_pl,0) total_pl,
							   IFNULL(monthly_profit_loss,0) monthly_profit_loss,IFNULL(w.total_paid_amount,0)as total_withdraw,
							   (IFNULL(total_contr,0) + IFNULL(total_pl,0) - IFNULL(total_paid_amount,0)) as total_right
            				from tabEmployee as e
            				left Join contr c on e.employee = c.employee
            				Left Join pl as p on c.employee = p.employee
            				Left Join withdraw as w on c.employee = w.employee;""")




def get_columns():
	return [
	   "Employee #: Link/Employee:200",
	   "Employee Name: Data:120",
	   "Total Employee Contr: Currency:200",
	   "Total Bank Contr: Currency:200",
	   "Total Contr: Currency:200",
	   "Total Employee P&L: Currency:200",
	   "Total Bank P&L: Currency:200",
	   "Total P&L: Currency:200",
	   "Monthly Profit/Loss: Currency:200",
	   "Total Withdraw: Currency:200",
	   "Total Rights: Currency:200"

	]
