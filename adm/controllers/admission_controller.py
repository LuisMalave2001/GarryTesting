# -*- coding: utf-8 -*-

from odoo import http, SUPERUSER_ID, api
from odoo.http import request
from odoo.addons.adm.models.application.admission_application \
    import Application
from odoo.addons.base.models.res_users import Users


class AdmissionController(http.Controller):

    @staticmethod
    def _get_values_for_selection_fields(model_name: str, field_name: str):
        field_selection_type = request.env[model_name]._fields[field_name]
        return [{
            'name': name,
            'value': value
            } for value, name in field_selection_type.selection]

    def compute_view_render_params(self, application_id: Application):
        application_id = application_id.sudo()
        sudo_env = api.Environment(request.env.cr, SUPERUSER_ID, request.env.context)

        # relationship_types = (AdmissionController
        #                       ._get_values_for_selection_fields(
        #                             'adm.relationship', 'relationship_type'))

        relationship_types = request.env['school_base.relationship_type'].sudo().search([])

        marital_status_types = (AdmissionController
                                ._get_values_for_selection_fields(
                                        'res.partner', 'marital_status'))

        # custody_types = (AdmissionController
        #                           ._get_values_for_selection_fields(
        #                             'adm.relationship', 'custody'))

        applying_semester_values = (AdmissionController
                                    ._get_values_for_selection_fields(
                                            'adm.application', 'applying_semester'))

        contact_id = AdmissionController.get_user().partner_id
        contact_time_ids = request.env["adm.contact_time"].search([])
        degree_program_ids = request.env["adm.degree_program"].search([])

        gender_ids = request.env['adm.gender'].search([])
        application_status_ids = (request.env["adm.application.status"]
                                  .search([]))

        grade_level_ids = (request.env['school_base.grade_level'].sudo()
                           .search([('active_admissions', '=', True)]))
        school_year_ids = (request.env['school_base.school_year'].sudo()
                           .search([('active_admissions', '=', True)]))

        language_ids = http.request.env['adm.language'].search([])
        language_level_ids = request.env['adm.language.level'].search([])

        country_ids = request.env['res.country'].search([])
        state_ids = request.env['res.country.state'].search([])

        return {
            "country_ids": country_ids,
            "state_ids": state_ids,
            'contact_id': contact_id,
            'application_id': application_id,
            'application_status_ids': application_status_ids,
            'language_ids': language_ids.ids,
            'language_level_ids': language_level_ids.ids,
            'contact_time_ids': contact_time_ids,
            "gender_ids": gender_ids,
            'degree_program_ids': degree_program_ids,
            'current_url': request.httprequest.full_path,
            "showPendingInformation": False,
            'grade_level_ids': grade_level_ids,
            'applying_semester_values': applying_semester_values,
            'school_year_ids': school_year_ids,
            'relationship_types': relationship_types,
            'marital_status_types': marital_status_types,
            'user_env': request.env,
            'sudo_env': sudo_env,
            }

    @staticmethod
    def get_user() -> Users:
        return request.env.user

    @staticmethod
    def get_parameters():
        return request.httprequest.args

    @staticmethod
    def post_parameters():
        return request.httprequest.form

    @staticmethod
    def _parse_json_to_odoo_fields(model_env, json_request: dict):
        json_to_build = {}

        for field, value in json_request.items():
            value_to_json = False
            if isinstance(value, list):
                if value:
                    rel_model_env = request.env[
                        model_env._fields[field].comodel_name].sudo()
                    parsed_vals = [(5, 0, 0)]
                    for val_array in value:
                        if 'id' not in val_array or not val_array['id']:
                            parsed_vals.append((0, 0,
                                                AdmissionController
                                                ._parse_json_to_odoo_fields(
                                                    rel_model_env, val_array)))
                        else:
                            rel_id = val_array.pop('id')
                            parsed_vals.append((4, rel_id, False))
                            if len(val_array.keys()):
                                rel_model_env.browse(rel_id).write(
                                    AdmissionController
                                    ._parse_json_to_odoo_fields(rel_model_env,
                                                                val_array))
                    value_to_json = parsed_vals
            elif isinstance(value, dict):
                model_name = model_env._fields[field].comodel_name
                rel_model_env = request.env[model_name].sudo()

                if 'id' not in value or not value['id']:
                    if len(model_env) == 1 and model_name == 'ir.attachment':
                        attachment_id = model_env.env[
                            'ir.attachment'].sudo().create({
                                'name': value['name'],
                                'datas': value['base64_encoded_file'],
                                'mimetype': value['content_type'],
                                'res_id': model_env.id,
                                'res_model': model_env._name,
                                'type': 'binary',
                                })
                        rel_id = attachment_id.id
                    else:
                        rel_id = rel_model_env.create(
                            AdmissionController._parse_json_to_odoo_fields(
                                rel_model_env, value)).id
                else:
                    rel_id = value.pop('id')

                    for aux_field in value:
                        if hasattr(rel_model_env._fields[aux_field],
                                   'comodel_name'):
                            if rel_model_env._fields[aux_field]\
                                    .comodel_name == 'ir.attachment':
                                attachment_dict = value.pop(aux_field)
                                # noinspection PyUnresolvedReferences

                                attachment_vals = {
                                    'name': attachment_dict['name'],
                                    'datas': attachment_dict[
                                        'base64_encoded_file'],
                                    'mimetype': attachment_dict[
                                        'content_type'],
                                    'res_id': rel_id,
                                    'res_model': model_name,
                                    'type': 'binary',
                                    }

                                attachment_id = (rel_model_env
                                                 .env['ir.attachment']
                                                 .create(attachment_vals))
                                value[aux_field] = attachment_id.id

                    if len(value.keys()):
                        rel_model_env.browse(rel_id).write(
                            AdmissionController._parse_json_to_odoo_fields(
                                rel_model_env, value))
                value_to_json = rel_id
            else:
                if not value:
                    value = False
                value_to_json = value
            json_to_build[field] = value_to_json

        return json_to_build

    # noinspection PyUnusedLocal
    @http.route("/admission/applications/"
                "<model(adm.application):application_id>/", auth="public",
                methods=["PUT"], csrf=True, type='json')
    def update_application_with_json(self, application_id, **params):
        """ This is a JSON controller, this get a JSON and write
        the application with it, that's all
        """
        json_request = request.jsonrequest

        if not json_request.get('family_id', False) or application_id.family_id:
            json_request["family_id"] = application_id.sudo().responsible_user_id.partner_id.family_ids[0].id

        application_id = application_id.with_context({'default_family_id': json_request["family_id"]}).sudo()
        write_vals = self._parse_json_to_odoo_fields(application_id,
                                                     json_request)
        application_id.sudo().write(write_vals)
