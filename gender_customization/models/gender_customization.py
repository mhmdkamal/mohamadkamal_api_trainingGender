# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Gender(models.Model):
    _inherit = 'res.partner'

    person_gender = fields.Char("Gender")
