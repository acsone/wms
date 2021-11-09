# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"
    partner_type = fields.Selection(  # replaces alcyon_category_id
        string="Alcyon Partner Category",
        required=True,
        selection=[
            ("guest", "Guest"),  # lowest access rights
            ("misc", "Miscellaneous"),
            ("student_like", "Student and similar"),
            ("shareholder", "Shareholder"),
            ("veterinary", "Veterinary"),
            ("wholesaler_pharmacy", "Pharmacy Wholesaler"),
            ("wholesaler_veterinary", "Veterinary Wholesaler"),
            ("equipment_only", "Equipment Only"),
            ("food_only", "Food Only"),
            ("export_customer", "Export Customer"),
            ("export_meds", "Export Medicine"),
            ("supplier", "Suppliers"),
        ],
        default="misc",
    )

    @api.model
    def _get_partner_types(self):
        return [s[0] for s in self._fields["partner_type"].selection]
