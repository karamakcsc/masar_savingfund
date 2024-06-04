# Copyright (c) 2023, Karama kcsc and contributors
# For license information, please see license.txt

# import frappe


# import frappe
from __future__ import unicode_literals
from frappe import _
import frappe, erpnext, json,datetime
from typing import Dict, List, Optional, Tuple

def execute(filters=None):
	return get_columns(), get_data(filters)

def get_data(filters):
	_from = filters.get('from')
	to = filters.get('to')  # date range

	# if _from is not None :
	# 	trans_date = (
	# 		datetime.datetime.strptime(_from, '%Y-%m-%d'),
	# 		# datetime.datetime.strptime(to, '%Y-%m-%d')
	# 	)
	# 	date_rang = f"'{_from}'"
	# else:
	# 	frappe.throw(_("Please provide both 'from'  filters."))

	#SQL Query

	return frappe.db.sql(f"""
		WITH pl AS (
    SELECT 
        tial.employee,
        tial.employee_name,
        SUM(tial.pl_employee_contr) AS total_employee_pl,
        SUM(tial.pl_bank_contr) AS total_bank_pl,
        SUM(tial.pl_employee_contr) + SUM(tial.pl_bank_contr) AS total_pl,
        EXTRACT(MONTH FROM tia.posting_date) AS month
    FROM `tabIncome Allocation Line` tial
    INNER JOIN `tabIncome Allocation` tia ON tial.parent = tia.name
    INNER JOIN `tabEmployee` em ON tial.employee = em.name
    WHERE tia.posting_date BETWEEN '{_from}' AND '{to}'
    AND tia.posting_date > em.date_of_joining
    AND tia.docstatus = 1
    GROUP BY tial.employee, tial.employee_name, EXTRACT(MONTH FROM tia.posting_date)
),

contr AS (
    SELECT 
        tecl.employee,
        tecl.employee_name,
        SUM(tecl.employee_contr) AS total_employee_contr,
        SUM(tecl.bank_contr) AS total_bank_contr,
        (SUM(tecl.employee_contr) + SUM(tecl.bank_contr)) AS total_contr,
        EXTRACT(MONTH FROM tec.posting_date) AS month
    FROM `tabEmployee Contribution Line` tecl
    INNER JOIN `tabEmployee Contribution` tec ON tecl.parent = tec.name
    INNER JOIN `tabEmployee` em ON tecl.employee = em.name
    WHERE tec.posting_date BETWEEN '{_from}' AND '{to}'
    AND tec.posting_date > em.date_of_joining
    AND tec.docstatus = 1
    GROUP BY tecl.employee, tecl.employee_name, EXTRACT(MONTH FROM tec.posting_date)
),

withdraw AS (
    SELECT 
        tsfp.employee,
        tsfp.employee_name,
        SUM(tsfp.paid_amount) AS total_paid_amount,
        EXTRACT(MONTH FROM tsfp.posting_date) AS month
    FROM `tabSaving Fund Payment` tsfp
    INNER JOIN `tabEmployee` em ON tsfp.employee = em.name
    WHERE tsfp.posting_date BETWEEN '{_from}' AND '{to}'
    AND tsfp.posting_date > em.date_of_joining
    AND tsfp.docstatus = 1
    AND tsfp.status = 'Active'
    GROUP BY tsfp.employee, tsfp.employee_name, EXTRACT(MONTH FROM tsfp.posting_date)
),

liability AS (
    SELECT 
        ter.employee,
        ter.employee_name,
        (ter.employee_equity_amount + ter.bank_equity_amount) AS liability_amount,
        EXTRACT(MONTH FROM ter.posting_date) AS month
    FROM `tabEmployee Resignation` ter
    INNER JOIN `tabEmployee` em ON ter.employee = em.name
    WHERE ter.posting_date BETWEEN '{_from}' AND '{to}'
    AND ter.posting_date > em.date_of_joining
    AND ter.docstatus = 1
    AND ter.resignation_date = (SELECT MAX(ter.resignation_date))
    GROUP BY ter.employee, ter.employee_name, EXTRACT(MONTH FROM ter.posting_date)
    ORDER BY ter.resignation_date
)

SELECT 
    e.employee,
    e.employee_name,
	MAX(CASE WHEN c.month <'{_from}' THEN (IFNULL(c.total_contr, 0) + IFNULL(p.total_pl, 0) - IFNULL(w.total_paid_amount, 0) - IFNULL(l.liability_amount, 0)) END) AS `Previous Period`,
    MAX(CASE WHEN c.month = 1 THEN (IFNULL(c.total_contr, 0) + IFNULL(p.total_pl, 0) - IFNULL(w.total_paid_amount, 0) - IFNULL(l.liability_amount, 0)) END) AS `January`,
    MAX(CASE WHEN c.month = 2 THEN (IFNULL(c.total_contr, 0) + IFNULL(p.total_pl, 0) - IFNULL(w.total_paid_amount, 0) - IFNULL(l.liability_amount, 0)) END) AS `February`,
    MAX(CASE WHEN c.month = 3 THEN (IFNULL(c.total_contr, 0) + IFNULL(p.total_pl, 0) - IFNULL(w.total_paid_amount, 0) - IFNULL(l.liability_amount, 0)) END) AS `March`,
    MAX(CASE WHEN c.month = 4 THEN (IFNULL(c.total_contr, 0) + IFNULL(p.total_pl, 0) - IFNULL(w.total_paid_amount, 0) - IFNULL(l.liability_amount, 0)) END) AS `April`,
    MAX(CASE WHEN c.month = 5 THEN (IFNULL(c.total_contr, 0) + IFNULL(p.total_pl, 0) - IFNULL(w.total_paid_amount, 0) - IFNULL(l.liability_amount, 0)) END) AS `May`,
    MAX(CASE WHEN c.month = 6 THEN (IFNULL(c.total_contr, 0) + IFNULL(p.total_pl, 0) - IFNULL(w.total_paid_amount, 0) - IFNULL(l.liability_amount, 0)) END) AS `June`,
    MAX(CASE WHEN c.month = 7 THEN (IFNULL(c.total_contr, 0) + IFNULL(p.total_pl, 0) - IFNULL(w.total_paid_amount, 0) - IFNULL(l.liability_amount, 0)) END) AS `July`,
    MAX(CASE WHEN c.month = 8 THEN (IFNULL(c.total_contr, 0) + IFNULL(p.total_pl, 0) - IFNULL(w.total_paid_amount, 0) - IFNULL(l.liability_amount, 0)) END) AS `August`,
    MAX(CASE WHEN c.month = 9 THEN (IFNULL(c.total_contr, 0) + IFNULL(p.total_pl, 0) - IFNULL(w.total_paid_amount, 0) - IFNULL(l.liability_amount, 0)) END) AS `September`,
    MAX(CASE WHEN c.month = 10 THEN (IFNULL(c.total_contr, 0) + IFNULL(p.total_pl, 0) - IFNULL(w.total_paid_amount, 0) - IFNULL(l.liability_amount, 0)) END) AS `October`,
    MAX(CASE WHEN c.month = 11 THEN (IFNULL(c.total_contr, 0) + IFNULL(p.total_pl, 0) - IFNULL(w.total_paid_amount, 0) - IFNULL(l.liability_amount, 0)) END) AS `November`,
    MAX(CASE WHEN c.month = 12 THEN (IFNULL(c.total_contr, 0) + IFNULL(p.total_pl, 0) - IFNULL(w.total_paid_amount, 0) - IFNULL(l.liability_amount, 0)) END) AS `December`
FROM tabEmployee e
LEFT JOIN contr c ON e.employee = c.employee
LEFT JOIN pl p ON e.employee = p.employee AND c.month = p.month
LEFT JOIN withdraw w ON e.employee = w.employee AND c.month = w.month
LEFT JOIN liability l ON e.employee = l.employee AND c.month = l.month
GROUP BY e.employee, e.employee_name
ORDER BY e.employee;
;""")					

def get_columns():
	return [
	   "Employee #: Link/Employee:150",
	   "Employee Name: Data:200",
	   "Previous Period: Data:200",
	   "January: Data:200",
	   "February: Data:200",
	   "March: Data:200",
	   "April: Data:200",
	   "May: Data:200",
	   "June: Data:200",
	   "July: Data:200",
	   "August: Data:200",
	   "September: Data:200", 
	   "October: Data:200",
	   "November: Data:200",
	   "December: Data:200"

	]
