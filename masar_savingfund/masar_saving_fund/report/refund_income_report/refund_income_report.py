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
        conditions += f" AND ter.date_of_joining BETWEEN '{_from}' AND '{to}'"
    if to and _from and to < _from:
        frappe.msgprint('Error: To Joining Date is Less than From Joining Date')

    date = frappe.utils.add_years(frappe.utils.today(), -3)                
    query = frappe.db.sql(f"""
    SELECT te.employee, te.employee_name, ter.date_of_joining, te.status, ter.total_right, ter.withdraw_amount,
           SUM(ter.total_right - ter.withdraw_amount) AS refund_income
    FROM `tabEmployee Resignation` ter
    INNER JOIN `tabEmployee` te ON te.employee = ter.employee                      
    WHERE  ter.date_of_joining >= '{date}' AND te.status = 'Left' {conditions}
    GROUP BY employee
    """, as_dict=True)

    return query

def get_columns():
    return [
        "Employee: Link/Employee:250",
        "Employee Name: Data:250",
        "Refund Income: Curency:300",
        "Date Of Joining: Data:250"
    ]