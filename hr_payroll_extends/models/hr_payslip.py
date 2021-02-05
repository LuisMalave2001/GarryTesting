#-*- coding:utf-8 -*-

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    loan_payment_ids = fields.One2many(string="Loan Payments",
        comodel_name="hr.loan.payment",
        inverse_name="payslip_id",
        copy=True)
    savings_payment_ids = fields.One2many(string="Savings Payments",
        comodel_name="hr.savings.payment",
        inverse_name="payslip_id",
        copy=True)

    @api.onchange("struct_id")
    def _onchange_struct_id(self):
        close_date = self.struct_id.type_id.default_close_date
        if close_date > 0:
            self.date_to = fields.Date.to_string(date.today().replace(day=close_date))
            self.date_from = self.date_to + relativedelta(months=-1, days=1)

    def _get_worked_day_lines(self):
        res = []
        self.ensure_one()
        contract = self.contract_id
        if contract.resource_calendar_id:
            paid_amount = self._get_contract_wage()
            unpaid_work_entry_types = self.struct_id.unpaid_work_entry_type_ids.ids

            work_hours = contract._get_work_hours(self.date_from, self.date_to)
            number_of_days = (self.date_to - self.date_from).days + 1
            hours_in_a_day = 0
            for date in (self.date_from + relativedelta(days=n) for n in range(number_of_days)):
                hours_in_a_day = sum(contract._get_work_hours(date, date).values())
                if hours_in_a_day > 0:
                    break

            work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
            biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
            add_days_rounding = 0
            
            total_hours = sum(work_hours.values()) or 1
            paid_hours = 0
            unpaid_hours = 0
            for work_entry_type_id, hours in work_hours_ordered:
                if work_entry_type_id not in unpaid_work_entry_types:
                    paid_hours += hours
                else:
                    unpaid_hours += hours
            if self.struct_id.type_id.unpaid_deduction_basis == "natural_days":
                total_hours = (hours_in_a_day * number_of_days) or 1
            elif self.struct_id.type_id.unpaid_deduction_basis == "fixed_days":
                total_hours = (hours_in_a_day * self.struct_id.type_id.days_in_a_month) or 1
            multiplier = 1
            if paid_hours:
                multiplier = (total_hours - unpaid_hours) / paid_hours

            for work_entry_type_id, hours in work_hours_ordered:
                work_entry_type = self.env["hr.work.entry.type"].browse(work_entry_type_id)
                is_paid = work_entry_type_id not in unpaid_work_entry_types
                calendar = contract.resource_calendar_id
                days = round(hours / calendar.hours_per_day, 5) if calendar.hours_per_day else 0
                if work_entry_type_id == biggest_work:
                    days += add_days_rounding
                day_rounded = self._round_days(work_entry_type, days)
                add_days_rounding += (days - day_rounded)
                attendance_line = {
                    "sequence": work_entry_type.sequence,
                    "work_entry_type_id": work_entry_type_id,
                    "number_of_days": day_rounded,
                    "number_of_hours": hours,
                    "amount": hours * multiplier * paid_amount / total_hours if is_paid else 0,
                }
                res.append(attendance_line)
        return res

    @api.onchange("employee_id", "date_to", "contract_id")
    def _compute_loan_and_savings_payments(self):
        if not self.employee_id or not self.date_to:
            return
        payments_vals = self.get_loan_payment_lines(self.employee_id, self.date_to)
        loan_payments = self.env["hr.loan.payment"]
        for r in payments_vals:
            loan_payments += loan_payments.new(r)
        self.loan_payment_ids = loan_payments
        payments_vals = self.get_savings_payment_lines(self.employee_id, self.date_to)
        savings_payments = self.env["hr.savings.payment"]
        for r in payments_vals:
            savings_payments += savings_payments.new(r)
        self.savings_payment_ids = savings_payments
        return

    @api.model
    def get_loan_payment_lines(self, employee, date_to):
        res = []
        loans = self.env["hr.loan"].search([
            ("employee_id","=",employee.id),
            ("state","=","open"),
            ("date_deduction","<=",date_to)])
        for loan in loans:
            balance = loan.amount - loan.total_paid
            amount = balance if loan.payslip_deduction > balance else loan.payslip_deduction
            payment_vals = {
                "loan_id": loan.id,
                "amount": amount,
            }
            res.append(payment_vals)
        return res
    
    def get_loans_amount(self, partner_id=None, code=False):
        self.ensure_one()
        amount = 0
        for payment in self.loan_payment_ids.filtered(lambda l: l.code == code):
            if not partner_id:
                amount += payment.amount
            elif partner_id and partner_id == payment.partner_id.id:
                amount += payment.amount
        return amount

    @api.model
    def get_savings_payment_lines(self, employee, date_to):
        res = []
        savings = self.env["hr.savings"].search([
            ("employee_id","=",employee.id),
            ("state","=","open"),
            ("date_deduction","<=",date_to)])
        for saving in savings:
            payment_vals = {
                "savings_id": saving.id,
                "amount": self.contract_id.wage * saving.payslip_deduction / 100 if saving.percentage_of_wage else saving.payslip_deduction,
            }
            res.append(payment_vals)
        return res
    
    def get_savings_amount(self, partner_id=None, code=False):
        self.ensure_one()
        amount = 0
        for payment in self.savings_payment_ids.filtered(lambda l: l.code == code):
            if not partner_id:
                amount += payment.amount
            elif partner_id and partner_id == payment.partner_id.id:
                amount += payment.amount
        return amount