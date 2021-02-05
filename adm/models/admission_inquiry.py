# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.addons.crm.models import crm_stage
from ..utils import formatting

status_types = [
    ("stage", "Stage"),
    ("done", "Done"),
    ("cancelled", "Cancelled")
    ]


class StatusType(models.Model):
    _name = 'adm.inquiry.status.type'
    _description = "Inquiry Status Type"

    name = fields.Char(string="Status Name")


class Status(models.Model):
    _name = 'adm.inquiry.status'
    _description = "Inquiry Status"
    _order = "sequence"

    name = fields.Char(string="Status Name")
    description = fields.Text(string="Description")
    sequence = fields.Integer(readonly=True, default=-1)
    fold = fields.Boolean(string="Fold")
    # type_id = fields.Many2one("adm.inquiry.status.type",string="Type", required=True)
    # type_name = fields.Char(related="type_id.name", string="Type Name")

    type_id = fields.Selection(selection=status_types, string="Type", default="stage")

    task_ids = fields.One2many("adm.inquiry.task", "status_id", "Status Ids")


class ApplicationSource(models.Model):
    _name = "adm.inquiry.source"
    _order = "sequence"

    name = fields.Char(string="Name", translate=True)
    description = fields.Char("Description")
    other = fields.Boolean("Other")
    sequence = fields.Integer(readonly=True, default=-1)


class Inquiry(models.Model):
    _name = 'adm.inquiry'
    _description = "Inquiry"

    _inherit = ['mail.thread', 'mail.activity.mixin']
    _primary_email = ['email']

    @api.model
    def _read_group_status_ids(self, stages, domain, order):
        status_ids = self.env['adm.inquiry.status'].search([])
        return status_ids

    # Admission Information

    school_year_id = fields.Many2one("school_base.school_year", string="School Year")
    current_grade_level_id = fields.Many2one("school_base.grade_level", string="Current Grade Level")
    grade_level_id = fields.Many2one("school_base.grade_level", string="Grade Level", domain=[('active_admissions', '=', True)])
    responsible_id = fields.Many2many("res.partner")

    preferred_degree_program = fields.Many2one("adm.degree_program",
                                               string="Preferred Degree Program")

    # Demographic  Parent Base
    name = fields.Char(string="Name", default="Undefined", readonly=True)
    first_name = fields.Char(string="First Name", default="")
    middle_name = fields.Char(string="Middle Name", default="")
    last_name = fields.Char(string="Last Name", default="")
    date_of_birth = fields.Date(string="Date of birth")
    gender = fields.Many2one("adm.gender", string="Gender")

    # Contact Parent Base
    email = fields.Char(string="Email", related="partner_id.email", readonly=False)
    phone = fields.Char(string="Phone", related="partner_id.phone", readonly=False)

    community_street_address = fields.Char(string="Community residence address", default="", readonly=False)
    reference_family_1 = fields.Char(string="a) References Families", default="", readonly=False)
    reference_family_2 = fields.Char(string="b) References Families", default="", readonly=False)
    congregation_member = fields.Char("Congregation member", readonly=False)

    # School
    current_school = fields.Char(string="Current School")
    current_school_address = fields.Char(string="Current School Address")
    
    # Skills
    language_ids = fields.One2many("adm.inquiry.language", "inquiry_id",
                                    string="language")
    
    # Location
    country_id = fields.Many2one("res.country", related="partner_id.country_id",
                                  readonly=False, string="Country")
    state_id = fields.Many2one("res.country.state", readonly=False,
                                related="partner_id.state_id", string="State")
    city = fields.Char(string="City", readonly=False, related="partner_id.city")
    street = fields.Char(string="Street Address", readonly=False, related="partner_id.street")
    zip = fields.Char("zip", readonly=False, related="partner_id.zip")

    partner_id = fields.Many2one("res.partner", string="Contact")
    status_id = fields.Many2one("adm.inquiry.status", string="Status", 
                                group_expand="_read_group_status_ids")
    task_ids = fields.Many2many("adm.inquiry.task")

    state_tasks = fields.One2many(string="State task", related="status_id.task_ids")

    # status_type = fields.Char(string="Status Type", related="status_id.name")
    status_type = fields.Selection(string="Status Type", related="status_id.type_id")

    application_id = fields.Many2one("adm.application")
    forcing = False

    extra_service_ids = fields.Many2many(string="Extra Services",
                                         comodel_name="school_base.service")

    known_people_in_school = fields.Char(string="Known People in School")

    sources_id = fields.Many2one("adm.inquiry.source")
    source_other = fields.Char(string="Other Source")
    sources_id_other = fields.Boolean(string="sources_id_other", readonly=True, related="sources_id.other")

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
        status_ids_ordered = self.env['adm.inquiry.status'].search([], order="sequence")
        index = 0
        for status in status_ids_ordered:
            if status == self.status_id:
                break
            index += 1

        index -= 1
        if index >= 0:
            next_status = status_ids_ordered[index]
            self.forcing = True
            self.status_id = next_status

    def force_next(self):
        status_ids_ordered = self.env['adm.inquiry.status'].search([], order="sequence")
        index = 0
        for status in status_ids_ordered:
            if status == self.status_id:
                break
            index += 1

        index += 1
        if index < len(status_ids_ordered):
            next_status = status_ids_ordered[index]
            self.forcing = True
            self.status_id = next_status

    def move_to_next_status(self):
        status_ids_ordered = self.env['adm.inquiry.status'].search([], order="sequence")
        index = 0
        for status in status_ids_ordered:
            if status == self.status_id:
                break
            index += 1

        index += 1
        if index < len(status_ids_ordered):
            next_status = status_ids_ordered[index]

            if self.status_id.type_id == 'done':
                raise exceptions.except_orm(_('Inquiry completed'), _('The Inquiry is already done'))
            elif self.status_id.type_id == 'cancelled':
                raise exceptions.except_orm(_('Inquiry cancelled'), _('The Inquiry cancelled'))
            else:
                self.status_id = next_status

    def cancel(self):
        status_ids_ordered = self.env['adm.inquiry.status'].search([], order="sequence")
        for status in status_ids_ordered:
            if status.type_id == 'cancelled':
                self.status_id = status
                break

    @api.onchange("first_name", "middle_name", "last_name")
    def _set_full_name(self):
        self.name = formatting.format_name(self.first_name, self.middle_name, self.last_name) 

    @api.onchange("country_id")
    def _onchange_country_id(self):
        res = {}
        if self.country_id:
            res['domain'] = {'state_id': [('country_id', '=', self.country_id.id)]}

    @api.model
    def create(self, values):
        first_status = self.env['adm.inquiry.status'].search([], order="sequence")[0]
        values['status_id'] = first_status.id
        values['name'] = formatting.format_name(values['first_name'], values['middle_name'], values['last_name']) 

        parter = False

        if not "partner_id" in values or not values["partner_id"]:
            partner = self.create_new_partner(values)
            values["partner_id"] = partner.id
        else:
            partner = self.env["res.partner"].browse(values["partner_id"])
        inquiry = super().create(values)
        
        partner.uni_inquiry_id = inquiry.id
        return inquiry

    def create_new_partner(self, values):
        PartnerEnv = self.env["res.partner"]

        partner = PartnerEnv.create({
            "name": values.get("name", False),
            "first_name": values.get("first_name", False),
            "middle_name": values.get("middle_name", False),
            "last_name": values.get("last_name", False),
            "email": values.get("email", False),
            "phone": values.get("phone", False),
            "country_id": values.get("country_id", False),
            "state_id": values.get("state_id", False),
            "city": values.get("city", False),
            "street": values.get("street", False),
            "zip": values.get("zip", False),
        })
        
        #===============================================================================================================
        # user = UsersEnv.create({
        #     "name": values["name"],
        #     "partner_id": partner.id,
        #     "login": values["email"],
        #     "sel_groups_1_9_10": 9,
        # })
        #===============================================================================================================
         
        return partner
    
    def create_new_application(self):
        print("Create New Application")
        
        #===============================================================================================================
        # # Create Contact
        # Partner = User
        # user = super(ResUsers, self).create(values)
        # if user.email and not self.env.context.get('no_reset_password'):
        #     try:
        #         user.with_context(create_user=True).action_reset_password()
        #     except MailDeliveryException:
        #         user.partner_id.with_context(create_user=True).signup_cancel()
        # return user
        #===============================================================================================================

        
        ApplicationEnv = self.env["adm.application"] 


        medical_base = []

        
        PartnerEnv = self.env["res.partner"]
        UsersEnv = self.env["res.users"]
        
        parent_id = PartnerEnv.search(["&", ("parent_id", "=", self.partner_id.parent_id.id), ("function", "=", "parent")])

        user_created = False
        first_user = False
        for parent in parent_id:
            parent_main_id = parent.id
            parent_main_name = parent.name
            parent_main_email = parent.email

            user = UsersEnv.search([("partner_id", "=", parent_main_id)])

            if not user:
                user_created = True
                parent_main_id = parent_main_id
                parent_main_name = parent_main_name
                parent_main_email = parent_main_email
                user = UsersEnv.create({
                    "name": parent_main_name,
                    "partner_id": parent_main_id,
                    "login": parent_main_email,
                    "password": 'userdemo',
                    "sel_groups_1_8_9": 8,
                })
                if not first_user:
                    first_user = user

        if not user_created:
            template_id = self.env.ref('adm.email_template_data_inquiry_accepted')
            #===========================================================================================================
            # Note:
            # You should provide a template for making message_post_with_template work
            # this template should have a model_id for the model that will send and 
            # a example for this is in email_tempalte_data.xml in data folder
            #===========================================================================================================
                        
            self.message_post_with_template(template_id=template_id.id, res_id=self.id)

        application_record = ApplicationEnv.create({
            "name": self.name,
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "last_name": self.last_name,
            "date_of_birth": self.date_of_birth,
            "gender": self.gender.id,
            "current_school": self.current_school,
            "current_school_address": self.current_school_address,
            "partner_id": self.partner_id.id,
            "grade_level": self.grade_level_id.id,
            "school_year": self.school_year_id.id,
            "medical_conditions_ids": medical_base,
            "family_id": self.partner_id.get_families()[0].id,
            "responsible_user_id": first_user.id
        })

        # Creating language
        for language in self.language_ids:
            ApplicationLanguageEnv = self.env["adm.application.language"]

            ApplicationLanguageEnv.create({
                "language_id": language.language_id.id,
                "language_level_id": language.language_level_id.id,
                "application_id": application_record.id,
            })

        self.partner_id.application_id = application_record.id
        self.application_id = application_record.id
        application_record.inquiry_id = self.id

    def write(self, values):

        # print(self.task_ids)
        # print(self.state_tasks)
        #
        # self.condition = ()
        # print(self.condition)

        StatusEnv = self.env['adm.inquiry.status'] 
        status_ids = StatusEnv.search([])

        print(status_ids)

        if "status_id" in values and not self.forcing:
            if not self.state_tasks & self.task_ids == self.state_tasks and self:
                raise exceptions.ValidationError("All task are not completed")
        else:
            self.forcing = False

        inquiry = super().write(values)
        self.partner_id.name = self.name
        
        if "status_id" in values:
            next_status = StatusEnv.browse([values["status_id"]])
            if (next_status.type_id == "done" and 
                not self.application_id):
                self.create_new_application()
        
        return inquiry

    
    def unlink(self):
        print("Borrado")
        return super(Inquiry, self).unlink()

    # Mail integration
    # message_follower_ids
    
    def message_get_default_recipients(self):
        return {
            r.id : {'partner_ids': [],
                    'email_to': r.email}
            for r in self.sudo()
        }


    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        # remove default author when going through the mail gateway. Indeed we
        # do not want to explicitly set user_id to False; however we do not
        # want the gateway user to be responsible if no other responsible is
        # found.
        self = self.with_context(default_user_id=False)

        if custom_values is None:
            custom_values = {}
        defaults = {
            'name':  msg_dict.get('subject') or _("No Subject"),
            'email_from': msg_dict.get('from'),
            'email_cc': msg_dict.get('cc'),
            'partner_id': msg_dict.get('author_id', False),
        }
        if msg_dict.get('author_id'):
            defaults.update(self._onchange_partner_id_values(msg_dict.get('author_id')))
        if msg_dict.get('priority') in dict(crm_stage.AVAILABLE_PRIORITIES):
            defaults['priority'] = msg_dict.get('priority')
        defaults.update(custom_values)

        # assign right company
        if 'company_id' not in defaults and 'team_id' in defaults:
            defaults['company_id'] = self.env['crm.team'].browse(defaults['team_id']).company_id.id
        return super().message_new(msg_dict, custom_values=defaults)


class InquiryTasks(models.Model):
    _name = 'adm.inquiry.task'
    _description = "Inquiry Task"

    name = fields.Char("Name")
    description = fields.Char("Description")
    status_id = fields.Many2one("adm.inquiry.status", string="Status")

    
class AdmissionInquirylanguage(models.Model):
    _name = 'adm.inquiry.language'
    _description = "Inquiry Language"

    language_id = fields.Many2one("adm.language", string="Language")
    language_level_id = fields.Many2one("adm.language.level", string="Language Level")
    inquiry_id = fields.Many2one("adm.inquiry", string="Inquiry")
