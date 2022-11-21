from __future__ import unicode_literals
import frappe, erpnext, json,datetime
from frappe import _, scrub, ValidationError
from frappe.utils import flt, comma_or, nowdate, getdate
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from frappe.model.document import Document


@frappe.whitelist()
def get_employee_savefund_balance(selected_employees,date_to):
    selected_employees = json.loads(selected_employees)
    employees_tuple = tuple(selected_employees)
    emp = employees_tuple[0]
    trans_date = datetime.datetime.strptime(date_to, '%Y-%m-%d')
    month_to = trans_date.month
    year_to = trans_date.year
    up_to = month_to + ((year_to - 1) * 12)
    date_prev = frappe.utils.add_months(date_to, -1)
    if len(selected_employees) != 1:

        return frappe.db.sql(f"""
            With pl
            as (Select tial.employee,tial.employee_name ,SUM(tial.pl_employee_contr) as total_employee_pl,SUM(tial.pl_bank_contr) as total_bank_pl,
            	   SUM(tial.pl_employee_contr) + SUM(tial.pl_bank_contr) as total_pl
            From `tabIncome Allocation Line` tial
            Inner Join `tabIncome Allocation` tia on tial.parent =tia.name
            Where tial.employee  in {employees_tuple} and month(tia.date) + ((year(tia.date) - 1) * 12) < {up_to}
                  and tia.docstatus = 1
            Group By tial.employee,tial.employee_name),

            contr as (Select tecl.employee,tecl.employee_name ,SUM(tecl.employee_contr) total_employee_contr,SUM(tecl.bank_contr) total_bank_contr,
            (SUM(tecl.employee_contr)+SUM(tecl.bank_contr)) total_contr
            From `tabEmployee Contribution Line` tecl
            Inner Join `tabEmployee Contribution` tec on tecl.parent =tec.name
            Where tecl.employee  in {employees_tuple} and month(tec.date_transaction) + ((year(tec.date_transaction) - 1) * 12) <= {up_to}
                  and tec.docstatus = 1
            Group By tecl.employee,tecl.employee_name
            )

            Select c.employee,c.employee_name,total_employee_contr,total_bank_contr,total_contr,
            	   IFNULL(p.total_employee_pl,0)as total_employee_pl ,IFNULL(total_bank_pl,0) total_bank_pl,IFNULL(total_pl,0) total_pl,
            	   (IFNULL(total_contr,0) + IFNULL(total_pl,0) ) as total_right
            from contr as c
            Left Join pl as p on c.employee = p.employee""",as_dict=True)
    else:

        return frappe.db.sql(f"""
            With pl
            as (Select tial.employee,tial.employee_name ,SUM(tial.pl_employee_contr) as total_employee_pl,SUM(tial.pl_bank_contr) as total_bank_pl,
            	   SUM(tial.pl_employee_contr) + SUM(tial.pl_bank_contr) as total_pl
            From `tabIncome Allocation Line` tial
            Inner Join `tabIncome Allocation` tia on tial.parent =tia.name
            Where tial.employee  = '{emp}' and month(tia.date) + ((year(tia.date) - 1) * 12) < {up_to}
                  and tia.docstatus = 1
            Group By tial.employee,tial.employee_name),

            contr as (Select tecl.employee,tecl.employee_name ,SUM(tecl.employee_contr) total_employee_contr,SUM(tecl.bank_contr) total_bank_contr,
            (SUM(tecl.employee_contr)+SUM(tecl.bank_contr)) total_contr
            From `tabEmployee Contribution Line` tecl
            Inner Join `tabEmployee Contribution` tec on tecl.parent =tec.name
            Where tecl.employee  = '{emp}' and month(tec.date_transaction) + ((year(tec.date_transaction) - 1) * 12) <= {up_to}
                  and tec.docstatus = 1
            Group By tecl.employee,tecl.employee_name
            )

            Select c.employee,c.employee_name,total_employee_contr,total_bank_contr,total_contr,
            	   IFNULL(p.total_employee_pl,0)as total_employee_pl ,IFNULL(total_bank_pl,0) total_bank_pl,IFNULL(total_pl,0) total_pl,
            	   (IFNULL(total_contr,0) + IFNULL(total_pl,0) ) as total_right
            from contr as c
            Left Join pl as p on c.employee = p.employee""",as_dict=True)
