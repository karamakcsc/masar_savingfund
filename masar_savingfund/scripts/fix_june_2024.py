"""
سكريبت إصلاح بيانات يونيو 2024
الهدف: إعادة حساب وتصحيح سجلات الاستقالة للموظفين المستقيلين في يونيو 2024
الذين قد يكون حُسب لهم رصيد ناقص بسبب عدم اكتمال الاشتراكات/الأرباح وقتها

التشغيل:
    bench --site [site-name] execute masar_savingfund.scripts.fix_june_2024.run
    أو:
    bench --site [site-name] console
    >>> from masar_savingfund.scripts.fix_june_2024 import run; run()
"""

import frappe
import json
from frappe.utils import flt

TARGET_MONTH_FROM = '2024-06-01'
TARGET_MONTH_TO   = '2024-06-30'
DRY_RUN = True  # غيّر إلى False لتنفيذ الإصلاح الفعلي


def run():
    print("=" * 70)
    print(f"سكريبت إصلاح يونيو 2024 — {'محاكاة (DRY RUN)' if DRY_RUN else 'تنفيذ فعلي'}")
    print("=" * 70)

    step1_diagnose()
    step2_check_contributions()
    step3_check_income_allocations()
    step4_fix_resignations()

    print("\nانتهى السكريبت")
    if DRY_RUN:
        print("لم يُطبَّق أي تغيير — غيّر DRY_RUN = False للتنفيذ الفعلي")


def step1_diagnose():
    print(f"\n{'─'*50}")
    print("الخطوة 1: تشخيص الموظفين المستقيلين في يونيو 2024")
    print(f"{'─'*50}")

    resigned = frappe.db.sql("""
        SELECT name, employee, employee_name,
               resignation_date, posting_date, docstatus,
               employee_contr, bank_contr,
               pl_employee_contr, pl_bank_contr,
               deserved_amount, total_right
        FROM `tabEmployee Resignation`
        WHERE resignation_date BETWEEN %s AND %s
        ORDER BY resignation_date
    """, (TARGET_MONTH_FROM, TARGET_MONTH_TO), as_dict=True)

    if not resigned:
        print("  لا يوجد موظفون مستقيلون في هذه الفترة")
        return

    for r in resigned:
        status = "مُرسَل" if r.docstatus == 1 else ("مسودة" if r.docstatus == 0 else "ملغي")
        print(f"\n  [{status}] {r.name}")
        print(f"    الموظف          : {r.employee} — {r.employee_name}")
        print(f"    تاريخ الاستقالة : {r.resignation_date}")
        print(f"    اشتراك موظف     : {flt(r.employee_contr):,.2f}")
        print(f"    اشتراك بنك      : {flt(r.bank_contr):,.2f}")
        print(f"    أرباح موظف      : {flt(r.pl_employee_contr):,.2f}")
        print(f"    أرباح بنك       : {flt(r.pl_bank_contr):,.2f}")
        print(f"    المستحق         : {flt(r.deserved_amount):,.2f}")
        print(f"    الإجمالي        : {flt(r.total_right):,.2f}")


def step2_check_contributions():
    print(f"\n{'─'*50}")
    print("الخطوة 2: فحص Employee Contribution لشهر يونيو 2024")
    print(f"{'─'*50}")

    contributions = frappe.db.sql("""
        SELECT tec.name, tec.posting_date, tec.docstatus,
               tecl.employee, tecl.employee_name,
               tecl.employee_contr, tecl.bank_contr
        FROM `tabEmployee Contribution Line` tecl
        JOIN `tabEmployee Contribution` tec ON tecl.parent = tec.name
        WHERE MONTH(tec.posting_date) = 6 AND YEAR(tec.posting_date) = 2024
        ORDER BY tec.posting_date, tecl.employee
    """, as_dict=True)

    resigned_employees = frappe.db.sql_list("""
        SELECT employee FROM `tabEmployee Resignation`
        WHERE resignation_date BETWEEN %s AND %s
          AND docstatus IN (0, 1)
    """, (TARGET_MONTH_FROM, TARGET_MONTH_TO))

    contributed_employees = [c.employee for c in contributions]
    missing = [e for e in resigned_employees if e not in contributed_employees]

    if missing:
        print(f"\n  الموظفون المستقيلون الغائبون عن اشتراكات يونيو 2024:")
        for emp in missing:
            name = frappe.db.get_value('Employee', emp, 'employee_name')
            print(f"    - {emp} | {name}")
    else:
        print("\n  جميع الموظفون المستقيلون موجودون في اشتراكات يونيو 2024")

    print(f"\n  إجمالي الاشتراكات لشهر يونيو 2024: {len(contributions)} سطر")


def step3_check_income_allocations():
    print(f"\n{'─'*50}")
    print("الخطوة 3: فحص Income Allocation لشهر يونيو 2024")
    print(f"{'─'*50}")

    allocations = frappe.db.sql("""
        SELECT tia.name, tia.posting_date, tia.docstatus,
               tial.employee, tial.employee_name,
               tial.pl_employee_contr, tial.pl_bank_contr
        FROM `tabIncome Allocation Line` tial
        JOIN `tabIncome Allocation` tia ON tial.parent = tia.name
        WHERE MONTH(tia.posting_date) = 6 AND YEAR(tia.posting_date) = 2024
        ORDER BY tia.posting_date, tial.employee
    """, as_dict=True)

    resigned_employees = frappe.db.sql_list("""
        SELECT employee FROM `tabEmployee Resignation`
        WHERE resignation_date BETWEEN %s AND %s
          AND docstatus IN (0, 1)
    """, (TARGET_MONTH_FROM, TARGET_MONTH_TO))

    allocated_employees = [a.employee for a in allocations]
    missing = [e for e in resigned_employees if e not in allocated_employees]

    if missing:
        print(f"\n  الموظفون المستقيلون الغائبون عن توزيع أرباح يونيو 2024:")
        for emp in missing:
            name = frappe.db.get_value('Employee', emp, 'employee_name')
            print(f"    - {emp} | {name}")
    else:
        print("\n  جميع الموظفون المستقيلون موجودون في توزيع أرباح يونيو 2024")

    print(f"\n  إجمالي توزيع الأرباح لشهر يونيو 2024: {len(allocations)} سطر")


def step4_fix_resignations():
    print(f"\n{'─'*50}")
    print("الخطوة 4: مقارنة وإصلاح سجلات الاستقالة")
    print(f"{'─'*50}")

    from masar_savingfund.custom.employee.employee import get_employee_savefund_balance

    resigned_submitted = frappe.db.sql("""
        SELECT name, employee, employee_name,
               resignation_date, docstatus,
               employee_contr, bank_contr,
               pl_employee_contr, pl_bank_contr,
               deserved_amount, total_right
        FROM `tabEmployee Resignation`
        WHERE resignation_date BETWEEN %s AND %s
          AND docstatus = 1
    """, (TARGET_MONTH_FROM, TARGET_MONTH_TO), as_dict=True)

    if not resigned_submitted:
        print("  لا توجد سجلات استقالة مُرسَلة لهذه الفترة")
        return

    for r in resigned_submitted:
        live_balance = get_employee_savefund_balance(
            json.dumps([r.employee]), r.resignation_date
        )

        if not live_balance:
            print(f"  لا يوجد رصيد للموظف {r.employee_name}")
            continue

        lb = live_balance[0]
        live_deserved = flt(lb.get('deserved_amount', 0))
        stored_deserved = flt(r.deserved_amount)
        diff = live_deserved - stored_deserved

        print(f"\n  الموظف: {r.employee} — {r.employee_name}")
        print(f"    المستحق المُخزَّن : {stored_deserved:,.2f}")
        print(f"    المستحق الصحيح   : {live_deserved:,.2f}")
        print(f"    الفارق           : {diff:+,.2f}")

        if abs(diff) < 0.01:
            print(f"    الحالة: لا يوجد فارق — لا حاجة للإصلاح")
            continue

        print(f"    الحالة: يوجد فارق — يحتاج إصلاح")

        if not DRY_RUN:
            _fix_resignation(r.name, r.employee_name)
        else:
            print(f"    [DRY RUN] سيتم إلغاء {r.name} وإعادة إرساله")


def _fix_resignation(doc_name, employee_name):
    """إلغاء السجل وإعادة إرساله بالبيانات الصحيحة"""
    try:
        doc = frappe.get_doc('Employee Resignation', doc_name)

        print(f"    جاري إلغاء {doc_name}...")
        doc.cancel()
        frappe.db.commit()

        print(f"    جاري إنشاء نسخة جديدة...")
        new_doc = frappe.copy_doc(doc)
        new_doc.docstatus = 0
        new_doc.amended_from = doc_name
        new_doc.insert()
        frappe.db.commit()

        print(f"    جاري إرسال النسخة الجديدة {new_doc.name}...")
        new_doc.submit()
        frappe.db.commit()

        print(f"    تم الإصلاح: {doc_name} → {new_doc.name}")
        print(f"       المستحق الجديد: {flt(new_doc.deserved_amount):,.2f}")

    except Exception as e:
        frappe.db.rollback()
        print(f"    خطأ في إصلاح {doc_name}: {str(e)}")
