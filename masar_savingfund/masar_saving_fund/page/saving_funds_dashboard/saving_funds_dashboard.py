import frappe

@frappe.whitelist()
def get_contr_totals():
    return frappe.db.sql(f"""Select  SUM(tecn.total_employee_contr) AS total_employee_contr, SUM(tecn.total_bank_contr) AS total_bank_contr,
                            SUM(tecn.total_employee_contr + tecn.total_bank_contr) as total_contr,
                            SUM(tial.pl_employee_contr) AS total_employee_contr_pl
								From `tabIncome Allocation Line` tial
								INNER JOIN `tabIncome Allocation` tia on tia.name = tial.parent
								INNER  JOIN (Select tecl.employee, SUM(tecl.employee_contr) AS total_employee_contr, SUM(tecl.bank_contr) AS total_bank_contr,
								(SUM(tecl.employee_contr)+SUM(tecl.bank_contr)) AS total_contr
								FROM `tabEmployee Contribution Line` tecl
								INNER join `tabEmployee Contribution` tec on tecl.parent = tec.name
                                Where tec.docstatus =1) AS tecn on tial.employee = tecn.employee
								Where tia.docstatus =1;""",as_dict=True)

@frappe.whitelist()
def get_pl_totals():
    return frappe.db.sql(f"""Select  SUM(tial.pl_employee_contr) AS total_employee_contr_pl, SUM(tial.pl_bank_contr) AS total_bank_contr_pl,
                                SUM(tial.pl_employee_contr + tial.pl_bank_contr) AS total_contr_pl
    								From `tabIncome Allocation Line` tial
    								INNER JOIN `tabIncome Allocation` tia on tia.name = tial.parent
    								Where tia.docstatus =1;""",as_dict=True)


@frappe.whitelist()
def get_chart():
    return frappe.db.sql(f"""select employee_name, employee_contr, bank_contr
from `tabIncome Allocation Line` tial
group by employee_name """,as_dict=True)
