#-*- coding:utf-8 -*-

import json

from odoo import models, fields, api
from odoo.exceptions import MissingError, ValidationError

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    move_line_ids = fields.One2many(string="Invoice/Bill Lines",
        comodel_name="account.move.line",
        inverse_name="payslip_id")
    deduction_ids = fields.One2many(string="Invoice Payments",
        comodel_name="hr.payslip.deduction",
        inverse_name="payslip_id")
    
    def compute_sheet(self):
        for payslip in self.filtered(lambda s: s.state not in ["cancel", "done"]):
            payslip.deduction_ids.unlink()
        super(HrPayslip, self).compute_sheet()
        self._compute_deductions()
        return super(HrPayslip, self).compute_sheet()
    
    def _compute_deductions(self):
        for payslip in self.filtered(lambda s: s.state not in ["cancel", "done"]):
            if not payslip.employee_id or payslip.credit_note or not payslip.struct_id.type_id.invoice_payment_scope:
                continue
            deduction_vals = payslip._get_deduction_lines()
            deductions = self.env["hr.payslip.deduction"]
            for r in deduction_vals:
                deductions += deductions.new(r)
            payslip.deduction_ids = deductions
        return

    def _get_deduction_lines(self):
        self.ensure_one()
        res = []
        if not self.employee_id.address_home_id:
            raise MissingError("Private address of {} is not set. Set the private address in the employee form.".format(self.employee_id.name))
        partner = self.employee_id.address_home_id
        results, total, amls = self.env["report.account.report_agedpartnerbalance"].with_context(
            partner_ids=partner)._get_partner_move_lines(
                    ["receivable"], fields.Date.context_today(self), "posted", 30)
        remaining_wage = self.net_wage
        for aml in amls.get(partner.id, []):
            if aml["line"].date > self.date_to:
                continue
            if aml["amount"] <= 0 or ("overdue" in self.struct_id.type_id.invoice_payment_scope and aml["period"] >= 6):
                continue
            if self.struct_id.type_id.invoice_payment_scope == "overdue_end_of_period" and aml["line"].date_maturity > self.date_to:
                continue
            residual_amount = min(aml["amount"], remaining_wage)
            deduction_vals = {
                "move_line_id": aml["line"].id,
                "amount": residual_amount,
            }
            res.append(deduction_vals)
            remaining_wage -= residual_amount
            if not remaining_wage:
                break
        return res
    
    def get_deductions_amount(self):
        self.ensure_one()
        return sum(self.deduction_ids.mapped("amount"))

    def action_payslip_done(self):
        payslip_runs = self.filtered(lambda s: s.payslip_run_id).mapped("payslip_run_id")
        for run in payslip_runs:
            run_payslips = run.slip_ids.filtered(lambda s: s.state not in ["cancel", "done"])
            separated_payslips = run_payslips - self
            if separated_payslips:
                raise ValidationError(("You cannot create a draft entry for a payslip separate from other draft/waiting payslips in the same batch\n" \
                    "Batch: %s\n\n" \
                    "Included Payslips: %s\n\n" \
                    "Missing Payslips: %s") %
                    (run.name, ", ".join(self.filtered(lambda s: s.payslip_run_id == run).mapped("number")), ", ".join(separated_payslips.mapped("number"))))

        for payslip in self:
            employee = payslip.employee_id
            if not employee.address_home_id:
                raise MissingError("Private address of {} is not set. Set the private address in the employee form.".format(employee.name))
            if not employee.payroll_bill_product_id:
                raise MissingError("Payroll bill product of {} is not set. Set the product in the employee form.".format(employee.name))
            if not employee.payroll_invoice_product_id:
                raise MissingError("Payroll invoice product of {} is not set. Set the product in the employee form.".format(employee.name))
            if not employee.payroll_journal_id:
                raise MissingError("Payroll journal of {} is not set. Set the journal in the employee form.".format(employee.name))

        self.compute_sheet()
        res = super(HrPayslip, self).action_payslip_done()

        move_obj = self.env["account.move"]
        move_line_obj = self.env["account.move.line"]
        move_data = {}
        for payslip in self.filtered(lambda p: p.move_id and p.move_id.state == 'draft' and not p.move_line_ids):
            data = {}
            payslip_batch_bill_date = payslip.payslip_run_id.bill_date
            if payslip_batch_bill_date:
                payslip.move_id.date = payslip_batch_bill_date
            
            # CREATE INVOICE DEDUCTION OR BILL FOR EMPLOYEE PAY
            product = payslip.employee_id.payroll_invoice_product_id
            if not payslip.credit_note:
                credit_note_data = {}
                for deduction in payslip.deduction_ids:
                    credit_note_data.setdefault(deduction.move_id.partner_id.id, {})
                    credit_note_data[deduction.move_id.partner_id.id].setdefault(deduction.move_id.family_id.id, {})
                    credit_note_data[deduction.move_id.partner_id.id][deduction.move_id.family_id.id].setdefault(deduction.move_id.student_id.id, {})
                    credit_note_data[deduction.move_id.partner_id.id][deduction.move_id.family_id.id][deduction.move_id.student_id.id].setdefault(deduction.move_line_id.account_id.id, {
                        "amount": 0,
                        "reconcile_ids": []
                    })
                    credit_note_data[deduction.move_id.partner_id.id][deduction.move_id.family_id.id][deduction.move_id.student_id.id][deduction.move_line_id.account_id.id]["amount"] += deduction.amount
                    credit_note_data[deduction.move_id.partner_id.id][deduction.move_id.family_id.id][deduction.move_id.student_id.id][deduction.move_line_id.account_id.id]["reconcile_ids"] += [deduction.move_line_id.id]
                
                # CREATE CREDIT NOTES
                for partner_id, family_ids in credit_note_data.items():
                    for family_id, student_ids in family_ids.items():
                        for student_id, account_ids in student_ids.items():
                            for account_id, details in account_ids.items():
                                credit_note_vals = {
                                    "type": "out_refund",
                                    "partner_id": partner_id,
                                    "family_id": family_id,
                                    "student_id": student_id,
                                    "journal_id": payslip.employee_id.payroll_journal_id.id
                                }
                                if payslip_batch_bill_date:
                                    credit_note_vals["invoice_date"] = payslip_batch_bill_date
                                    credit_note_vals["date"] = payslip_batch_bill_date
                                credit_note = move_obj.create(credit_note_vals)
                                credit_note._onchange_partner_id()
                                accounts = product.product_tmpl_id.get_product_accounts(fiscal_pos=credit_note.fiscal_position_id)
                                created_line = move_line_obj.create({
                                    "move_id": credit_note.id,
                                    "product_id": product.id,
                                    "account_id": accounts["income"].id,
                                    "analytic_account_id": payslip.contract_id.analytic_account_id.id,
                                    "quantity": 1,
                                    "payslip_id": payslip.id,
                                })
                                created_line._onchange_product_id()
                                credit_note.write({
                                    "invoice_line_ids": [(1, created_line.id, {
                                        "name": created_line.name + "\n" + payslip.number + " (" + payslip.name + ")",
                                        "price_unit": details["amount"],
                                    })]
                                })
                                credit_note.action_post()
                                for line_id in details["reconcile_ids"]:
                                    credit_note.js_assign_outstanding_line(line_id)
                                for line in credit_note.line_ids:
                                    if line.account_id.user_type_id.type == "receivable" and line.account_id.id != account_id:
                                        line.account_id = account_id

            if payslip.net_wage:
                product = payslip.employee_id.payroll_bill_product_id
                payslip_bill_vals = {
                    "type": "in_refund" if (payslip.credit_note or payslip.net_wage < 0) else "in_invoice",
                    "partner_id": payslip.employee_id.address_home_id.id,
                    "journal_id": payslip.employee_id.payroll_journal_id.id,
                }
                if payslip_batch_bill_date:
                    payslip_bill_vals["invoice_date"] = payslip_batch_bill_date
                    payslip_bill_vals["date"] = payslip_batch_bill_date
                payslip_bill = move_obj.create(payslip_bill_vals)
                payslip_bill._onchange_partner_id()
                move_data.setdefault(payslip_bill.id, {})
                accounts = product.product_tmpl_id.get_product_accounts(fiscal_pos=payslip_bill.fiscal_position_id)
                created_line = move_line_obj.create({
                    "move_id": payslip_bill.id,
                    "product_id": product.id,
                    "account_id": accounts["expense"].id,
                    "analytic_account_id": payslip.contract_id.analytic_account_id.id,
                    "quantity": 1,
                    "payslip_id": payslip.id,
                })
                created_line._onchange_product_id()
                move_data[payslip_bill.id][created_line.id] = {
                    "name": created_line.name + "\n" + payslip.number + " (" + payslip.name + ")",
                    "price_unit": abs(payslip.net_wage),
                }

            # ALLOWANCES AND DEDUCTIONS
            adjustments = {}
            matched = payslip.contract_id.allowance_ids.filtered(
                lambda a: all([a.debit_account_id, a.credit_account_id]))
            if matched:
                adjustments["Contract Payments"] = matched
            matched = payslip.contract_id.other_allowance_ids.filtered(
                lambda a: all([a.debit_account_id, a.credit_account_id, a.date >= payslip.date_from, a.date <= payslip.date_to]))
            if matched:
                adjustments["Other Contract Payments"] = matched
            matched = payslip.contract_id.deduction_ids.filtered(
                lambda a: all([a.debit_account_id, a.credit_account_id]))
            if matched:
                adjustments["Contract Deductions"] = matched
            matched = payslip.contract_id.other_deduction_ids.filtered(
                lambda a: all([a.debit_account_id, a.credit_account_id, a.date >= payslip.date_from, a.date <= payslip.date_to]))
            if matched:
                adjustments["Other Contract Deductions"] = matched

            for label_base, adjs in adjustments.items():
                for adj in adjs:
                    label = label_base + ": " + adj.name
                    data.setdefault(label, {})
                    data[label].setdefault(adj.debit_account_id.id, {})
                    data[label].setdefault(adj.credit_account_id.id, {})
                    analytic_account_id = adj.analytic_account_id.id or payslip.contract_id.analytic_account_id.id
                    data[label][adj.debit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                    data[label][adj.credit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                    data[label][adj.debit_account_id.id][analytic_account_id]["debit"] += adj.amount
                    data[label][adj.credit_account_id.id][analytic_account_id]["credit"] += adj.amount
            
            # CONTRIBUTIONS
            contribs = payslip.contract_id.contribution_ids.filtered(
                lambda c: all([c.emp_debit_account_id, c.emp_credit_account_id]))
            label_base = "Employee Contributions"
            for contrib in contribs:
                label = label_base + ": " + contrib.name
                data.setdefault(label, {})
                data[label].setdefault(contrib.emp_debit_account_id.id, {})
                data[label].setdefault(contrib.emp_credit_account_id.id, {})
                analytic_account_id = contrib.emp_analytic_account_id.id or payslip.contract_id.analytic_account_id.id
                data[label][contrib.emp_debit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                data[label][contrib.emp_credit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                data[label][contrib.emp_debit_account_id.id][analytic_account_id]["debit"] += contrib.employee_amount
                data[label][contrib.emp_credit_account_id.id][analytic_account_id]["credit"] += contrib.employee_amount
            contribs = payslip.contract_id.contribution_ids.filtered(
                lambda c: all([c.comp_debit_account_id, c.comp_credit_account_id]))
            label_base = "Company Contributions"
            for contrib in contribs:
                label = label_base + ": " + contrib.name
                data.setdefault(label, {})
                data[label].setdefault(contrib.comp_debit_account_id.id, {})
                data[label].setdefault(contrib.comp_credit_account_id.id, {})
                analytic_account_id = contrib.comp_analytic_account_id.id or payslip.contract_id.analytic_account_id.id
                data[label][contrib.comp_debit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                data[label][contrib.comp_credit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                data[label][contrib.comp_debit_account_id.id][analytic_account_id]["debit"] += contrib.company_amount
                data[label][contrib.comp_credit_account_id.id][analytic_account_id]["credit"] += contrib.company_amount
            
            # LOANS
            payments = payslip.loan_payment_ids.filtered(
                lambda p: all([p.loan_id.debit_account_id, p.loan_id.credit_account_id]))
            for payment in payments:
                label = "Loan Payment: " + payment.loan_id.name
                data.setdefault(label, {})
                data[label].setdefault(payment.loan_id.debit_account_id.id, {})
                data[label].setdefault(payment.loan_id.credit_account_id.id, {})
                analytic_account_id = payment.loan_id.analytic_account_id.id
                data[label][payment.loan_id.debit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                data[label][payment.loan_id.credit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                data[label][payment.loan_id.debit_account_id.id][analytic_account_id]["debit"] += payment.amount
                data[label][payment.loan_id.credit_account_id.id][analytic_account_id]["credit"] += payment.amount
            
            # SAVINGS
            payments = payslip.savings_payment_ids.filtered(
                lambda p: all([p.savings_id.debit_account_id, p.savings_id.credit_account_id]))
            for payment in payments:
                label = "Savings Payment: " + payment.savings_id.name
                data.setdefault(label, {})
                data[label].setdefault(payment.savings_id.debit_account_id.id, {})
                data[label].setdefault(payment.savings_id.credit_account_id.id, {})
                analytic_account_id = payment.savings_id.analytic_account_id.id
                data[label][payment.savings_id.debit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                data[label][payment.savings_id.credit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                data[label][payment.savings_id.debit_account_id.id][analytic_account_id]["debit"] += payment.amount
                data[label][payment.savings_id.credit_account_id.id][analytic_account_id]["credit"] += payment.amount

            line_ids = []
            for label, accounts in data.items():
                for account_id, analytic_accounts in accounts.items():
                    for analytic_account_id, amounts in analytic_accounts.items():
                        line_ids.append((0, 0, {
                            "move_id": payslip.move_id.id,
                            "account_id": account_id,
                            "name": label,
                            "analytic_account_id": analytic_account_id,
                            "debit": amounts["credit"] if payslip.credit_note else amounts["debit"],
                            "credit": amounts["debit"] if payslip.credit_note else amounts["credit"],
                        }))
            payslip.move_id.write({"line_ids": line_ids})

            # CREATE/UPDATE VENDOR BILLS FOR CONTRIBUTIONS
            for contrib in payslip.contract_id.contribution_ids:
                # EMPLOYEE
                contrib_bill_domain = [
                    ("type","=","in_invoice"),
                    ("partner_id","=",contrib.partner_id.id),
                    ("journal_id","=",contrib.emp_journal_id.id),
                    ("state","=","draft")
                ]
                contrib_bill_vals = {
                    "type": "in_invoice",
                    "partner_id": contrib.partner_id.id,
                    "journal_id": contrib.emp_journal_id.id,
                }
                if payslip_batch_bill_date:
                    contrib_bill_domain.append(("invoice_date","=",payslip_batch_bill_date))
                    contrib_bill_domain.append(("date","=",payslip_batch_bill_date))
                    contrib_bill_vals["invoice_date"] = payslip_batch_bill_date
                    contrib_bill_vals["date"] = payslip_batch_bill_date
                matched_bill = move_obj.search(contrib_bill_domain, limit=1)
                if not matched_bill:
                    matched_bill = move_obj.create(contrib_bill_vals)
                    matched_bill._onchange_partner_id()
                move_data.setdefault(matched_bill.id, {})
                accounts = contrib.emp_product_id.product_tmpl_id.get_product_accounts(fiscal_pos=matched_bill.fiscal_position_id)
                created_line = move_line_obj.create({
                    "move_id": matched_bill.id,
                    "product_id": contrib.emp_product_id.id,
                    "account_id": accounts["expense"].id,
                    "analytic_account_id": contrib.emp_analytic_account_id.id,
                    "quantity": 1,
                    "payslip_id": payslip.id,
                })
                created_line._onchange_product_id()
                move_data[matched_bill.id][created_line.id] = {
                    "name": created_line.name + "\n" + payslip.number + " (" + payslip.name + ")",
                    "price_unit": -contrib.employee_amount if payslip.credit_note else contrib.employee_amount,
                }
                
                # COMPANY
                contrib_bill_domain = [
                    ("type","=","in_invoice"),
                    ("partner_id","=",contrib.partner_id.id),
                    ("journal_id","=",contrib.comp_journal_id.id),
                    ("state","=","draft")
                ]
                contrib_bill_vals = {
                    "type": "in_invoice",
                    "partner_id": contrib.partner_id.id,
                    "journal_id": contrib.comp_journal_id.id,
                }
                if payslip_batch_bill_date:
                    contrib_bill_domain.append(("invoice_date","=",payslip_batch_bill_date))
                    contrib_bill_domain.append(("date","=",payslip_batch_bill_date))
                    contrib_bill_vals["invoice_date"] = payslip_batch_bill_date
                    contrib_bill_vals["date"] = payslip_batch_bill_date
                matched_bill = move_obj.search(contrib_bill_domain, limit=1)
                if not matched_bill:
                    matched_bill = move_obj.create(contrib_bill_vals)
                    matched_bill._onchange_partner_id()
                move_data.setdefault(matched_bill.id, {})
                accounts = contrib.comp_product_id.product_tmpl_id.get_product_accounts(fiscal_pos=matched_bill.fiscal_position_id)
                created_line = move_line_obj.create({
                    "move_id": matched_bill.id,
                    "product_id": contrib.comp_product_id.id,
                    "account_id": accounts["expense"].id,
                    "analytic_account_id": contrib.comp_analytic_account_id.id,
                    "quantity": 1,
                    "payslip_id": payslip.id,
                })
                created_line._onchange_product_id()
                move_data[matched_bill.id][created_line.id] = {
                    "name": created_line.name + "\n" + payslip.number + " (" + payslip.name + ")",
                    "price_unit": -contrib.company_amount if payslip.credit_note else contrib.company_amount,
                }

        # UPDATE MOVES
        for move_id, created_lines in move_data.items():
            move = move_obj.browse(move_id)
            invoice_line_ids = []
            for line in move.invoice_line_ids:
                if line.id in created_lines:
                    invoice_line_ids.append((1, line.id, created_lines[line.id]))
                else:
                    invoice_line_ids.append((1, line.id, {
                        "name": line.name,
                        "account_id": line.account_id.id,
                    }))
            move.write({"invoice_line_ids": invoice_line_ids})

        return res