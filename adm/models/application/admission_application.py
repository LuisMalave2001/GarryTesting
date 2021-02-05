# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.addons.adm.utils import formatting
import base64
import datetime
from odoo.tools.safe_eval import safe_eval

status_types = [("stage", "Stage"),
                ("done", "Done"),
                ("return", "Return To Parents"),
                ("started", "Application Started"),
                ("submitted", "Submitted"),
                ("cancelled", "Cancelled")]


class Questions(models.Model):
    _name = 'adm.application.question'
    _description = "Application question"

    question = fields.Char(string="Question")
    answer = fields.Char(string="Answer")


class ApplicationStatus(models.Model):
    _name = 'adm.application.status'
    _description = "Application status"
    _order = "sequence"

    name = fields.Char(string="Status Name")
    description = fields.Text(string="Description")
    sequence = fields.Integer(readonly=True, default=-1)

    mail_template_id = fields.Many2one('mail.template', string='Email Template', domain=[('model', '=', 'adm.application')],
                                       help="If set an email will be sent to the customer when the application reaches this status")

    fold = fields.Boolean(string="Fold")
    type_id = fields.Selection(status_types, string="Type", default='stage')
    web_visible = fields.Boolean(string="Visible on web")
    web_alternative_name = fields.Char("Alternative name for web")
    hide_if_cancel = fields.Boolean(string="Hide if cancelled")
    hide_if_done = fields.Boolean(string="Hide if done")

    partner_id = fields.Many2one("res.partner", string="Customer")

    task_ids = fields.One2many("adm.application.task", "status_id", "Status Ids")

    @api.model
    def create(self, values):
        next_order = self.env['ir.sequence'].next_by_code('sequence.application.task')

        values['sequence'] = next_order
        return super().create(values)


class Gender(models.Model):
    _name = 'adm.gender'
    _description = "Admission Gender"

    name = fields.Char("Gender")


class Application(models.Model):
    _name = "adm.application"
    _description = "Admission Application"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _read_group_status_ids(self, stages, domain, order):
        status_ids = self.env['adm.application.status'].search([])
        return status_ids

    # Admission Information
    preferred_degree_program = fields.Many2one("adm.degree_program", string="Preferred Degree Program")

    # Demographic
    name = fields.Char(string="Name", related="partner_id.name")
    first_name = fields.Char(string="First Name", related="partner_id.first_name")
    middle_name = fields.Char(string="Middle Name", related="partner_id.middle_name")
    last_name = fields.Char(string="Last Name", related="partner_id.last_name")
    date_of_birth = fields.Date(string="Date of birth", related="partner_id.date_of_birth")
    identification = fields.Char(string="Identification", related="partner_id.identification")
    birth_country = fields.Many2one("res.country", string="Birth Country", related="partner_id.country_id")
    birth_city = fields.Char("Birth City", related="partner_id.city")
    gender = fields.Many2one("adm.gender", string="Gender", related="partner_id.gender", inverse="_set_gender")
    status_history_ids = fields.One2many('adm.application.history.status', 'application_id', string="Status history")
    last_time_submitted = fields.Datetime(compute='_compute_last_time_submitted', store=True)
    family_id = fields.Many2one('res.partner', domain="[('is_family', '=', True)]", required=True)

    finish_datetime = fields.Datetime(compute='_compute_finish_date', store=True)
    finish_timeline = fields.Float(compute='_compute_finish_date', store=True)

    responsible_user_id = fields.Many2one('res.users', required=True)

    responsible_user_kanban_ids = fields.Many2many(
        'res.users',
        compute="compute_responsible_user_kanban",
        string="Responsible User")

    is_current_school_year = fields.Boolean(string="Current school year", compute='_compute_current_school_year', search='_search_current_school_year')

    def compute_responsible_user_kanban(self):
        for application_id in self:
            application_id.responsible_user_kanban_ids = application_id.responsible_user_id

    assigned_user_id = fields.Many2one('res.users')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        a = 0
        return res

    def _search_current_school_year(self, operator, value):
        current_school_year_id = int(self.env['ir.config_parameter'].sudo().get_param('adm.adm_current_school_year', False))
        current_school_year = self.env['school_base.school_year'].browse(current_school_year_id)

        if value:
            operator = '='
        else:
            operator = '!='

        return [('school_year', operator, current_school_year.id)]

    def _compute_current_school_year(self):
        for application_id in self:
            current_school_year_id = int(self.env['ir.config_parameter'].sudo().get_param('adm.adm_current_school_year', False))
            current_school_year = self.env['school_base.school_year'].browse(current_school_year_id)
            application_id.is_current_school_year = (application_id.school_year
                                                     or current_school_year
                                                     or application_id.school_year == current_school_year)


    @api.depends('status_history_ids')
    def _compute_last_time_submitted(self):
        for application_id in self:
            submitted_status = application_id.status_history_ids.filtered(lambda sh: sh.status_id.type_id == 'submitted')[:1]
            application_id.last_time_submitted = submitted_status.timestamp

    @api.depends('status_id', 'status_id.type_id')
    def _compute_finish_date(self):
        for application_id in self:
            if application_id.status_id.type_id == 'done':

                now = datetime.datetime.now()
                diff = now - application_id.create_date

                application_id.finish_datetime = now
                # application_id.finish_timeline = diff
                application_id.finish_timeline = 0

    def _set_gender(self):
        for application_id in self:
            application_id.partner_id.gender = self.gender

    def _set_family_id(self):
        for application_id in self:
            application_id.family_id = application_id.family_id

    father_name = fields.Char("Father name")
    mother_name = fields.Char("Mother name")

    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'adm.application')], string='Attachments')

    # Contact
    email = fields.Char(string="Email", related="partner_id.email", index=True)
    phone = fields.Char(string="Phone", related="partner_id.mobile")
    home_phone = fields.Char(string="Home phone", related="partner_id.phone")
    other_contacts_ids = fields.One2many("adm.application.other_contacts", "application_id", string="Other Contacts")
    citizenship = fields.Many2one("res.country", string="Citizenship")
    language_spoken = fields.Many2one("adm.language", string="Language Spoken")
    image = fields.Binary("Applicant´s Photo", related="partner_id.image_1920")
    # School
    current_school = fields.Char(string="Current School")
    current_school_address = fields.Char(string="Current School Address")

    grade_level = fields.Many2one("school_base.grade_level", string="Grade Level", domain=[('active_admissions', '=', True)])
    grade_level_type = fields.Selection(related="grade_level.user_type_id.type")
    grade_level_inquiry = fields.Many2one(string="GradeLevel", related="inquiry_id.grade_level_id")
    school_year = fields.Many2one("school_base.school_year", string="School Year")

    previous_school = fields.Char(string="Previous School")
    previous_school_address = fields.Char(string="Previous School Address")

    gpa = fields.Float("GPA")
    cumulative_grades = fields.Float("Cumulative Grade")
    regional_exam_grade = fields.Float("Regional Grade")
    bac_grade = fields.Float("BAC Grade")

    # Skills
    language_ids = fields.One2many("adm.application.language",
                                   "application_id", string="Languages",
                                   kwargs={"website_form_blacklisted": False})

    # Location
    country_id = fields.Many2one("res.country",
                                 related="partner_id.country_id",
                                 string="Country")
    state_id = fields.Many2one("res.country.state",
                               related="partner_id.state_id", string="State")
    city = fields.Char(string="City", related="partner_id.city")
    street = fields.Char(string="Street Address", related="partner_id.street")
    zip = fields.Char("zip", related="partner_id.zip")

    # Relationships
    relationship_ids = fields.One2many(string="Relationship",
                                       related="partner_id.relationship_ids",
                                       readonly=False)
    custodial_relationship_ids = fields.Many2many('school_base.relationship',
                                                  string="Custodials",
                                                  compute="compute_custodials",
                                                  store=False,
                                                  )

    @api.depends('relationship_ids', 'relationship_ids.custody')
    def compute_custodials(self):
        for application_id in self:
            application_id.custodial_relationship_ids = (
                application_id.relationship_ids.filtered('custody'))

    # Documentation
    letter_of_motivation_id = fields.Many2one("ir.attachment",
                                              string="Letter of motivation")
    cv_id = fields.Many2one("ir.attachment", string="C.V")
    grade_transcript_id = fields.Many2one("ir.attachment",
                                          string="Grade transcript")
    letters_of_recommendation_id = fields.Many2one(
        "ir.attachment", string="Letter of recommendation")

    # Additional student info
    resident_status = fields.Selection([('permanent', 'Permanent'),
                                        ('transient', 'Transient'),
                                        ],
                                       string="Resident status")
    resident_length_of_stay = fields.Char("Length of stay")

    # languages level
    languages_levels = [("beginner", "Beginner"), ("elementary", "Elementary"), ("intermediate", "Intermediate"), ("advanced", "Advanced"), ("fluent", "Fluent")]
    first_level_language = fields.Selection(languages_levels, string="Level", default='beginner')
    second_level_language = fields.Selection(languages_levels, string="Level", default='beginner')
    third_level_language = fields.Selection(languages_levels, string="Level", default='beginner')

    number_years_in_english = fields.Char("Years in English")
    additional_info_other = fields.Char("Other")

    special_education = fields.Boolean("Special Education")
    special_education_desc = fields.Text("Special Education Description")

    psycho_educational_testing = fields.Boolean("Psycho educational testing")

    emotional_support = fields.Boolean("Emotional support")
    emotional_support_desc = fields.Text("Emotional support description")

    iep_education = fields.Boolean("IEP Education")

    # Previous School
    previous_school_ids = fields.One2many("adm.previous_school_description", "application_id")

    # houses
    house_address_ids = fields.One2many(related="family_id.house_address_ids", string="House addresses")

    # References
    isp_community_reference_1 = fields.Char("ISP Community Reference #1")
    isp_community_reference_2 = fields.Char("ISP Community Reference #2")

    personal_reference_contact_information_1 = fields.Char("Personal Reference #1 Contact Information:")
    personal_reference_name_1 = fields.Char("Personal Reference #1 Name")

    personal_reference_contact_information_2 = fields.Char("Personal Reference #2 Contact Information:")
    personal_reference_name_2 = fields.Char("Personal Reference #2 Name")

    # Medical information
    doctor_name = fields.Char("Doctor name")
    doctor_phone = fields.Char("Doctor phone")
    doctor_address = fields.Char("Doctor Direction")
    hospital = fields.Char("Hospital")
    hospital_address = fields.Char("Hospital Address")
    permission_to_treat = fields.Boolean("Permission To Treat")
    blood_type = fields.Char("Blood Type")
    medical_allergies_ids = fields.One2many(string="Allergies", related="partner_id.medical_allergies_ids", readonly=False)
    medical_conditions_ids = fields.One2many(string="Conditions", related="partner_id.medical_conditions_ids", readonly=False)
    medical_medications_ids = fields.One2many(string="Medications", related="partner_id.medical_medications_ids", readonly=False)

    # Meta
    contact_time_id = fields.Many2one("adm.contact_time", string="Preferred contact time")

    partner_id = fields.Many2one("res.partner", string="Contact")
    status_id = fields.Many2one("adm.application.status", string="Status", group_expand="_read_group_status_ids")
    task_ids = fields.Many2many("adm.application.task")

    inquiry_id = fields.Many2one("adm.inquiry")

    state_tasks = fields.One2many(string="State task", related="status_id.task_ids")

    status_type = fields.Selection(string="Status Type", related="status_id.type_id")
    forcing = False

    # QUESTION CUSTOMIZED PREESCOLAR
    applying_semester = fields.Selection([
        ('semester_1', 'Semester 1 (August)'),
        ('semester_2', 'Semester 2 (January)'),
        ('immediate', 'Immediate'),
        ],
        string="Applying semester")

    # HERMANOS INFORMATION
    sibling_ids = fields.One2many("adm.application.sibling", "application_id", "Siblings")

    # Files
    passport_file_ids = fields.Many2many('ir.attachment', 'application_passport_id')
    residency_file_ids = fields.Many2many('ir.attachment', 'application_residency_id')

    residency_permit_id_number = fields.Many2one('ir.attachment')
    parent_passport_upload = fields.Many2one('ir.attachment')

    required_fields_completed = fields.Integer(string="Required fields completed", compute="_compute_application_fields")
    optional_fields_completed = fields.Integer(string="Optional fields completed", compute="_compute_application_fields")
    fields_completed = fields.Float(string="Fields completed", compute="_compute_application_fields")

    total_required_fields_completed = fields.Float(string="Total required fields completed", compute="_compute_application_fields")
    total_optional_fields_completed = fields.Float(string="Total optional fields completed", compute="_compute_application_fields")
    total_fields_completed = fields.Float(string="Total fields completed", compute="_compute_application_fields")

    # Signature
    signature_attach_url = fields.Char("Signature Attachment URL")
    signature_person_name = fields.Char()
    signature_agreements = fields.Boolean(string="Signature agreements")
    check_confidential_info_adm_file = fields.Boolean(string="Rights to access confidential information contained in applicant's admission file.")

    signature_date = fields.Date()

    def _compute_application_fields(self):
        for application_id in self:

            config_parameter = self.env['ir.config_parameter'].sudo()
            application_required_fields_str = config_parameter.get_param('adm_application_required_field_ids', '')
            application_required_fields = [int(e) for e in application_required_fields_str.split(',') if e.isdigit()]

            if application_required_fields:
                required_field_ids = self.env['adm.fields.settings'].sudo().browse(application_required_fields)
                filtered_required_fields_ids = self.env['adm.fields.settings'].sudo()
                for required_field_id in required_field_ids:
                    field_domain = safe_eval(required_field_id.domain or '[]')
                    if application_id.filtered_domain(field_domain):
                        filtered_required_fields_ids += required_field_id

                application_id.required_fields_completed = sum(filtered_required_fields_ids.mapped(lambda f: not not application_id[f.name]))
                if filtered_required_fields_ids:
                    application_id.total_required_fields_completed = application_id.required_fields_completed * 100 / len(filtered_required_fields_ids)
                else:
                    application_id.total_required_fields_completed = 0
            else:
                application_id.required_fields_completed = 0
                application_id.total_required_fields_completed = 0

            application_optional_fields_str = config_parameter.get_param('adm_application_optional_field_ids', '')
            application_optional_fields = [int(e) for e in application_optional_fields_str.split(',') if e.isdigit()]

            if application_optional_fields:
                optional_field_ids = self.env['adm.fields.settings'].sudo().browse(application_optional_fields)
                filtered_optional_field_ids = self.env['adm.fields.settings'].sudo()
                for required_field_id in optional_field_ids:
                    field_domain = safe_eval(required_field_id.domain or '[]')
                    if application_id.filtered_domain(field_domain):
                        filtered_optional_field_ids += optional_field_ids
                application_id.optional_fields_completed = sum(filtered_optional_field_ids.mapped(lambda f: not not application_id[f.name]))
                if filtered_optional_field_ids:
                    application_id.total_optional_fields_completed = application_id.optional_fields_completed * 100 / len(filtered_optional_field_ids)
                else:
                    application_id.total_optional_fields_completed = 0
            else:
                application_id.optional_fields_completed = 0
                application_id.total_optional_fields_completed = 0

            # Required fields first
            application_id.fields_completed = application_id.required_fields_completed + application_id.optional_fields_completed
            if application_optional_fields and application_required_fields:
                application_id.total_fields_completed = (application_id.fields_completed * 100) / (len(application_optional_fields) + len(application_required_fields))
            else:
                application_id.total_fields_completed = 0

    def message_get_suggested_recipients(self):
        recipients = super().message_get_suggested_recipients()
        try:
            for inquiry in self:
                if inquiry.email:
                    inquiry._message_add_suggested_recipient(recipients, partner=self.partner_id, email=inquiry.email, reason=_('Custom Email Luis'))
        except exceptions.AccessError:  # no read access rights -> just ignore suggested recipients because this imply modifying followers
            pass
        return recipients

    def force_back(self):
        status_ids_ordered = self.env['adm.application.status'].search([], order="sequence")
        index = 0
        for status in status_ids_ordered:
            if status == self.status_id:
                break
            index += 1

        index -= 1
        if index >= 0:
            next_status = status_ids_ordered[index]
            self.with_context({
                'forcing': True
                }).status_id = next_status

    def print_default(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/report/html/adm.report_default/' + str(self.id),
            'target': '_blank',
            'res_id': self.id,
            }

    def print_custom(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/report/html/adm.report_custom/' + str(self.id),
            'target': '_blank',
            'res_id': self.id,
            }

    # GENERATE THE INTERNAL REPORT AND WILL SAVE INT ATTACHMENT OF THE APPLICATION
    def generate_internal_report(self):
        AttachmentEnv = self.env["ir.attachment"]
        REPORT_ID = 'adm.report_internal_custom'
        pdf = self.env.ref(REPORT_ID).render_qweb_pdf(self.ids)
        # pdf result is a list
        b64_pdf = base64.b64encode(pdf[0])
        # save pdf as attachment
        # requests.session = request.session

        file_id = AttachmentEnv.sudo().create({
            'name': 'Internal Report',  # 'datas_fname': upload_file.filename,
            'res_name': 'reportInternal.pdf',
            'type': 'binary',
            'res_model': 'adm.application',
            'res_id': self.id,
            'datas': b64_pdf,
            # 'datas': base64.b64encode(urlopen('/report/html/adm.report_internal_custom/'+str(self.id)).read()),
            # 'datas': base64.b64encode(s.get(url).content),
            })

        return {
            'type': 'ir.actions.act_url',
            'url': '/report/html/adm.report_custom/' + str(self.id),
            'target': '_blank',
            'res_id': self.id,
            }

    def force_next(self):
        status_ids_ordered = self.env['adm.application.status'].sudo().search([], order="sequence")
        index = 0
        for status in status_ids_ordered:
            if status == self.status_id:
                break
            index += 1

        index += 1
        if index < len(status_ids_ordered):
            next_status = status_ids_ordered[index]
            self.with_context({
                'forcing': True
                }).status_id = next_status

    def force_status_submitted(self, next_status_id):
        self.with_context({
            'forcing': True
            }).status_id = next_status_id

    def move_to_next_status(self):
        self.forcing = False
        status_ids_ordered = self.env['adm.application.status'].search([], order="sequence")
        index = 0
        for status in status_ids_ordered:
            if status == self.status_id:
                # print("Encontrado! -> {}".format(index))
                break
            index += 1

        index += 1
        if index < len(status_ids_ordered):
            next_status = status_ids_ordered[index]

            if self.status_id.type_id == 'done':
                raise exceptions.except_orm(_('Application completed'), _('The Application is already done'))
            elif self.status_id.type_id == 'cancelled':
                raise exceptions.except_orm(_('Application cancelled'), _('The Application cancelled'))
            else:
                self.status_id = next_status

    def cancel(self):
        status_ids_ordered = self.env['adm.application.status'].search([], order="sequence")
        for status in status_ids_ordered:
            if status.type_id == 'cancelled':
                self.status_id = status
                break

    @api.depends("first_name", "middle_name", "last_name")
    def _compute_name(self):
        for record in self:
            record.name = formatting.format_name(record.first_name, record.middle_name, record.last_name)
            record.partner_id.first_name = record.first_name

    @api.depends("first_name", "middle_name", "last_name")
    def _update_contact(self):
        for record in self:
            record.partner_id.first_name = record.first_name

    @api.onchange("first_name", "middle_name", "last_name")
    def _set_full_name(self):
        self.name = formatting.format_name(self.first_name, self.middle_name, self.last_name)

    @api.onchange("country_id")
    def _onchange_country_id(self):
        res = {}
        if self.country_id:
            res['domain'] = {
                'state_id': [('country_id', '=', self.country_id.id)]
                }

    @api.model
    def create(self, values):

        if not values.get('status_id', False):
            status_id = self.env['adm.application.status'].search([], order="sequence")[0]
            values['status_id'] = status_id.id
        else:
            status_id = self.env['adm.application.status'].browse(values['status_id'])
        # values['name'] = formatting.format_name(values['first_name'],
        # values['middle_name'], values['last_name'])
        application_id = super(Application, self).create(values)

        message = _("Application created in [%s] status") % status_id.name
        timestamp = datetime.datetime.now()

        self.env['adm.application.history.status'].sudo().create({
            'note': message,
            'timestamp': timestamp,
            'application_id': application_id.id,
            'status_id': status_id.id,
            })

        if status_id.mail_template_id:
            application_id.message_post_with_template(template_id=status_id.mail_template_id.id, res_id=application_id.id)

        return application_id

    def write(self, values):

        for application_id in self:
            first_name = values.get('first_name', application_id.first_name)
            middle_name = values.get('middle_name', application_id.middle_name)
            last_name = values.get('last_name', application_id.last_name)

            # "related" in application_id.fields_get()["email"]
            # Se puede hacer totalmente dinamico, no lo hago ahora por falta de
            # tiempo
            # Pero sin embargo, es totalmente posible.
            # Los no related directamente no tiene related, y los que si son
            # tiene el campo related de la siguiente manera: (model, field)
            # fields = application_id.fields_get()
            partner_related_fields = {}
            partner_fields = ['email', 'phone', 'home_phone', 'country_id', 'state_id', 'city', 'street', 'zip', 'date_of_birth', 'identification']
            for partner_field in partner_fields:
                if partner_field in values:
                    partner_related_fields[partner_field] = values[partner_field]

            if "first_name" in values:
                partner_related_fields["first_name"] = first_name
            if "middle_name" in values:
                partner_related_fields["middle_name"] = middle_name
            if "last_name" in values:
                partner_related_fields["last_name"] = last_name

            application_id.sudo().partner_id.write(partner_related_fields)

            # PARA PONER VALOR POR DEFECTO
            # application_id._context.get('forcing', False):

            if values.get('status_id', False):

                next_status_id = application_id.env['adm.application.status'].browse(values['status_id'])

                message = _("From [%s] to [%s] status") % (application_id.status_id.name, next_status_id.name)
                timestamp = datetime.datetime.now()

                self.env['adm.application.history.status'].sudo().create({
                    'note': message,
                    'timestamp': timestamp,
                    'application_id': application_id.id,
                    'status_id': next_status_id.id,
                    })

                if next_status_id.mail_template_id:
                    application_id.message_post_with_template(template_id=next_status_id.mail_template_id.id, res_id=application_id.id)

                if not self._context.get('forcing', False):
                    if not application_id.state_tasks & application_id.task_ids == application_id.state_tasks and application_id:
                        raise exceptions.ValidationError("All task are not completed")
            else:
                self.forcing = False

        return super().write(values)


class ApplicationOtherContacts(models.Model):
    _name = 'adm.application.other_contacts'
    _description = "Application other contacts"

    contact_name = fields.Char("Contact Name")
    contact_identification = fields.Char("Contact Identification")

    application_id = fields.Many2one("adm.application", string="Application")


class ApplicationTasks(models.Model):
    _name = 'adm.application.task'
    _description = "Application Task"

    name = fields.Char("Name")
    description = fields.Char("Description")
    status_id = fields.Many2one("adm.application.status", string="Status")


class ApplicationSiblings(models.Model):
    _name = 'adm.application.sibling'
    _description = "Application sibling"

    partner_id = fields.Many2one('res.partner')

    name = fields.Char(related="partner_id.name")
    age = fields.Integer("Edad")

    school = fields.Char("School name")
    application_id = fields.Many2one("adm.application", "Application")
    grade_level_id = fields.Many2one('school_base.grade_level')
    alumni_state = fields.Selection([('alumni', 'Alumni'), ('currently_enrolled', 'Currently Enrolled')], 'Alumni or currently Enrolled Students')
    alumnus_enrolled_1 = fields.Char("Alumnus/Enrolled 1")
    alumnus_enrolled_name = fields.Char()
    relationship_to_application = fields.Char()
    years_attended = fields.Char()


class AdmissionApplicationLanguages(models.Model):
    _name = 'adm.application.language'
    _description = "Application language"

    language_id = fields.Many2one("adm.language", string="Language")
    language_level_id = fields.Many2one("adm.language.level", string="Language Level")
    application_id = fields.Many2one("adm.application", string="Application")
