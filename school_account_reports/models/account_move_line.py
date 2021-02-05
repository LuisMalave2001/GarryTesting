# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    student_id = fields.Many2one(string='Student',
        comodel_name='res.partner',
        compute='_compute_student_details',
        store=True)
    family_id = fields.Many2one(string='Family',
        comodel_name='res.partner',
        compute='_compute_student_details',
        store=True)
    grade_level_id = fields.Many2one(string='Grade Level',
        comodel_name='school_base.grade_level',
        related='student_id.grade_level_id',
        store=True)
    homeroom = fields.Char(string='Homeroom',
        related='student_id.homeroom',
        store=True)
    
    @api.depends('move_id', 'move_id.student_id', 'move_id.family_id',
                 'matched_debit_ids', 'matched_debit_ids.debit_move_id.move_id.student_id',
                 'matched_debit_ids.debit_move_id.move_id.family_id',
                 'matched_credit_ids', 'matched_credit_ids.credit_move_id.move_id.student_id',
                 'matched_credit_ids.credit_move_id.move_id.family_id')
    def _compute_student_details(self):
        for line in self:
            student = False
            family = False
            if line.move_id.student_id:
                student = line.move_id.student_id.id
                family = line.move_id.family_id.id
            if not student and line.matched_debit_ids:
                for debit in line.matched_debit_ids:
                    if debit.debit_move_id.move_id.student_id:
                        student = debit.debit_move_id.move_id.student_id.id
                        family = debit.debit_move_id.move_id.family_id.id
                        break
            if not student and line.matched_credit_ids:
                for credit in line.matched_credit_ids:
                    if credit.credit_move_id.move_id.student_id:
                        student = credit.credit_move_id.move_id.student_id.id
                        family = credit.credit_move_id.move_id.family_id.id
                        break
            line.student_id = student
            line.family_id = family