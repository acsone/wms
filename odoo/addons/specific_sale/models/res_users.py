from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    is_for_newpharma = fields.Boolean("For NewPharma")
    is_for_olalux = fields.Boolean("For Olalux")
