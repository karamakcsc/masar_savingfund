# Copyright (c) 2024, Karama kcsc and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    return get_columns(), get_data(filters)

def get_data(filters):
    _from, to = filters.get('_from'), filters.get('to')

    conditions = ''
    if filters.get('employee'):
        conditions = f" AND te.employee LIKE '%{filters.get('employee')}%' "
    if filters.get('employee_name'):
        conditions = f" AND te.employee_name LIKE '%{filters.get('employee_name')}%' "
    if _from and to:
        conditions += f" AND ter.posting_date BETWEEN '{_from}' AND '{to}'"
    if to and _from and to < _from:
        frappe.msgprint('Error: To Posting Date is Less than From Posting Date')

    query = frappe.db.sql(f"""                          
    SELECT te.employee, te.employee_name, ter.date_of_joining, ter.posting_date, te.status, ter.total_right, ter.withdraw_amount,
           CASE
               WHEN DATEDIFF(ter.resignation_date, ter.date_of_joining) < 365 
                          THEN ter.total_right - (ter.employee_contr + ter.pl_bank_contr + ter.pl_employee_contr - withdraw_amount)
               WHEN DATEDIFF(ter.resignation_date, ter.date_of_joining) >= 365 AND DATEDIFF(ter.resignation_date, ter.date_of_joining) < 1095 
                          THEN ter.total_right - (ter.employee_contr + ter.pl_bank_contr - withdraw_amount)
           END AS refund_income
    FROM `tabEmployee Resignation` ter
    INNER JOIN `tabEmployee` te ON te.employee = ter.employee                      
    WHERE DATEDIFF(ter.resignation_date, ter.date_of_joining) <= 1095 AND te.status = 'Left' {conditions}
    GROUP BY employee
    """, as_dict=True)

    return query
def get_columns():
    return [
        "Employee: Link/Employee:250",
        "Employee Name: Data:250",
        "Refund Income: Curency:300",
        "Date Of Joining: Data:250",
        "Posting Date: Data:250"
    ]