# Copyright (c) 2022, Karama kcsc and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext, json, datetime
from frappe import _, scrub, ValidationError
from frappe.utils import flt, comma_or, nowdate, getdate
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from frappe.model.document import Document


@frappe.whitelist()
def get_exist_income_allocation_in_month(selected_employees, date_to):
    selected_employees = json.loads(selected_employees)
    trans_date = datetime.datetime.strptime(date_to, '%Y-%m-%d')
    up_to = trans_date.month + ((trans_date.year - 1) * 12)

    if len(selected_employees) > 1:
        placeholders = ', '.join(['%s'] * len(selected_employees))
        return frappe.db.sql(f"""
            SELECT tial.employee, tial.employee_name
            FROM `tabIncome Allocation Line` tial
            INNER JOIN `tabIncome Allocation` tia ON tial.parent = tia.name
            WHERE tial.employee IN ({placeholders})
              AND MONTH(tia.posting_date) + ((YEAR(tia.posting_date) - 1) * 12) = %s
              AND tia.docstatus = 1
        """, tuple(selected_employees) + (up_to,), as_dict=True)
    else:
        return frappe.db.sql("""
            SELECT tial.employee, tial.employee_name
            FROM `tabIncome Allocation Line` tial
            INNER JOIN `tabIncome Allocation` tia ON tial.parent = tia.name
            WHERE tial.employee = %s
              AND MONTH(tia.posting_date) + ((YEAR(tia.posting_date) - 1) * 12) = %s
              AND tia.docstatus = 1
        """, (selected_employees[0], up_to), as_dict=True)


@frappe.whitelist()
def get_interim_revenue_account():
    return frappe.db.get_single_value('Saving Fund Settings', 'interim_revenue')

@frappe.whitelist()
def get_current_year_profit_account():
    return frappe.db.get_single_value('Saving Fund Settings', 'current_year_profit')


class InvalidIncomeAllocation(ValidationError):
    pass


class IncomeAllocation(AccountsController):
    def __init__(self, *args, **kwargs):
        super(IncomeAllocation, self).__init__(*args, **kwargs)

    def validate(self):
        pass

    def on_submit(self):
        self.make_gl()

    def on_cancel(self):
        self.delete_linked_gl_entries()

    def make_gl(self):
        gl_entries = []
        for d in self.get("employees"):
            pl_emp = flt(d.pl_employee_contr) + flt(d.pl_employee_contr_diff)
            pl_bank = flt(d.pl_bank_contr) + flt(d.pl_bank_contr_diff)
            if pl_emp:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.current_year_profit,
                        "against": self.interim_revenue,
                        "credit_in_account_currency": pl_emp,
                        "credit": pl_emp,
                        "employee": d.employee,
                        "remarks": d.employee + ' : ' + d.employee_name,
                        "cost_center": self.cost_center,
                    }))
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.interim_revenue,
                        "against": self.current_year_profit,
                        "debit_in_account_currency": pl_emp,
                        "debit": pl_emp,
                        "employee": d.employee,
                        "remarks": d.employee + ' : ' + d.employee_name,
                        "cost_center": self.cost_center,
                    }))
            if pl_bank:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.current_year_profit,
                        "against": self.interim_revenue,
                        "credit_in_account_currency": pl_bank,
                        "credit": pl_bank,
                        "employee": d.employee,
                        "remarks": d.employee + ' : ' + d.employee_name,
                        "cost_center": self.cost_center,
                    }))
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.interim_revenue,
                        "against": self.current_year_profit,
                        "debit_in_account_currency": pl_bank,
                        "debit": pl_bank,
                        "employee": d.employee,
                        "remarks": d.employee + ' : ' + d.employee_name,
                        "cost_center": self.cost_center,
                    }))
        if gl_entries:
            make_gl_entries(gl_entries, cancel=0, adv_adj=0)

    @frappe.whitelist()
    def fill_employee_details(self):
        """
        يشمل الموظفين المستقيلين في نفس شهر الترحيل
        حتى لو تغيّرت حالتهم إلى 'Left' قبل تسجيل Income Allocation
        """
        posting_date = self.posting_date or nowdate()
        posting_month = getdate(posting_date).month
        posting_year = getdate(posting_date).year

        cond = "1=1"
        params = []

        if self.status and self.status != 'All':
            if self.status == 'Active':
                # شمل الموظفين المستقيلين في نفس شهر الترحيل
                cond += """
                    AND (
                        te.status = 'Active'
                        OR (
                            te.status = 'Left'
                            AND MONTH(te.relieving_date) = %s
                            AND YEAR(te.relieving_date) = %s
                        )
                    )
                """
                params += [posting_month, posting_year]
            else:
                cond += " AND te.status = %s"
                params.append(self.status)

        results = frappe.db.sql(f"""
            SELECT
                te.name AS employee,
                te.employee_name,
                te.status,
                IFNULL(te.relieving_date, '') AS relieving_date
            FROM tabEmployee te
            WHERE {cond}
            ORDER BY te.employee_name
        """, tuple(params) if params else (), as_dict=True)

        self.set("employees", [])
        fill_emp = []
        for result in results:
            fill_emp.append({
                "employee": result.get('employee'),
                "employee_name": result.get('employee_name'),
                "status": result.get('status'),
                "resignation_date": result.get('relieving_date'),
            })
        self.set("employees", fill_emp)
        self.number_of_employees = len(results)
        return 'ok'

    def delete_linked_gl_entries(self):
        frappe.db.sql("""DELETE FROM `tabGL Entry`
            WHERE voucher_type = 'Income Allocation' AND voucher_no = %s""",
            self.name)
