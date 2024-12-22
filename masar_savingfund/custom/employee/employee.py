from __future__ import unicode_literals
import frappe, erpnext, json,datetime
from frappe import _, scrub, ValidationError
from frappe.utils import flt, comma_or, nowdate, getdate
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from frappe.model.document import Document
from frappe.model.naming import set_name_by_naming_series


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
            Where tial.employee  in {employees_tuple} and month(tia.posting_date) + ((year(tia.posting_date) - 1) * 12) < '{up_to}' and tia.docstatus = 1
            Group By tial.employee,tial.employee_name),

            contr as (Select tecl.employee,tecl.employee_name ,SUM(tecl.employee_contr) total_employee_contr,SUM(tecl.bank_contr) total_bank_contr,
            (SUM(tecl.employee_contr)+SUM(tecl.bank_contr)) total_contr
            From `tabEmployee Contribution Line` tecl
            Inner Join `tabEmployee Contribution` tec on tecl.parent =tec.name
            Where tecl.employee  in {employees_tuple} and month(tec.posting_date) + ((year(tec.posting_date) - 1) * 12) <= '{up_to}'
                  and tec.docstatus = 1
            Group By tecl.employee,tecl.employee_name
            ),
            withdraw as (Select tsfp.employee,tsfp.employee_name ,SUM(tsfp.paid_amount) total_paid_amount
            From `tabSaving Fund Payment` tsfp
            Where tsfp.employee in {employees_tuple} and month(tsfp.posting_date) + ((year(tsfp.posting_date) - 1) * 12) <= '{up_to}'
                  and tsfp.docstatus = 1
            Group By tsfp.employee,tsfp.employee_name
            ),

            liabilty as (Select ter.employee,ter.employee_name ,ter.employee_equity_amount + ter.bank_equity_amount as liability_amount
            From `tabEmployee Resignation` ter 
            Where ter.employee in {employees_tuple} and month(ter.posting_date) + ((year(ter.posting_date) - 1) * 12) <= '{up_to}'
                AND ter.docstatus = 1
                AND ter.resignation_date = (
                    SELECT MAX(ter.resignation_date))                 
                Group By ter.employee,ter.employee_name
                order by ter.resignation_date )         

            Select c.employee,c.employee_name,IFNULL(total_employee_contr,0) as total_employee_contr,IFNULL(total_bank_contr,0) as total_bank_contr,IFNULL(total_contr,0) as total_contr,
            	   IFNULL(p.total_employee_pl,0)as total_employee_pl ,IFNULL(total_bank_pl,0) total_bank_pl,IFNULL(total_pl,0) total_pl,
                   IFNULL(total_paid_amount,0) as total_paid_amount,
                   IFNULL(liability_amount,0) as liability_amount,                   
            	   (IFNULL(total_contr,0) + IFNULL(total_pl,0) - IFNULL(total_paid_amount,0)) as total_right,
            	   (CASE WHEN DATEDIFF('{date_to}', e.date_of_joining)/365 >=3 Then  IFNULL(total_contr,0) + IFNULL(total_pl,0) - IFNULL(total_paid_amount,0)
            	   		 WHEN DATEDIFF('{date_to}', e.date_of_joining)/365 >= 1 And DATEDIFF('{date_to}', e.date_of_joining)/365 < 3  Then total_employee_contr + IFNULL(p.total_employee_pl,0) - IFNULL(total_paid_amount,0) 
            	   		 ELSE total_employee_contr - IFNULL(total_paid_amount,0)  END ) as deserved_amount
            from tabEmployee as e
            left Join contr c on e.employee = c.employee
            Left Join pl as p on c.employee = p.employee
            Left Join withdraw as w on c.employee = w.employee
            Left Join liabilty as l on c.employee = l.employee""",as_dict=True)

    else:

        return frappe.db.sql(f"""
        With pl
            as (Select tial.employee,tial.employee_name ,SUM(tial.pl_employee_contr) as total_employee_pl,SUM(tial.pl_bank_contr) as total_bank_pl,
            	   SUM(tial.pl_employee_contr) + SUM(tial.pl_bank_contr) as total_pl
            From `tabIncome Allocation Line` tial
            Inner Join `tabIncome Allocation` tia on tial.parent =tia.name
            Where tial.employee  = '{emp}' and month(tia.posting_date) + ((year(tia.posting_date) - 1) * 12) < '{up_to}' and tia.docstatus = 1
            Group By tial.employee,tial.employee_name),

            contr as (Select tecl.employee,tecl.employee_name ,SUM(tecl.employee_contr) total_employee_contr,SUM(tecl.bank_contr) total_bank_contr,
            (SUM(tecl.employee_contr)+SUM(tecl.bank_contr)) total_contr
            From `tabEmployee Contribution Line` tecl
            Inner Join `tabEmployee Contribution` tec on tecl.parent =tec.name
            Where tecl.employee  = '{emp}' and month(tec.posting_date) + ((year(tec.posting_date) - 1) * 12) <= '{up_to}' and tec.docstatus = 1
            Group By tecl.employee,tecl.employee_name
            ),
            withdraw as (Select tsfp.employee,tsfp.employee_name ,SUM(tsfp.paid_amount) total_paid_amount
            From `tabSaving Fund Payment` tsfp
            Where tsfp.employee = '{emp}' and month(tsfp.posting_date) + ((year(tsfp.posting_date) - 1) * 12) <= '{up_to}' and tsfp.docstatus = 1
            Group By tsfp.employee,tsfp.employee_name
            ),
            liabilty as (Select ter.employee,ter.employee_name ,ter.employee_equity_amount + ter.bank_equity_amount as liability_amount
            From `tabEmployee Resignation` ter 
            Where ter.employee = '{emp}' and month(ter.posting_date) + ((year(ter.posting_date) - 1) * 12) <= '{up_to}' and ter.docstatus = 1
                AND ter.docstatus = 1
                AND ter.resignation_date = (
                    SELECT MAX(ter.resignation_date))                 
                Group By ter.employee,ter.employee_name
                order by ter.resignation_date )                     


            Select e.employee,e.employee_name,IFNULL(total_employee_contr,0) as total_employee_contr,IFNULL(total_bank_contr,0) as total_bank_contr,IFNULL(total_contr,0) as total_contr,
            	   IFNULL(p.total_employee_pl,0)as total_employee_pl ,IFNULL(total_bank_pl,0) total_bank_pl,IFNULL(total_pl,0) total_pl,
                   IFNULL(total_paid_amount,0) as total_paid_amount,
                   IFNULL(liability_amount,0) as liability_amount,
            	   (IFNULL(total_contr,0) + IFNULL(total_pl,0) - IFNULL(total_paid_amount,0)) as total_right,
            	   (CASE WHEN DATEDIFF('{date_to}', e.date_of_joining)/365 >=3 Then  IFNULL(total_contr,0) + IFNULL(total_pl,0) - IFNULL(total_paid_amount,0)
            	   		 WHEN DATEDIFF('{date_to}', e.date_of_joining)/365 >= 1 And DATEDIFF('{date_to}', e.date_of_joining)/365 < 3  Then total_employee_contr + IFNULL(p.total_employee_pl,0) - IFNULL(total_paid_amount,0)
            	   		 ELSE total_employee_contr - IFNULL(total_paid_amount,0) END ) as deserved_amount
            from tabEmployee as e
            left Join contr c on e.employee = c.employee
            Left Join pl as p on c.employee = p.employee
            Left Join withdraw as w on c.employee = w.employee
            Left Join liabilty as l on c.employee = l.employee            
            Where e.name = '{emp}' """,as_dict=True)
