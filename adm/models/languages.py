# -*- coding: utf-8 -*-

from odoo import models, fields


class AdmissionLanguages(models.Model):
    _name = 'adm.language'
    _description = "Adm Language"

    name = fields.Char("Name", required=True)


class AdmissionLanguageLevels(models.Model):
    _name = 'adm.language.level'
    _description = "Adm Language skill"

    name = fields.Char("Name", required=True)


class LanguageTypeOfSkill(models.Model):
    _name = 'adm.language.skill.type'
    _description = "Adm Language skill type"

    name = fields.Char("Type")
