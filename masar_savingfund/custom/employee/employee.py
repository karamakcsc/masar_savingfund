from __future__ import unicode_literals
import frappe, erpnext, json, datetime
from frappe import _, scrub, ValidationError
from frappe.utils import flt, comma_or, nowdate, getdate
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from frappe.model.document import Document


@frappe.whitelist()
def get_employee_savefund_balance(selected_employees, date_to):
    selected_employees = json.loads(selected_employees)
    trans_date = datetime.datetime.strptime(date_to, '%Y-%m-%d')
    up_to = trans_date.month + ((trans_date.year - 1) * 12)

    # بناء شرط الموظفين بشكل آمن
    if len(selected_employees) > 1:
        placeholders = ', '.join(['%s'] * len(selected_employees))
        emp_condition_pl    = f"tial.employee IN ({placeholders})"
        emp_condition_contr = f"tecl.employee IN ({placeholders})"
        emp_condition_with  = f"tsfp.employee IN ({placeholders})"
        emp_condition_res   = f"ter.employee IN ({placeholders})"
        emp_condition_main  = f"e.name IN ({placeholders})"
        emp_params = tuple(selected_employees)
    else:
        emp_condition_pl    = "tial.employee = %s"
        emp_condition_contr = "tecl.employee = %s"
        emp_condition_with  = "tsfp.employee = %s"
        emp_condition_res   = "ter.employee = %s"
        emp_condition_main  = "e.name = %s"
        emp_params = (selected_employees[0],)

    query = f"""
        WITH pl AS (
            SELECT
                tial.employee,
                tial.employee_name,
                SUM(tial.pl_employee_contr) AS total_employee_pl,
                SUM(tial.pl_bank_contr)     AS total_bank_pl,
                SUM(tial.pl_employee_contr) + SUM(tial.pl_bank_contr) AS total_pl
            FROM `tabIncome Allocation Line` tial
            INNER JOIN `tabIncome Allocation` tia ON tial.parent = tia.name
            INNER JOIN `tabEmployee` te ON tial.employee = te.name
            WHERE tia.posting_date > te.date_of_joining
              AND {emp_condition_pl}
              AND MONTH(tia.posting_date) + ((YEAR(tia.posting_date) - 1) * 12) <= %s
              AND tia.docstatus = 1
            GROUP BY tial.employee, tial.employee_name
        ),
        contr AS (
            SELECT
                tecl.employee,
                tecl.employee_name,
                SUM(tecl.employee_contr) AS total_employee_contr,
                SUM(tecl.bank_contr)     AS total_bank_contr,
                SUM(tecl.employee_contr) + SUM(tecl.bank_contr) AS total_contr
            FROM `tabEmployee Contribution Line` tecl
            INNER JOIN `tabEmployee Contribution` tec ON tecl.parent = tec.name
            INNER JOIN `tabEmployee` te ON tecl.employee = te.name
            WHERE tec.posting_date > te.date_of_joining
              AND {emp_condition_contr}
              AND MONTH(tec.posting_date) + ((YEAR(tec.posting_date) - 1) * 12) <= %s
              AND tec.docstatus = 1
            GROUP BY tecl.employee, tecl.employee_name
        ),
        withdraw AS (
            SELECT
                tsfp.employee,
                tsfp.employee_name,
                SUM(tsfp.paid_amount) AS total_paid_amount
            FROM `tabSaving Fund Payment` tsfp
            INNER JOIN `tabEmployee` te ON tsfp.employee = te.name
            WHERE tsfp.posting_date > te.date_of_joining
              AND {emp_condition_with}
              AND MONTH(tsfp.posting_date) + ((YEAR(tsfp.posting_date) - 1) * 12) <= %s
              AND tsfp.docstatus = 1
            GROUP BY tsfp.employee, tsfp.employee_name
        ),
        liability AS (
            SELECT
                ter.employee,
                ter.employee_name,
                ter.employee_equity_amount + ter.bank_equity_amount AS liability_amount
            FROM `tabEmployee Resignation` ter
            INNER JOIN `tabEmployee` te ON ter.employee = te.name
            WHERE ter.posting_date > te.date_of_joining
              AND {emp_condition_res}
              AND MONTH(ter.posting_date) + ((YEAR(ter.posting_date) - 1) * 12) <= %s
              AND ter.docstatus = 1
              AND ter.resignation_date = (
                  SELECT MAX(ter2.resignation_date)
                  FROM `tabEmployee Resignation` ter2
                  WHERE ter2.employee = ter.employee
                    AND ter2.docstatus = 1
              )
            GROUP BY ter.employee, ter.employee_name
        )
        SELECT
            e.name AS employee,
            e.employee_name,
            IFNULL(c.total_employee_contr, 0) AS total_employee_contr,
            IFNULL(c.total_bank_contr, 0)     AS total_bank_contr,
            IFNULL(c.total_contr, 0)          AS total_contr,
            IFNULL(p.total_employee_pl, 0)    AS total_employee_pl,
            IFNULL(p.total_bank_pl, 0)        AS total_bank_pl,
            IFNULL(p.total_pl, 0)             AS total_pl,
            IFNULL(w.total_paid_amount, 0)    AS total_paid_amount,
            IFNULL(l.liability_amount, 0)     AS liability_amount,
            (IFNULL(c.total_contr, 0) + IFNULL(p.total_pl, 0) - IFNULL(w.total_paid_amount, 0)) AS total_right,
            CASE
                WHEN DATEDIFF(%s, e.date_of_joining) / 365 >= 3
                    THEN IFNULL(c.total_contr, 0) + IFNULL(p.total_pl, 0) - IFNULL(w.total_paid_amount, 0)
                WHEN DATEDIFF(%s, e.date_of_joining) / 365 >= 1
                    THEN IFNULL(c.total_employee_contr, 0) + IFNULL(p.total_employee_pl, 0) - IFNULL(w.total_paid_amount, 0)
                ELSE
                    IFNULL(c.total_employee_contr, 0) - IFNULL(w.total_paid_amount, 0)
            END AS deserved_amount
        FROM tabEmployee AS e
        LEFT JOIN contr    c ON e.name = c.employee
        LEFT JOIN pl       p ON e.name = p.employee
        LEFT JOIN withdraw w ON e.name = w.employee
        LEFT JOIN liability l ON e.name = l.employee
        WHERE {emp_condition_main}
    """

    # params: emp_params x4 CTEs (each with up_to) + date_to x2 (DATEDIFF) + emp_params (WHERE)
    params = (
        emp_params + (up_to,)    # pl
        + emp_params + (up_to,)  # contr
        + emp_params + (up_to,)  # withdraw
        + emp_params + (up_to,)  # liability
        + (date_to, date_to)     # DATEDIFF x2
        + emp_params             # WHERE
    )

    return frappe.db.sql(query, params, as_dict=True)


@frappe.whitelist()
def get_employee_up_to_date_balance(emp, date_to):
    query = """
        WITH
        pl AS (
            SELECT tial.employee, tial.employee_name,
                   SUM(tial.pl_employee_contr)                           AS total_employee_pl,
                   SUM(tial.pl_bank_contr)                               AS total_bank_pl,
                   SUM(tial.pl_employee_contr) + SUM(tial.pl_bank_contr) AS total_pl
            FROM `tabIncome Allocation Line` tial
            INNER JOIN `tabIncome Allocation` tia ON tial.parent = tia.name
            INNER JOIN `tabEmployee` em ON tial.employee = em.name
            WHERE tia.posting_date <= %(date_to)s
              AND tia.posting_date > em.date_of_joining
              AND tia.docstatus = 1
            GROUP BY tial.employee, tial.employee_name
        ),
        contr AS (
            SELECT tecl.employee, tecl.employee_name,
                   SUM(tecl.employee_contr)                            AS total_employee_contr,
                   SUM(tecl.bank_contr)                                AS total_bank_contr,
                   SUM(tecl.employee_contr) + SUM(tecl.bank_contr)    AS total_contr
            FROM `tabEmployee Contribution Line` tecl
            INNER JOIN `tabEmployee Contribution` tec ON tecl.parent = tec.name
            INNER JOIN `tabEmployee` em ON tecl.employee = em.name
            WHERE tec.posting_date <= %(date_to)s
              AND tec.posting_date > em.date_of_joining
              AND tec.docstatus = 1
            GROUP BY tecl.employee, tecl.employee_name
        ),
        withdraw AS (
            SELECT tsfp.employee, tsfp.employee_name,
                   SUM(tsfp.paid_amount) AS total_paid_amount
            FROM `tabSaving Fund Payment` tsfp
            INNER JOIN `tabEmployee` em ON tsfp.employee = em.name
            WHERE tsfp.posting_date <= %(date_to)s
              AND tsfp.posting_date > em.date_of_joining
              AND tsfp.docstatus = 1
              AND tsfp.status = 'Active'
            GROUP BY tsfp.employee, tsfp.employee_name
        ),
        liability AS (
            SELECT ter.employee, ter.employee_name,
                   SUM(ter.employee_equity_amount + ter.bank_equity_amount) AS liability_amount
            FROM `tabEmployee Resignation` ter
            INNER JOIN `tabEmployee` em ON ter.employee = em.name
            WHERE ter.posting_date <= %(date_to)s
              AND ter.posting_date > em.date_of_joining
              AND ter.docstatus = 1
              AND ter.resignation_date = (
                  SELECT MAX(ter2.resignation_date)
                  FROM `tabEmployee Resignation` ter2
                  WHERE ter2.employee = ter.employee
                    AND ter2.docstatus = 1
              )
            GROUP BY ter.employee, ter.employee_name
        )
        SELECT
            e.name AS employee,
            e.employee_name,
            IFNULL(c.total_employee_contr, 0) AS total_employee_contr,
            IFNULL(c.total_bank_contr, 0)     AS total_bank_contr,
            IFNULL(c.total_contr, 0)          AS total_contr,
            IFNULL(p.total_employee_pl, 0)    AS total_employee_pl,
            IFNULL(p.total_bank_pl, 0)        AS total_bank_pl,
            IFNULL(p.total_pl, 0)             AS total_pl,
            IFNULL(w.total_paid_amount, 0)    AS total_withdraw,
            IFNULL(l.liability_amount, 0)     AS liability_amount,
            (IFNULL(c.total_contr, 0) + IFNULL(p.total_pl, 0)
             - IFNULL(w.total_paid_amount, 0) - IFNULL(l.liability_amount, 0)) AS total_right
        FROM tabEmployee e
        LEFT JOIN contr    c ON e.name = c.employee
        LEFT JOIN pl       p ON e.name = p.employee
        LEFT JOIN withdraw w ON e.name = w.employee
        LEFT JOIN liability l ON e.name = l.employee
        WHERE e.name = %(emp)s
    """
    return frappe.db.sql(query, {"emp": emp, "date_to": date_to}, as_dict=True)
