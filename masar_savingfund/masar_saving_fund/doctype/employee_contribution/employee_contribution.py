# Copyright (c) 2022, Karama kcsc and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from dateutil.relativedelta import relativedelta
import frappe, erpnext, json, datetime
from frappe import _, scrub, ValidationError
from erpnext.setup.utils import get_exchange_rate
from erpnext.controllers.accounts_controller import AccountsController
from frappe.model.document import Document
from frappe.query_builder.functions import Coalesce, Count
from erpnext.accounts.general_ledger import make_gl_entries, process_gl_map, make_reverse_gl_entries
from frappe.utils import (
    DATE_FORMAT, add_days, nowdate, add_to_date, cint, comma_and,
    date_diff, flt, get_link_to_form, getdate,
)


@frappe.whitelist()
def get_exist_employee_in_month(selected_employees, date_to):
    selected_employees = json.loads(selected_employees)
    trans_date = datetime.datetime.strptime(date_to, '%Y-%m-%d')
    up_to = trans_date.month + ((trans_date.year - 1) * 12) - 1

    if len(selected_employees) > 1:
        placeholders = ', '.join(['%s'] * len(selected_employees))
        return frappe.db.sql(f"""
            SELECT tecl.employee, tecl.employee_name
            FROM `tabEmployee Contribution Line` tecl
            INNER JOIN `tabEmployee Contribution` tec ON tecl.parent = tec.name
            WHERE tecl.employee IN ({placeholders})
              AND (MONTH(tec.posting_date) + ((YEAR(tec.posting_date) - 1) * 12) - 1) = %s
              AND tec.docstatus = 1
        """, tuple(selected_employees) + (up_to,), as_dict=True)
    else:
        return frappe.db.sql("""
            SELECT tecl.employee, tecl.employee_name
            FROM `tabEmployee Contribution Line` tecl
            INNER JOIN `tabEmployee Contribution` tec ON tecl.parent = tec.name
            WHERE tecl.employee = %s
              AND (MONTH(tec.posting_date) + ((YEAR(tec.posting_date) - 1) * 12) - 1) = %s
              AND tec.docstatus = 1
        """, (selected_employees[0], up_to), as_dict=True)


@frappe.whitelist()
def get_employee_contr_perc():
    return frappe.db.get_single_value('Saving Fund Settings', 'employee_contr_per') or 0

@frappe.whitelist()
def get_bank_contr_perc():
    return frappe.db.get_single_value('Saving Fund Settings', 'bank_contr_per') or 0

@frappe.whitelist()
def get_cash_account():
    return frappe.db.get_single_value('Saving Fund Settings', 'cash_account')

@frappe.whitelist()
def get_employee_equity_account():
    return frappe.db.get_single_value('Saving Fund Settings', 'employee_equity')

@frappe.whitelist()
def get_bank_equity_account():
    return frappe.db.get_single_value('Saving Fund Settings', 'bank_equity')

@frappe.whitelist()
def get_liability_account():
    return frappe.db.get_single_value('Saving Fund Settings', 'liability_account')

@frappe.whitelist()
def get_income_account():
    return frappe.db.get_single_value('Saving Fund Settings', 'income_account')

@frappe.whitelist()
def get_retained_earning():
    return frappe.db.get_single_value('Saving Fund Settings', 'retained_earning')

@frappe.whitelist()
def get_withdrawal():
    return frappe.db.get_single_value('Saving Fund Settings', 'withdrawal')

# Alias used by client scripts
get_emp_contr_perc = get_employee_contr_perc


class InvalidEmployeeContribution(ValidationError):
    pass


class EmployeeContribution(AccountsController):
    def __init__(self, *args, **kwargs):
        super(EmployeeContribution, self).__init__(*args, **kwargs)

    def validate(self):
        pass

    def on_submit(self):
        self.make_gl()

    def on_cancel(self):
        self.delete_linked_gl_entries()

    def make_gl(self):
        gl_entries = []
        for d in self.get("employee_contr_lines"):
            emp_contr = flt(d.employee_contr) + flt(d.employee_contr_diff)
            bank_contr = flt(d.bank_contr) + flt(d.bank_contr_diff)
            if emp_contr:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.employee_equity,
                        "against": self.cash_account,
                        "credit_in_account_currency": emp_contr,
                        "credit": emp_contr,
                        "employee": d.employee,
                        "remarks": d.employee + ' : ' + d.employee_name,
                    }))
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.cash_account,
                        "against": self.employee_equity,
                        "debit_in_account_currency": emp_contr,
                        "debit": emp_contr,
                        "employee": d.employee,
                        "remarks": d.employee + ' : ' + d.employee_name,
                    }))
            if bank_contr:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.bank_equity,
                        "against": self.cash_account,
                        "credit_in_account_currency": bank_contr,
                        "credit": bank_contr,
                        "employee": d.employee,
                        "remarks": d.employee + ' : ' + d.employee_name,
                    }))
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.cash_account,
                        "against": self.bank_equity,
                        "debit_in_account_currency": bank_contr,
                        "debit": bank_contr,
                        "employee": d.employee,
                        "remarks": d.employee + ' : ' + d.employee_name,
                    }))
        if gl_entries:
            make_gl_entries(gl_entries, cancel=0, adv_adj=0)

    def delete_linked_gl_entries(self):
        frappe.db.sql("""DELETE FROM `tabGL Entry`
            WHERE voucher_type = 'Employee Contribution' AND voucher_no = %s""",
            self.name)
