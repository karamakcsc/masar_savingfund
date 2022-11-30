import frappe

@frappe.whitelist()
def get_saving_funds():
    return frappe.db.sql(f"""
    With pl
    as (Select tial.employee,tial.employee_name ,SUM(tial.pl_employee_contr) as total_employee_pl,SUM(tial.pl_bank_contr) as total_bank_pl,
           SUM(tial.pl_employee_contr) + SUM(tial.pl_bank_contr) as total_pl
    From `tabIncome Allocation Line` tial
    Inner Join `tabIncome Allocation` tia on tial.parent =tia.name
    Group By tial.employee,tial.employee_name),

    contr as (Select tecl.employee,tecl.employee_name ,SUM(tecl.employee_contr) total_employee_contr,SUM(tecl.bank_contr) total_bank_contr,
    (SUM(tecl.employee_contr)+SUM(tecl.bank_contr)) total_contr
    From `tabEmployee Contribution Line` tecl
    Inner Join `tabEmployee Contribution` tec on tecl.parent =tec.name
    Where tec.docstatus = 1
    Group By tecl.employee,tecl.employee_name
    )

    Select c.employee,c.employee_name,total_employee_contr,total_bank_contr,total_contr,
           IFNULL(p.total_employee_pl,0)as total_employee_pl ,IFNULL(total_bank_pl,0) total_bank_pl,IFNULL(total_pl,0) total_pl,
           (IFNULL(total_contr,0) + IFNULL(total_pl,0) ) as total_right
    from contr as c
    Inner Join tabEmployee e on c.employee = e.employee
    Left Join pl as p on c.employee = p.employee;""",as_dict=True)
