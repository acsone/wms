# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class AlcLegalForm(models.Model):

    _name = "alc.partner.legal.form"
    _description = "Legal form of a company"

    name = fields.Char("Name", required=True, translate=True)

    _sql_constraints = [
        ("unique_name", "unique(name)", _("This legal form already exists"))
    ]
