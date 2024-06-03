# Copyright (c) 2024, Karama kcsc and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    return get_columns(), get_data(filters)

def get_data(filters):
    _from, to = filters.get('_from'), filters.get('to')

    conditions = ''
    if filters.get('employee'):
        conditions = f" AND employee LIKE '%{filters.get('employee')}%' "
    if filters.get('employee_name'):
        conditions = f" AND employee_name LIKE '%{filters.get('employee_name')}%' "
    if _from and to:
        conditions += f" AND date_of_joining BETWEEN '{_from}' AND '{to}'"
    if to and _from and to < _from:
        frappe.msgprint('Error: To Joining Date is Less than From Joining Date')            


    query = frappe.db.sql(f"""
    SELECT employee, employee_name, date_of_joining, total_right, withdraw_amount,
           SUM(total_right - withdraw_amount) AS refund_income
    FROM `tabEmployee Resignation`
    WHERE DATEDIFF(CURDATE(), date_of_joining) < 1095 {conditions}
    GROUP BY employee
    """, as_dict=True)

    return query

def get_columns():
    return [
        "Employee: Data:150",
        "Employee Name: Data:250",
        "Refund Income: Curency:300",
        "Date Of Joining: Data:250"
    ]