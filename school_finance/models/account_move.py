# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, exceptions


class AccountMove(models.Model):
    """ Added school finance functionalities """
    _inherit = "account.move"

    student_id = fields.Many2one("res.partner", string="Student", domain=[('person_type', '=', 'student')])
    family_id = fields.Many2one("res.partner", string="Family", domain=[('is_family', '=', True)])

    family_members_ids = fields.Many2many(related="family_id.member_ids")
    receivable_account_id = fields.Many2one("account.account", string="Receivable account", domain=[("user_type_id.type", "=", "receivable")])

    is_in_debug_mode = fields.Boolean(compute="compute_is_in_debug_mode")
    period_start = fields.Date(string="Period Start")
    period_end = fields.Date(string="Period End")
    invoice_payment_state_color = fields.Integer(string="Payment Status Color", compute="compute_invoice_payment_state_color")

    def compute_is_in_debug_mode(self):
        self.is_in_debug_mode = self.env.user.has_group('base.group_no_one')

    def compute_invoice_payment_state_color(self):
        for move in self:
            result = 0
            if move.invoice_payment_state == "not_paid":
                result = 1 #red
            elif move.invoice_payment_state == "in_payment":
                result = 3 #yellow
            elif move.invoice_payment_state == "paid":
                result = 10 #green
            move.invoice_payment_state_color = result

    def get_receivable_account_ids(self):
        return self.get_receivable_line_ids().mapped("account_id")

    def get_receivable_line_ids(self):
        return self.mapped("line_ids").filtered(lambda line_id: line_id.account_id.user_type_id.type == 'receivable')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "student_id" in vals and vals["student_id"]:
                student_id = self.env["res.partner"].browse([vals["student_id"]])
                if student_id:
                    if "student_grade_level" not in vals:
                        vals["student_grade_level"] = student_id.grade_level_id.id
                    if "student_homeroom" not in vals:
                        vals["student_homeroom"] = student_id.homeroom

        return super().create(vals_list)

    student_grade_level = fields.Many2one("school_base.grade_level", string="Grade level")
    student_homeroom = fields.Char(string="Student homeroom")

    def compute_grade_and_homeroom(self):
        self.ensure_one()

        if self.student_id:
            self.student_grade_level = self.student_id.grade_level_id
            self.student_homeroom = self.student_id.homeroom
        else:
            raise exceptions.ValidationError(_("You cannot compute the homeroom if there is not student..."))

    def set_receivable_account(self):
        """ It uses receivable_account_id field to set autoamtically the receivable account """
        for record in self:
            if record.receivable_account_id:
                receivable_line_ids = record.line_ids.filtered(
                    lambda line: line.account_id.user_type_id.type == 'receivable')
                for receivable_line_id in receivable_line_ids:
                    receivable_line_id.account_id = record.receivable_account_id.id



