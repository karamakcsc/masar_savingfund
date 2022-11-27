frappe.pages['saving-funds-dashboard'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}

MyPage=Class.extend({
	init: function(wrapper){
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Saving Funds Dashboard',
			single_column: true
		});
		this.make();
	},
	make: function(){
		let me=$(this);

		let chart_emps=[]
		let chart_emp_contr=[]
		let chart_bank_contr=[]


		let totals=function(){
			frappe.call({
				method:"masar_savingfund.masar_saving_fund.page.saving_funds_dashboard.saving_funds_dashboard.get_contr_totals",
				callback: function(r){
					$.each(r.message, function(i, d) {
             $("#total_emp_contr")[0].innerText = d.total_employee_contr.toFixed(3);
						 $("#total_bank_contr")[0].innerText = d.total_bank_contr.toFixed(3);
						 $("#total_contr")[0].innerText = d.total_contr.toFixed(3);
          });
				}
			})
			frappe.call({
				method:"masar_savingfund.masar_saving_fund.page.saving_funds_dashboard.saving_funds_dashboard.get_pl_totals",
				callback: function(z){
					$.each(z.message, function(i, d) {
						$("#total_emp_contr_pl")[0].innerText = d.total_employee_contr_pl.toFixed(3);
						$("#total_bank_contr_pl")[0].innerText = d.total_bank_contr_pl.toFixed(3);
						$("#total_contr_pl")[0].innerText = d.total_contr_pl.toFixed(3);
						$("#total_rights")[0].innerText =(parseInt($("#total_contr")[0].innerText)+ parseInt($("#total_contr_pl")[0].innerText)).toFixed(3);

					});
				}
			})
		}

		let funds=function(){
			// frappe.msgprint("Khabour")
			frappe.call({
				method:"masar_savingfund.masar_saving_fund.page.saving_funds_dashboard.saving_funds_dashboard.get_chart",
				callback: function(r){
					$.each(r.message, function(i, d) {
							chart_emps.push(d[i].employee_name)
							// chart_emp_contr.push(rsp[1])
							// chart_bank_contr.push(rsp[2])
          });
				}
			})

		}

		// let body='<h1>Hello, World</h1>'

		let page_chart=function(){
			const data = {
			labels: chart_emps,
			datasets: [
					{
							name: "Employee Contribution", type: "bar",
							values: [25, 40, 30, 35, 8, 52 , 17, -4]
					},
					{
							name: "Bank Contribution", type: "bar",
							values: [25, 50, -10, 15, 18, 32, 27, 14]
					}
			]
	}

	const chart = new frappe.Chart("#chart", {  // or a DOM element,
																							// new Chart() in case of ES6 module with above usage
			title: "Saving Funds Chart",
			data: data,
			type: 'axis-mixed', // or 'bar', 'line', 'scatter', 'pie', 'percentage'
			height: 250,
			colors: ['#7cd6fd', '#743ee2']
	})

		}

		$(frappe.render_template(frappe.saving_funds.body, this)).appendTo(this.page.main)
		totals()
		funds()
		page_chart()


	}

})

let body='<script src="https://unpkg.com/frappe-charts@1.2.4/dist/frappe-charts.min.iife.js"></script>'
body+='<div class="widget-group ">'
body+='			<div class="widget-group-head">'
body+='				<div class="widget-group-control"></div>'
body+='			</div>'
body+='			<div class="widget-group-body grid-col-3">'

body+='				<div class="widget widget-shadow number-widget-box" data-widget-name="total emp contr">'
body+='					<div class="widget-head">'
body+='					<div class="widget-label">'
body+='						<div class="widget-title">'
body+='							<div class="number-label">Total Employees Contributions</div>'
body+='						</div>'
body+='						<div class="widget-subtitle"></div>'
body+='					</div>'
body+='				</div>'
body+='				<div class="widget-body">'
body+='					<div class="widget-content">'
body+='						<div class="number" style="color:undefined" id="total_emp_contr"> 0</div>'
body+='					</div>'
body+='				</div>'
body+='				<div class="widget-footer"></div>'
body+='			</div>'

body+='				<div class="widget widget-shadow number-widget-box" data-widget-name="total bank contr">'
body+='					<div class="widget-head">'
body+='					<div class="widget-label">'
body+='						<div class="widget-title">'
body+='							<div class="number-label">Total Bank Contributions</div>'
body+='						</div>'
body+='						<div class="widget-subtitle"></div>'
body+='					</div>'
body+='				</div>'
body+='				<div class="widget-body">'
body+='					<div class="widget-content">'
body+='						<div class="number" style="color:undefined" id="total_bank_contr"> 0</div>'
body+='					</div>'
body+='				</div>'
body+='				<div class="widget-footer"></div>'
body+='			</div>'

body+='				<div class="widget widget-shadow number-widget-box" data-widget-name="total contr">'
body+='					<div class="widget-head">'
body+='					<div class="widget-label">'
body+='						<div class="widget-title">'
body+='							<div class="number-label">Total Contributions</div>'
body+='						</div>'
body+='						<div class="widget-subtitle"></div>'
body+='					</div>'
body+='				</div>'
body+='				<div class="widget-body">'
body+='					<div class="widget-content">'
body+='						<div class="number" style="color:undefined" id="total_contr"> 0</div>'
body+='					</div>'
body+='				</div>'
body+='				<div class="widget-footer"></div>'
body+='			</div>'

body+='				<div class="widget widget-shadow number-widget-box" data-widget-name="total rights">'
body+='					<div class="widget-head">'
body+='					<div class="widget-label">'
body+='						<div class="widget-title">'
body+='							<div class="number-label">Total Rights</div>'
body+='						</div>'
body+='						<div class="widget-subtitle"></div>'
body+='					</div>'
body+='				</div>'
body+='				<div class="widget-body">'
body+='					<div class="widget-content">'
body+='						<div class="number text-danger" style="color:undefined" id="total_rights"> 0</div>'
body+='					</div>'
body+='				</div>'
body+='				<div class="widget-footer"></div>'
body+='			</div>'


body+='				<div class="widget widget-shadow number-widget-box" data-widget-name="total emp contr pl">'
body+='					<div class="widget-head">'
body+='					<div class="widget-label">'
body+='						<div class="widget-title">'
body+='							<div class="number-label">Total Employees P&L Contributions</div>'
body+='						</div>'
body+='						<div class="widget-subtitle"></div>'
body+='					</div>'
body+='				</div>'
body+='				<div class="widget-body">'
body+='					<div class="widget-content">'
body+='						<div class="number" style="color:undefined" id="total_emp_contr_pl"> 0</div>'
body+='					</div>'
body+='				</div>'
body+='				<div class="widget-footer"></div>'
body+='			</div>'

body+='				<div class="widget widget-shadow number-widget-box" data-widget-name="total bank contr pl">'
body+='					<div class="widget-head">'
body+='					<div class="widget-label">'
body+='						<div class="widget-title">'
body+='							<div class="number-label">Total Bank P&L Contributions</div>'
body+='						</div>'
body+='						<div class="widget-subtitle"></div>'
body+='					</div>'
body+='				</div>'
body+='				<div class="widget-body">'
body+='					<div class="widget-content">'
body+='						<div class="number" style="color:undefined" id="total_bank_contr_pl"> 0</div>'
body+='					</div>'
body+='				</div>'
body+='				<div class="widget-footer"></div>'
body+='			</div>'

body+='				<div class="widget widget-shadow number-widget-box" data-widget-name="total contr pl">'
body+='					<div class="widget-head">'
body+='					<div class="widget-label">'
body+='						<div class="widget-title">'
body+='							<div class="number-label">Total P&L Contributions</div>'
body+='						</div>'
body+='						<div class="widget-subtitle"></div>'
body+='					</div>'
body+='				</div>'
body+='				<div class="widget-body">'
body+='					<div class="widget-content">'
body+='						<div class="number" style="color:undefined" id="total_contr_pl"> 0</div>'
body+='					</div>'
body+='				</div>'
body+='				<div class="widget-footer"></div>'
body+='			</div>'


body+='		</div>'
body+='	</div>'
body+='<div id="chart"></div>'

frappe.saving_funds={
	body: body
}
