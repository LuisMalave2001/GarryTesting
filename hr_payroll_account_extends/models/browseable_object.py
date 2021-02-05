#-*- coding:utf-8 -*-

from odoo.addons.hr_payroll.models.browsable_object import Payslips

def get_deductions_amount(self):
    return self.dict.get_deductions_amount()

Payslips.get_deductions_amount = get_deductions_amount