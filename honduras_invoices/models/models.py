# -*- coding: utf-8 -*-

from ..tools import tools

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError, MissingError

# raise UserError(_('There is no responsible family for %s') % (line.product_id.categ_id.name))
class Invoice(models.Model):
    _inherit = "account.payment"

    amount_total_letters = fields.Char("Amount total in letters", compute="_compute_amount_total_letters")


    def _compute_amount_total_letters(self):
        for record in self:
            amount_total = record.amount
            number_converter = tools.NumberToTextConverter("LP.", "LPS.", "CTV.", "CTVS.")
            amount_total_letters = number_converter.numero_a_letra(amount_total)

            record.amount_total_letters = amount_total_letters

class Invoice(models.Model):
    _inherit = "account.move"

    amount_total_letters = fields.Char("Amount total in letters", compute="_compute_amount_total_letters")
    surcharge_invoice_id = fields.Many2one("Surcharge Invoice", readonly=True)
    authorized_range_from = fields.Char("Authorized range from", readonly=True)
    authorized_range_to = fields.Char("Authorized range to", readonly=True)
    cai = fields.Char("CAI", readonly=True)
    issue_limit_date = fields.Date("Issue limit date", readonly=True)
    hide_line_price = fields.Boolean(string="Hide Line Price in Print")

    def _formatLang(self, value):
        lang = self.partner_id.lang
        lang_objs = self.env['res.lang'].search([('code', '=', lang)])
        if not lang_objs:
            lang_objs = self.env['res.lang'].search([], limit=1)
        lang_obj = lang_objs[0]

        res = lang_obj.format('%.' + str(2) + 'f', value, grouping=True, monetary=True)
        currency_obj = self.currency_id;

        if currency_obj and currency_obj.symbol:
            if currency_obj.position == 'after':
                res = '%s %s' % (res, currency_obj.symbol)
            elif currency_obj and currency_obj.position == 'before':
                res = '%s %s' % (currency_obj.symbol, res)
        return res

    def _compute_amount_total_letters(self):
        for record in self:
            amount_total = record.amount_total
            number_converter = tools.NumberToTextConverter("LP.", "LPS.", "CTV.", "CTVS.")
            amount_total_letters = number_converter.numero_a_letra(amount_total)

            record.amount_total_letters = amount_total_letters
            
    @api.constrains("name")
    def _check_name_within_range(self):
        for move in self.filtered(lambda m: m.journal_id.is_honduras_invoice and m.state == "posted" and m.type == "out_invoice"):
            if not all([move.journal_id.cai, move.journal_id.prefix, move.journal_id.authorized_range_from,
                        move.journal_id.authorized_range_to, move.journal_id.issue_limit_date]):
                raise MissingError("CAI, Prefix, Issue Limit Date, or Authorized Range fields are not set in Journal")

            if fields.Date.context_today(self) > move.journal_id.issue_limit_date:
                raise ValidationError("Invoice issue limit date of %s is exceeded!" % move.journal_id.issue_limit_date)

            prefix = move.journal_id.prefix
            padding = move.journal_id.sequence_id.padding
            lower_limit = prefix + str(move.journal_id.authorized_range_from).zfill(padding)
            upper_limit = prefix + str(move.journal_id.authorized_range_to).zfill(padding)
            current_number = int(move.name.replace(prefix, ""))
            if move.journal_id.authorized_range_from > current_number or current_number > move.journal_id.authorized_range_to:
               raise ValidationError("Invoice number %s is outside of range (%s, %s)" % (move.name, lower_limit, upper_limit))
            move.cai = move.journal_id.cai
            move.authorized_range_from = lower_limit
            move.authorized_range_to = upper_limit
            move.issue_limit_date = move.journal_id.issue_limit_date

            warning_limit = prefix + str(move.journal_id.authorized_range_warning).zfill(padding)
            if move.name == warning_limit:
                self.env.ref("honduras_invoices.account_journal_mail_template_authorized_range_warn").send_mail(move.journal_id.id)

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    prefix = fields.Char("Prefix")
    is_honduras_invoice = fields.Boolean()
    authorized_range_from = fields.Integer("Authorized Range From")
    authorized_range_to = fields.Integer("Authorized Range To")
    cai = fields.Char("CAI")
    issue_limit_date = fields.Date("Issue Limit Date")
    authorized_range_warning = fields.Integer("Authorized Range Warning")
    issue_limit_date_warning = fields.Date("Issue Limit Warning Date")

    def write(self, values):
        for record in self:

            sequence_write = {}

            if "prefix" in values:
                sequence_write["prefix"] = values["prefix"]

            if "authorized_range_from" in values:
                sequence_write["number_next"] = values["authorized_range_from"]

            sequence_write["use_date_range"] = False

            if sequence_write:
                self.sequence_id.write(sequence_write)

            if ("is_honduras_invoice" in values and values["is_honduras_invoice"]) or ("is_honduras_invoice" not in values and record.is_honduras_invoice):
                # Check for every new field
                
                prefix                = values["prefix"] if "prefix" in values else record.prefix
                authorized_range_from = values["authorized_range_from"] if "authorized_range_from" in values else record.authorized_range_from
                authorized_range_to   = values["authorized_range_to"] if "authorized_range_to" in values else record.authorized_range_to
                cai                   = values["cai"] if "cai" in values else record.cai
                issue_limit_date      = values["issue_limit_date"] if "issue_limit_date" in values else record.issue_limit_date 
                
                if not prefix:
                    raise UserError(_('Prefix is not set'))
                if not authorized_range_from:
                    raise UserError(_('Authorized range from is not set'))
                if not authorized_range_to:
                    raise UserError(_('Authorized range to is not set'))
                if not cai:
                    raise UserError(_('CAI is not set'))
                if not issue_limit_date:
                    raise UserError(_('Issue limit date is not set'))
        return super().write(values)

    @api.onchange("prefix")
    def _onchange_prefix(self):
        for record in self:
            record.sequence_id.prefix = record.prefix

    @api.onchange("authorized_range_from")
    def _onchange_prefix(self):
        for record in self:
            record.sequence_id.number_next = record.authorized_range_from

    @api.onchange("authorized_range_to")
    def _onchange_prefix(self):
        pass
#        Maybe we can do something like this?.
#        for record in self:
#            record.sequence_id.max_numnber = record.authorized_range_to
