# -*- coding: utf-8 -*-

from odoo import api, fields, models

class TuitionPlanInstallment(models.Model):
    _inherit = "tuition.plan.installment"

    def _get_end_date(self):
        if self._context.get("optimize"):
            return self.date
        return super(TuitionPlanInstallment, self)._get_end_date()