# -*- coding: utf-8 -*-

from odoo import http, exceptions

import json

import logging

logger = logging.getLogger(__name__)


class FactsAccountController(http.Controller):
    """ Web service for facts """

    @http.route("/account/getDataOdooFromFamilyID", auth="none", methods=["GET"], cors='*', csrf=False)
    def get_odoo_data_from_family_id(self, **kw):
        """ metodo encargado de recuperar datos de una factura y enviarla a FACTS # definiendo la url desde donde va
        ser posible acceder, tipo de metodo, cors para habiltiar accesos a ip externas. """

        logger.info("getDataOdooFromFamilyID, parameters: %s" % kw)

        # Codigo para filtrar por el districtCode que llega en la URL. Solo queremos las facturas de ese districtCode
        # crea una variable con el modelo desde donde se va a tomar la información:'res.company'

        company_district_code = kw['dist'] if "dist" in kw else '-1'
        family_facts_id = kw['idF'] if "idF" in kw else -1

        company_env = http.request.env['res.company']
        partner_env = http.request.env['res.partner']

        # filtro del modelo basados en parametros de la url. ilike como el like pero no diferencia mayusculas de
        # minisculas. Buscamos informacion en el modelo con el filtro definido. Con sudo() entramos como administradores
        company_id = company_env.sudo().search([("district_code_name", "ilike", company_district_code)])

        # Sacamos el valor del districtCode. Lo guardamos para usarlo en el siguiente filtro
        family_domain = [("facts_id", "=", family_facts_id)]

        # Buscamos informacion en el modelo con el filtro definido
        family_id = partner_env.sudo().search(family_domain)

        if not company_id:
            raise exceptions.ValidationError("Company with district code [%s] not found!" % company_district_code)

        if not family_id:
            raise exceptions.ValidationError("Family with facts id [%s] not found!" % family_facts_id)

        facturas = http.request.env['account.move']

        # Buscamos informacion en el modelo con el filtro definido. Ordenamos por la fecha de la factura
        facturas_record = facturas.sudo().search([
            ("company_id", "=", company_id.id), ("state", "=", "posted"),
            ("family_id", "=", family_id.id)],
            order='invoice_date asc')

        # Obtenemos los registros con los datos que buscamos. Solo recogemos los campos definidos a continuacion
        facturas_values = facturas_record.read(
            ["name", "state", "partner_id", "ref", "student_id", "family_id", "invoice_date", "invoice_payment_term_id",
             "journal_id", "company_id", "access_token",
             "amount_untaxed", "amount_by_group", "amount_total", "amount_residual", "invoice_line_ids", "line_ids"])

        for record in facturas_values:
            if record["invoice_date"]:
                record["invoice_date"] = record["invoice_date"].strftime('%m/%d/%Y')
            else:
                record["invoice_date"] = ''

            record["datos"] = []

            # crea una variable con el modelo desde donde se va a tomar la información
            datosLinea = http.request.env['account.move.line']
            # filtro del modelo basados en parametros de la url
            search_domain_linea = [("move_id", "=", record["id"])]
            # Tomar informacion basado en el modelo y en el domain IDS
            datosLinea_record = datosLinea.sudo().search(search_domain_linea)
            # Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la
            # funcion posterior
            datosLinea_values = datosLinea_record.read(
                ["product_id", "quantity", "price_unit", "discount", "analytic_tag_ids",
                 "account_id", "tax_ids",
                 "analytic_account_id", "name"])

            record["datos"] = datosLinea_values
        return json.dumps(facturas_values)
