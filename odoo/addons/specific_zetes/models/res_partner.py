# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_passport_required = fields.Boolean(
        "Passport required",
        help="Define if pickings for this "
        "partner need to be verify by "
        "an another picker.",
    )
