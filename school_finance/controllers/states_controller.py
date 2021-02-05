# -*- coding: utf-8 -*-

from odoo import http

import json


class StateController(http.Controller):
    """ Its a controller to allow some really good things """

    # TODO: We need to change this route, add cors and change method name
    @http.route("/admission/states", auth="public", methods=["GET"])
    def get_states(self, **kw):
        """ This return some invoices """

        # Codigo para filtrar por el districtCode que llega en la URL. Solo queremos las facturas de ese districtCode
        # crea una variable con el modelo desde donde se va a tomar la información:'res.company'
        #

        distCod = False

        compania = http.request.env['res.company']
        # filtro del modelo basados en parametros de la url.
        search_compania = [("x_district_code", "=", (kw['dist']))]
        # Buscamos informacion en el modelo con el filtro definido
        compania_record = compania.search(search_compania)
        # Obtenemos los registros con los datos que buscamos. Solo recogemos los campos definidos a continuacion
        compania_values = compania_record.read(["id"])
        # Sacamos el valor del districtCode. Lo guardamos para usarlo en el siguiente filtro
        for com in compania_values:
            distCod = com["id"]

        # Codigo para filtrar por el facts Id que llega en la URL. Solo queremos las facturas de esa persona
        # crea una variable con el modelo desde donde se va a tomar la información:'res.partner'

        # 7/24/2020 It isn't used
        # idFacts = http.request.env['res.partner']

        # filtro del modelo basados en parametros de la url.

        # 7/24/2020 It isn't used
        # search_idFacts = [("facts_id", "=", kw['idF'])] if "idF" in kw else []

        # Buscamos informacion en el modelo con el filtro definido

        # 7/24/2020 It isn't used
        # idFacts_record = idFacts.search(search_idFacts)

        # Obtenemos los registros con los datos que buscamos. Solo recogemos los campos definidos a continuacion

        # 7/24/2020 It isn't used
        # idFacts_values = idFacts_record.read(["id"])

        # Sacamos el valor del districtCode. Lo guardamos para usarlo en el siguiente filtro

        # 7/24/2020 It isn't used
        # for ids in idFacts_values:
        #     facts = ids["id"]

        # Por cada factura buscamos todos los datos que tiene asignados:
        # crea una variable con el modelo desde donde se va a tomar la información:'account.move'
        facturas = http.request.env['account.move']

        # filtro del modelo basados en parametros de la url. Filtramos por el districtCode
        # Recogemos el parametro id de odoo o el id de facts.Este codigo es para el id de facts.
        #        search_facturas = [("company_id","=",distCod),("partner_id","=",facts)] #if "id" in kw else []
        # Si usamos el id de odoo ponemos este codigo
        search_facturas = [("company_id", "=", distCod), ("partner_id", "=", int(kw['id']))] if "id" in kw else []

        # Buscamos informacion en el modelo con el filtro definido
        facturas_record = facturas.search(search_facturas)

        # Obtenemos los registros con los datos que buscamos. Solo recogemos los campos definidos a continuacion
        facturas_values = facturas_record.read(
            ["partner_id", "ref", "student_id", "family_id", "invoice_date", "invoice_payment_term_id", "journal_id",
             "company_id", "access_token",
             "amount_untaxed", "amount_by_group", "amount_total", "invoice_line_ids", "line_ids"])

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
            datosLinea_record = datosLinea.search(search_domain_linea)

            # Obtienes la información basada en los ids anteriores y tomando en cuenta
            # los campos definifos en la funcion posterior
            datosLinea_values = datosLinea_record.read(
                ["product_id", "quantity", "price_unit", "discount", "analytic_tag_ids", "subscription_id",
                 "account_id", "tax_ids",
                 "analytic_account_id", "name"])

            record["datos"] = datosLinea_values

        return json.dumps(facturas_values)
