# Copyright (c) 2026, Karama kcsc and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


def execute(filters=None):
	report_type = filters.get("report_type") or "Both"
	data = []

	if report_type in ("Employee Contribution", "Both"):
		data += get_contribution_data(filters)
	if report_type in ("Income Allocation", "Both"):
		data += get_income_data(filters)

	columns = get_columns()
	return columns, data


def get_contribution_data(filters):
	conditions = "tec.docstatus = 1"

	if filters.get("from_date"):
		conditions += f" AND tec.posting_date >= '{filters['from_date']}'"
	if filters.get("to_date"):
		conditions += f" AND tec.posting_date <= '{filters['to_date']}'"
	if filters.get("employee"):
		conditions += f" AND tecl.employee = '{filters['employee']}'"
	if not filters.get("show_all"):
		conditions += " AND (IFNULL(tecl.employee_contr_diff, 0) != 0 OR IFNULL(tecl.bank_contr_diff, 0) != 0)"

	rows = frappe.db.sql(f"""
		SELECT
			'Employee Contribution'                                 AS type,
			tec.name                                                AS voucher,
			tec.posting_date                                        AS posting_date,
			tecl.employee                                           AS employee,
			tecl.employee_name                                      AS employee_name,
			tecl.basic_salary                                       AS basic_salary,
			tecl.employee_contr                                     AS expected_emp_amount,
			IFNULL(tecl.employee_contr_diff, 0)                     AS emp_diff,
			tecl.employee_contr + IFNULL(tecl.employee_contr_diff, 0) AS actual_emp_amount,
			tecl.bank_contr                                         AS expected_bank_amount,
			IFNULL(tecl.bank_contr_diff, 0)                         AS bank_diff,
			tecl.bank_contr + IFNULL(tecl.bank_contr_diff, 0)       AS actual_bank_amount
		FROM `tabEmployee Contribution Line` tecl
		INNER JOIN `tabEmployee Contribution` tec ON tecl.parent = tec.name
		WHERE {conditions}
		ORDER BY tec.posting_date, tecl.employee
	""", as_dict=True)

	return rows


def get_income_data(filters):
	conditions = "tia.docstatus = 1"

	if filters.get("from_date"):
		conditions += f" AND tia.posting_date >= '{filters['from_date']}'"
	if filters.get("to_date"):
		conditions += f" AND tia.posting_date <= '{filters['to_date']}'"
	if filters.get("employee"):
		conditions += f" AND tial.employee = '{filters['employee']}'"
	if not filters.get("show_all"):
		conditions += " AND (IFNULL(tial.pl_employee_contr_diff, 0) != 0 OR IFNULL(tial.pl_bank_contr_diff, 0) != 0)"

	rows = frappe.db.sql(f"""
		SELECT
			'Income Allocation'                                               AS type,
			tia.name                                                          AS voucher,
			tia.posting_date                                                  AS posting_date,
			tial.employee                                                     AS employee,
			tial.employee_name                                                AS employee_name,
			NULL                                                              AS basic_salary,
			tial.pl_employee_contr                                            AS expected_emp_amount,
			IFNULL(tial.pl_employee_contr_diff, 0)                            AS emp_diff,
			tial.pl_employee_contr + IFNULL(tial.pl_employee_contr_diff, 0)   AS actual_emp_amount,
			tial.pl_bank_contr                                                AS expected_bank_amount,
			IFNULL(tial.pl_bank_contr_diff, 0)                               AS bank_diff,
			tial.pl_bank_contr + IFNULL(tial.pl_bank_contr_diff, 0)          AS actual_bank_amount
		FROM `tabIncome Allocation Line` tial
		INNER JOIN `tabIncome Allocation` tia ON tial.parent = tia.name
		WHERE {conditions}
		ORDER BY tia.posting_date, tial.employee
	""", as_dict=True)

	return rows


def get_columns():
	return [
		{
			"fieldname": "type",
			"label": "Type",
			"fieldtype": "Data",
			"width": 140
		},
		{
			"fieldname": "voucher",
			"label": "Voucher",
			"fieldtype": "Dynamic Link",
			"options": "type",
			"width": 180
		},
		{
			"fieldname": "posting_date",
			"label": "Posting Date",
			"fieldtype": "Date",
			"width": 110
		},
		{
			"fieldname": "employee",
			"label": "Employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 120
		},
		{
			"fieldname": "employee_name",
			"label": "Employee Name",
			"fieldtype": "Data",
			"width": 180
		},
		{
			"fieldname": "basic_salary",
			"label": "Basic Salary",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "expected_emp_amount",
			"label": "Expected Emp Amount",
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"fieldname": "emp_diff",
			"label": "Emp Diff",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "actual_emp_amount",
			"label": "Actual Emp Amount",
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"fieldname": "expected_bank_amount",
			"label": "Expected Bank Amount",
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"fieldname": "bank_diff",
			"label": "Bank Diff",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "actual_bank_amount",
			"label": "Actual Bank Amount",
			"fieldtype": "Currency",
			"width": 160
		},
	]
