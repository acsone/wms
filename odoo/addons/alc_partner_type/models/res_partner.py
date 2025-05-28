# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.product.models import res_partner


class ResPartner(res_partner.ResPartner):

    partner_type = fields.Selection(  # replaces alcyon_category_id
        string="Alcyon Partner Category",
        required=True,
        selection=[
            ("guest", "Guest"),  # lowest access rights
            ("misc", "Miscellaneous"),
            ("student_like", "Student and similar"),
            ("shareholder", "Shareholder"),
            ("veterinary", "Veterinary"),
            ("veterinary_without_pharmacy", "Veterinary without Pharmacy"),
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
    is_student = fields.Boolean(string="Student", compute="_compute_is_student")

    @api.model
    def _get_partner_types(self):
        return [s[0] for s in self._fields["partner_type"].selection]

    @api.depends("partner_type")
    def _compute_is_student(self):
        for partner in self:
            partner.is_student = partner.partner_type == "student_like"

    def _get_product_domain(self):
        self.ensure_one()
        partner_type_like = f"%%{self.partner_type}%%"
        return [("allowed_partner_types", "like", partner_type_like)]
