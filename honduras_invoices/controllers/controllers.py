# -*- coding: utf-8 -*-
# from odoo import http


# class AdventistasReports(http.Controller):
#     @http.route('/adventistas_reports/adventistas_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/adventistas_reports/adventistas_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('adventistas_reports.listing', {
#             'root': '/adventistas_reports/adventistas_reports',
#             'objects': http.request.env['adventistas_reports.adventistas_reports'].search([]),
#         })

#     @http.route('/adventistas_reports/adventistas_reports/objects/<model("adventistas_reports.adventistas_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('adventistas_reports.object', {
#             'object': obj
#         })
