# -*- coding: utf-8 -*-
import logging
from odoo import http
from datetime import datetime
import base64
import itertools
import re
import json
from odoo.http import content_disposition, dispatch_rpc, request, \
    serialize_exception as _serialize_exception, Response

_logger = logging.getLogger(__name__)


class ExternalLogin(http.Controller):
    @http.route("/admission/logging_from_facts", auth="public",
                methods=["GET"],
                website=True)
    def logging_from_facts(self, **params):
        if 'parent_email' in params and params['parent_email']:
            parent_email = params['parent_email']
            user_id = (request.env["res.users"].sudo()
                    .search([('email', '=ilike', parent_email)]))
            if user_id:

                request.session.uid = user_id.id
                request.session.login = parent_email
                request.params['login_success'] = True

        page = params.get('page', '')
        family_id = params.get('family_id', '')
        route = '/admission/%s?family_id=%s' % (page, family_id)

        return request.redirect(route)
