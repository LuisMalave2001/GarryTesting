# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountReport(models.AbstractModel):
    _inherit = "account.report"

    @api.model
    def _init_filter_analytic(self, options, previous_options=None):
        super(AccountReport, self)._init_filter_analytic(options, previous_options)
        if not self.filter_analytic:
            return

        options["accounts"] = previous_options and previous_options.get("accounts") or []
        account_ids = [int(acc) for acc in options["accounts"]]
        selected_accounts = account_ids \
                            and self.env["account.account"].browse(account_ids) \
                            or self.env["account.account"]
        options["selected_account_names"] = selected_accounts.mapped("name")
    
    @api.model
    def _get_options_analytic_domain(self, options):
        domain = super(AccountReport, self)._get_options_analytic_domain(options)
        if options.get("accounts"):
            account_ids = [int(acc) for acc in options["accounts"]]
            domain.append(("account_id", "in", account_ids))
        return domain
    
    def _set_context(self, options):
        ctx = super(AccountReport, self)._set_context(options)
        if options.get("accounts"):
            ctx["account_ids"] = self.env["account.account"].browse([int(acc) for acc in options["accounts"]])
        return ctx
    
    def get_report_informations(self, options):
        info = super(AccountReport, self).get_report_informations(options)
        options = options or self._get_options(options)
        if options.get("accounts") is not None:
            info["options"]["selected_account_names"] = [self.env["account.account"].browse(int(account)).name for account in options["accounts"]]
        return info
