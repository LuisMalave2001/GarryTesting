
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request


class AdmissionPortal(CustomerPortal):

    def _prepare_home_portal_values(self):
        values = super(AdmissionPortal, self)._prepare_home_portal_values()

        values.update({
            'application_count': len(request.env.user.application_ids)
            })
        return values
