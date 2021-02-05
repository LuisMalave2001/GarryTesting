'''
Created on Feb 1, 2020

@author: LuisMora
'''
from odoo import models, fields


class HouseAddress(models.Model):
    _name = 'adm.house_address'
    _description = "Adm House address"

    name = fields.Char("Name")
    country_id = fields.Many2one("res.country", string="Country",
                                 required=True)
    state_id = fields.Many2one("res.country.state", string="State")

    city = fields.Char("City")
    zip = fields.Char("Zip")
    street = fields.Char("Street")
    phone = fields.Char("Homephone")

    family_id = fields.Many2one("res.partner", string="Family",
                                domain=[('is_company', '=', True)])
