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
	condiotions = " 1=1 "
	if filters.get('employee'):
		condiotions += f" AND e.name = '{filters.get('employee')}' "
	date_to = filters.get('date_to') #date range
	trans_date = datetime.datetime.strptime(date_to, '%Y-%m-%d')

	#SQL Query

	return frappe.db.sql(f"""
								WITH 
							pl AS (
								SELECT
									tial.employee,
									tial.employee_name,
									SUM(tial.pl_employee_contr) AS total_employee_pl,
									SUM(tial.pl_bank_contr) AS total_bank_pl,
									SUM(tial.pl_employee_contr) + SUM(tial.pl_bank_contr) AS total_pl
								FROM
									`tabIncome Allocation Line` tial
								INNER JOIN
									`tabIncome Allocation` tia ON tial.parent = tia.name
								INNER JOIN
									`tabEmployee` em ON tial.employee = em.name
								WHERE
									tia.posting_date <= '{date_to}' AND tia.posting_date > em.date_of_joining
									AND tia.docstatus = 1
								GROUP BY
									tial.employee,
									tial.employee_name
							),

							contr AS (
								SELECT
									tecl.employee,
									tecl.employee_name,
									SUM(tecl.employee_contr) AS total_employee_contr,
									SUM(tecl.bank_contr) AS total_bank_contr,
									SUM(tecl.employee_contr) + SUM(tecl.bank_contr) AS total_contr
								FROM
									`tabEmployee Contribution Line` tecl
								INNER JOIN
									`tabEmployee Contribution` tec ON tecl.parent = tec.name
								INNER JOIN
									`tabEmployee` em ON tecl.employee = em.name
								WHERE
									tec.posting_date <= '{date_to}' AND tec.posting_date > em.date_of_joining
									AND tec.docstatus = 1
								GROUP BY
									tecl.employee,
									tecl.employee_name
							),

							withdraw AS (
								SELECT
									tsfp.employee,
									tsfp.employee_name,
									SUM(tsfp.paid_amount) AS total_paid_amount
								FROM
									`tabSaving Fund Payment` tsfp
								INNER JOIN
									`tabEmployee` em ON tsfp.employee = em.name
								WHERE
									tsfp.posting_date <= '{date_to}' AND tsfp.posting_date > em.date_of_joining
									AND tsfp.docstatus = 1
									AND tsfp.status = 'Active'
								GROUP BY
									tsfp.employee,
									tsfp.employee_name
							),

							liability AS (
								SELECT
									ter.employee,
									ter.employee_name,
									SUM(ter.employee_equity_amount + ter.bank_equity_amount) AS liability_amount,
									MAX(ter.posting_date) AS resignation_posting_date
								FROM
									`tabEmployee Resignation` ter
								INNER JOIN
									`tabEmployee` em ON ter.employee = em.name
								WHERE
									ter.posting_date <= '{date_to}' AND ter.posting_date > em.date_of_joining
									AND ter.docstatus = 1
									AND ter.resignation_date = (
										SELECT
											MAX(ter2.resignation_date)
										FROM
											`tabEmployee Resignation` ter2
										WHERE
											ter2.employee = ter.employee
									)
								GROUP BY
									ter.employee,
									ter.employee_name
							)

						SELECT
							e.employee,
							e.employee_name,
							IFNULL(c.total_employee_contr, 0) AS total_employee_contr,
							IFNULL(c.total_bank_contr, 0) AS total_bank_contr,
							IFNULL(c.total_contr, 0) AS total_contr,
							IFNULL(p.total_employee_pl, 0) AS total_employee_pl,
							IFNULL(p.total_bank_pl, 0) AS total_bank_pl,
							IFNULL(p.total_pl, 0) AS total_pl,
							IFNULL(w.total_paid_amount, 0) AS total_withdraw,
							IFNULL(l.liability_amount, 0) AS liability_amount,
							CASE
								WHEN e.status = 'Left' AND '{date_to}' > l.resignation_posting_date THEN 0
								ELSE IFNULL(c.total_contr, 0) +
									 IFNULL(p.total_pl, 0) - 
          							 IFNULL(w.total_paid_amount, 0) - 
                  					 IFNULL(l.liability_amount, 0)
							END AS total_right
						FROM
							tabEmployee AS e
						LEFT JOIN
							contr c ON e.employee = c.employee
						LEFT JOIN
							pl p ON e.employee = p.employee
						LEFT JOIN
							withdraw w ON e.employee = w.employee
						LEFT JOIN
							liability l ON e.employee = l.employee
						WHERE {condiotions}
						;""")					






def get_columns():
	return [
	   "Employee #: Link/Employee:150",
	   "Employee Name: Data:200",
	   "Total Employee Contr: Currency:200",
	   "Total Bank Contr: Currency:200",
	   "Total Contr: Currency:200",
	   "Total Employee P&L: Currency:200",
	   "Total Bank P&L: Currency:200",
	   "Total P&L: Currency:200",
	   "Total Withdraw: Currency:200",
	   "Liabilty Amount: Currency:200",	   
	   "Total Rights: Currency:200"

	]


# -- IF(e.status = 'Left', 0, IFNULL(c.total_contr, 0) + IFNULL(p.total_pl, 0) - IFNULL(w.total_paid_amount, 0) - IFNULL(l.liability_amount, 0)) AS total_rights
# -- IF(e.status = 'Left', 0, IFNULL(c.total_contr, 0) + IFNULL(p.total_pl, 0) - IFNULL(w.total_paid_amount, 0) - IFNULL(l.liability_amount, 0)) AS total_right