# Copyright (c) 2022, Karama kcsc and contributors
# For license information, please see license.txt

# import frappe
# Copyright (c) 2022, Karama kcsc and contributors
# For license information, please see license.txt

# import frappe
from __future__ import unicode_literals
import frappe, erpnext, json,datetime
from frappe import _, scrub, ValidationError
from frappe.utils import flt, comma_or, nowdate, getdate
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from frappe.model.document import Document


class InvalidSavingFundPayment(ValidationError):
	pass
class SavingFundPayment(AccountsController):
	def __init__(self, *args, **kwargs):
		super(SavingFundPayment, self).__init__(*args, **kwargs)

	def validate(self):
		pass

	def on_submit(self):
		self.make_gl()

	def on_cancel(self, method):
		pass

	def make_gl(self):
		res_date=self.resignation_date
		join_date=self.date_of_joining
		res_date = datetime.datetime.strptime(res_date, '%Y-%m-%d')
		join_date = datetime.datetime.strptime(join_date, '%Y-%m-%d')
		number_year=(res_date-join_date).days/365.0
		gl_entries = []
		if number_year<1:
			gl_entries.append(
					self.get_gl_dict({
						"account": self.cash_account,
						#"account_currency": d.paid_from_account_currency,
						"against": self.employee_equity,
						"credit_in_account_currency": self.employee_contr,
						"credit": self.employee_contr,
						"employee": self.employee,
						"remarks": self.employee + ' : ' + self.employee_name
						}))
			gl_entries.append(
				self.get_gl_dict({
					"account": self.employee_equity,
					#"account_currency": d.paid_to_account_currency,
					"against": self.cash_account,
					"debit_in_account_currency": self.employee_contr,
					"debit": self.employee_contr,
					"employee": self.employee,
					"remarks": self.employee + ' : ' + self.employee_name
					}))
		if number_year>=1 and number_year<3:
			gl_entries.append(
					self.get_gl_dict({
						"account": self.cash_account,
						#"account_currency": d.paid_from_account_currency,
						"against": self.employee_equity,
						"credit_in_account_currency": self.employee_contr,
						"credit": self.employee_contr,
						"employee": self.employee,
						"remarks": self.employee + ' : ' + self.employee_name
						}))
			gl_entries.append(
				self.get_gl_dict({
					"account": self.employee_equity,
					#"account_currency": d.paid_to_account_currency,
					"against": self.cash_account,
					"debit_in_account_currency": self.employee_contr,
					"debit": self.employee_contr,
					"employee": self.employee,
					"remarks": self.employee + ' : ' + self.employee_name
					}))

			gl_entries.append(
					self.get_gl_dict({
						"account": self.cash_account,
						#"account_currency": d.paid_from_account_currency,
						"against": self.employee_equity,
						"credit_in_account_currency": self.pl_employee_contr,
						"credit": self.pl_employee_contr,
						"employee": self.employee,
						"remarks": self.employee + ' : ' + self.employee_name
						}))
			gl_entries.append(
				self.get_gl_dict({
					"account": self.employee_equity,
					#"account_currency": d.paid_to_account_currency,
					"against": self.cash_account,
					"debit_in_account_currency": self.pl_employee_contr,
					"debit": self.pl_employee_contr,
					"employee": self.employee,
					"remarks": self.employee + ' : ' + self.employee_name
					}))
		if number_year>=3:
			gl_entries.append(
					self.get_gl_dict({
						"account": self.cash_account,
						#"account_currency": d.paid_from_account_currency,
						"against": self.employee_equity,
						"credit_in_account_currency": self.employee_contr,
						"credit": self.employee_contr,
						"employee": self.employee,
						"remarks": self.employee + ' : ' + self.employee_name
						}))
			gl_entries.append(
				self.get_gl_dict({
					"account": self.employee_equity,
					#"account_currency": d.paid_to_account_currency,
					"against": self.cash_account,
					"debit_in_account_currency": self.employee_contr,
					"debit": self.employee_contr,
					"employee": self.employee,
					"remarks": self.employee + ' : ' + self.employee_name
					}))

			gl_entries.append(
					self.get_gl_dict({
						"account": self.cash_account,
						#"account_currency": d.paid_from_account_currency,
						"against": self.employee_equity,
						"credit_in_account_currency": self.pl_employee_contr,
						"credit": self.pl_employee_contr,
						"employee": self.employee,
						"remarks": self.employee + ' : ' + self.employee_name
						}))
			gl_entries.append(
				self.get_gl_dict({
					"account": self.employee_equity,
					#"account_currency": d.paid_to_account_currency,
					"against": self.cash_account,
					"debit_in_account_currency": self.pl_employee_contr,
					"debit": self.pl_employee_contr,
					"employee": self.employee,
					"remarks": self.employee + ' : ' + self.employee_name
					}))


			gl_entries.append(
					self.get_gl_dict({
						"account": self.cash_account,
						#"account_currency": d.paid_from_account_currency,
						"against": self.bank_equity,
						"credit_in_account_currency": self.bank_contr,
						"credit": self.bank_contr,
						"employee": self.employee,
						"remarks": self.employee + ' : ' + self.employee_name
						}))
			gl_entries.append(
				self.get_gl_dict({
					"account": self.bank_equity,
					#"account_currency": d.paid_to_account_currency,
					"against": self.cash_account,
					"debit_in_account_currency": self.bank_contr,
					"debit": self.bank_contr,
					"employee": self.employee,
					"remarks": self.employee + ' : ' + self.employee_name
					}))

			gl_entries.append(
					self.get_gl_dict({
						"account": self.cash_account,
						#"account_currency": d.paid_from_account_currency,
						"against": self.bank_equity,
						"credit_in_account_currency": self.pl_bank_contr,
						"credit": self.pl_bank_contr,
						"employee": self.employee,
						"remarks": self.employee + ' : ' + self.employee_name
						}))
			gl_entries.append(
				self.get_gl_dict({
					"account": self.bank_equity,
					#"account_currency": d.paid_to_account_currency,
					"against": self.cash_account,
					"debit_in_account_currency": self.pl_bank_contr,
					"debit": self.pl_bank_contr,
					"employee": self.employee,
					"remarks": self.employee + ' : ' + self.employee_name
					}))



		if gl_entries:
			make_gl_entries(gl_entries, cancel=0, adv_adj=0)
