# Copyright (c) 2024, Karama kcsc and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    return get_columns(), get_data(filters)

def get_data(filters):
    _from, to = filters.get('_from'), filters.get('to')

    conditions = ' 1=1 '
    if filters.get('employee'):
        conditions = f" AND ter.employee = '{filters.get('employee')}' "
    if filters.get('employee_name'):
        conditions = f" AND ter.employee_name LIKE '%{filters.get('employee_name')}%' "
    if _from and to:
        conditions += f" AND ter.posting_date BETWEEN '{_from}' AND '{to}'"
    if to and _from and to < _from:
        frappe.msgprint('Error: To Posting Date is Less than From Posting Date')

    query = frappe.db.sql(f"""                          
    SELECT 
        ter.name AS employee_resignation, ter.employee, ter.employee_name, ter.date_of_joining, ter.posting_date, ter.total_right, 
        ter.withdraw_amount, ter.income_amount AS income_amount
    FROM `tabEmployee Resignation` ter
    WHERE {conditions} AND DATEDIFF(ter.resignation_date, ter.date_of_joining) <= 1095 AND ter.status_on_submit = 'Left'
    GROUP BY ter.employee
    """, as_dict=True)

    return query
def get_columns():
    return [
        "Employee Resignation: Data:250",
        "Employee: Link/Employee:250",
        "Employee Name: Data:250",
        "Date Of Joining: Data:250",
        "Posting Date: Data:250",
        "Total Right: Float:200",
        "Withdraw Amount: Float:200",
        "Income Amount: Curency:300",
    ]