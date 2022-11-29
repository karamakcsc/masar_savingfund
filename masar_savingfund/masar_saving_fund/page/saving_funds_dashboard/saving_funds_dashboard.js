
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
		// test()
		let me=$(this);

		let chart_emps=[]
		let chart_emp_contr=[]
		let chart_bank_contr=[]
		total_emp_contr=0
		total_bank_contr=0
		total_contr=0
		total_emp_contr_pl=0
		total_bank_contr_pl=0
		total_contr_pl=0
		total_rights=0
			frappe.call({
				method:"masar_savingfund.masar_saving_fund.page.saving_funds_dashboard.saving_funds_dashboard.get_saving_funds",
				callback: function (r){
					$.each(r.message, function (i, d) {
						total_emp_contr+=parseFloat(d.total_employee_contr.toFixed(3));
						total_bank_contr+=parseFloat(d.total_bank_contr.toFixed(3));
						total_contr+=parseFloat(d.total_contr.toFixed(3));
						total_emp_contr_pl+=parseFloat(d.total_employee_pl.toFixed(3));
						total_bank_contr_pl+=parseFloat(d.total_bank_pl.toFixed(3));
						total_contr_pl+=parseFloat(d.total_pl.toFixed(3));
						total_rights+=parseFloat(d.total_right.toFixed(3));
						 chart_emps.push(d["employee_name"])
						 chart_emp_contr.push(d["total_employee_contr"])
						 chart_bank_contr.push(d["total_bank_contr"])
          });
					$("#total_emp_contr")[0].innerText = total_emp_contr.toFixed(3)
					$("#total_bank_contr")[0].innerText = total_bank_contr.toFixed(3)
					$("#total_contr")[0].innerText =total_contr.toFixed(3)
					$("#total_emp_contr_pl")[0].innerText =total_emp_contr_pl.toFixed(3)
					$("#total_bank_contr_pl")[0].innerText = total_bank_contr_pl.toFixed(3)
					$("#total_contr_pl")[0].innerText = total_contr_pl.toFixed(3)
					$("#total_rights")[0].innerText =total_rights.toFixed(3)

					page_chart(chart_emps, chart_emp_contr, chart_bank_contr)

				}
			})

		let page_chart=function(chart_emps, chart_emp_contr, chart_bank_contr){ // equals to -> function page_chart(){

			const data = {
				labels: chart_emps,
				datasets: [
						{
								name: "Employee Contribution", type: "bar",
								values: chart_emp_contr
						},
						{
								name: "Bank Contribution", type: "bar",
								values: chart_bank_contr
						}
				]
			}


			const chart = new frappe.Chart("#chart", {  // or a DOM element,
																									// new Chart() in case of ES6 module with above usage
					title: "Saving Funds Chart",
					data: data,
					type: 'bar', // 'axis-mixed' or 'bar', 'line', 'scatter', 'pie', 'percentage'
					height: 250,
					colors: ['#7cd6fd', '#743ee2'],
					tooltipOptions: {
					    formatTooltipX: (d) => (d).toUpperCase(),
					    formatTooltipY: (d) => d
					}


			})

		}

		$(frappe.render_template(frappe.saving_funds.body, this)).appendTo(this.page.main)
		page_chart()

	}
})


let body='<script src="https://unpkg.com/frappe-charts@latest"></script>'
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
