// Copyright (c) 2023, Karama kcsc and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Employee Resignation', {
// 	employee: function(frm) {
//     fetch_employee_details(frm);
//   },
//   resignation_date: function(frm) {
//         if (frm.doc.docstatus !== 0 || !frm.doc.resignation_date || !frm.doc.date_of_joining)
//             return;
//         run_equity_and_income_logic(frm);
//     }
// });

// Show General Ledger
frappe.ui.form.on('Employee Resignation', {
	refresh: function(frm) {
	  frm.events.show_general_ledger(frm);
	}
  });
  
  frappe.ui.form.on('Employee Resignation', {
  show_general_ledger: function(frm) {
	if(frm.doc.docstatus > 0) {
	  frm.add_custom_button(__('Show GL Ledger'), function() {
		frappe.route_options = {
		  "voucher_no": frm.doc.name,
		  "from_date": frm.doc.posting_date,
		  "to_date": moment(frm.doc.modified).format('YYYY-MM-DD'),
		  "company": frm.doc.company,
		  "group_by": "",
		  "show_cancelled_entries": frm.doc.docstatus === 2
		};
		frappe.set_route("query-report", "General Ledger");
	  }, "fa fa-table");
	}
  }
  });
  // END Show General Ledger

  cur_frm.fields_dict['employee'].get_query = function(doc) {
	return {
		filters: {
			"status": "Active"
		}
	}
}

function run_equity_and_income_logic(frm) {
    frappe.call({
        doc: frm.doc,
        method: "masar_savingfund.masar_saving_fund.doctype.employee_resignation.employee_resignation.get_employee_equity_balance",
        callback: function(r) {

            const resignationDate = new Date(frm.doc.resignation_date);
            const joiningDate = new Date(frm.doc.date_of_joining);
            const yearDiff = (resignationDate - joiningDate) / (1000 * 3600 * 24 * 365.25);

            const response = r.message ? JSON.parse(r.message) : {};

            let withdrawAmount = frm.doc.withdraw_amount || 0;
            let employeeEquity = frm.doc.employee_contr || 0;
            let bankEquity = frm.doc.bank_contr || 0;
            let empIncome = frm.doc.pl_employee_contr || 0;
            let bankIncome = frm.doc.pl_bank_contr || 0;

            // Year logic
            if (yearDiff < 1) {
                frm.set_value('employee_equity_amount', employeeEquity);
                frm.set_value('bank_equity_amount', 0);
                frm.set_value('emp_income_amount', 0);
                frm.set_value('bank_income_amount', 0);
            }
            else if (yearDiff >= 1 && yearDiff < 3) {
                frm.set_value('employee_equity_amount', employeeEquity);
                frm.set_value('bank_equity_amount', 0);
                frm.set_value('emp_income_amount', empIncome);
                frm.set_value('bank_income_amount', 0);
            }
            else if (yearDiff >= 3) {
                frm.set_value('employee_equity_amount', employeeEquity);
                frm.set_value('bank_equity_amount', bankEquity);
                frm.set_value('emp_income_amount', empIncome);
                frm.set_value('bank_income_amount', bankIncome);
            }


            // Withdrawal logic
            if (withdrawAmount > 0) {
                let empEquityVal = frm.doc.employee_contr || 0;
                let bankEquityVal = frm.doc.bank_contr || 0;
                let empIncomeVal = frm.doc.pl_employee_contr || 0;
                let bankIncomeVal = frm.doc.pl_bank_contr || 0;

                const totalBeforeWithdrawal =
                    empEquityVal + bankEquityVal + empIncomeVal + bankIncomeVal;

                if (totalBeforeWithdrawal > 0) {

                    const empEquityRatio = empEquityVal / totalBeforeWithdrawal;
                    const bankEquityRatio = bankEquityVal / totalBeforeWithdrawal;
                    const empIncomeRatio = empIncomeVal / totalBeforeWithdrawal;
                    const bankIncomeRatio = bankIncomeVal / totalBeforeWithdrawal;

                    const empEquityRemaining = empEquityVal - withdrawAmount * empEquityRatio;
                    const bankEquityRemaining = bankEquityVal - withdrawAmount * bankEquityRatio;
                    const empIncomeRemaining = empIncomeVal - withdrawAmount * empIncomeRatio;
                    const bankIncomeRemaining = bankIncomeVal - withdrawAmount * bankIncomeRatio;

                    frm.set_value('employee_equity_amount', Math.max(empEquityRemaining, 0));
                    frm.set_value('bank_equity_amount', Math.max(bankEquityRemaining, 0));
                    frm.set_value('emp_income_amount', Math.max(empIncomeRemaining, 0));
                    frm.set_value('bank_income_amount', Math.max(bankIncomeRemaining, 0));
                }
            }


            // Income calculation
            const incomeEmp = (frm.doc.employee_equity_amount || 0) - (frm.doc.employee_contr || 0);
            const incomeEmpPL = (frm.doc.emp_income_amount || 0) - (frm.doc.pl_employee_contr || 0);
            const incomeBank = (frm.doc.bank_equity_amount || 0) - (frm.doc.bank_contr || 0);
            const incomeBankPL = (frm.doc.bank_income_amount || 0) - (frm.doc.pl_bank_contr || 0);
            const totalIncome = incomeEmp + incomeBank + incomeEmpPL + incomeBankPL;

            frm.set_value('income_emp_amount', Math.abs(incomeEmp));
            frm.set_value('income_emp_amount_pl', Math.abs(incomeEmpPL));
            frm.set_value('income_bank_amount', Math.abs(incomeBank));
            frm.set_value('income_bank_amount_pl', Math.abs(incomeBankPL));
            frm.set_value('income_amount', Math.abs(totalIncome));
            frm.set_value('number_of_years', yearDiff.toFixed(2));

            [
                'employee_equity_amount',
                'bank_equity_amount',
                'emp_income_amount',
                'bank_income_amount',
                'income_emp_amount',
                'income_bank_amount',
                'income_amount',
                'number_of_years',
            ].forEach(field => frm.refresh_field(field));
        }
    });
}

function fetch_employee_details(frm) {
  //Get the employees listed in the form
    var selected_employees = new Array();
    selected_employees.push(frm.doc.employee);

    frappe.call({
        method: "masar_savingfund.custom.employee.employee.get_employee_savefund_balance",
        args: {
          selected_employees: selected_employees,
          date_to: frm.doc.posting_date
        },
        callback: function(r) {
            console.log(r.message);
              $.each(r.message, function(i, d) {
                frm.set_value('employee_contr', d.total_employee_contr);
                frm.set_value('bank_contr', d.total_bank_contr);
                frm.set_value('pl_employee_contr', d.total_employee_pl);
                frm.set_value('pl_bank_contr', d.total_bank_pl);
                frm.set_value('total_right', d.total_right);
                frm.set_value('deserved_amount', d.deserved_amount);
                frm.set_value('withdraw_amount', d.total_paid_amount);

          });
        }
    });
		cur_frm.refresh_field();
	}