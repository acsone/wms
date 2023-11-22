# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.models import Model


class VeterinaryGroup(Model):
    _name = "veterinary.group"
    _inherit = ["veterinary.group", "se.product.update.mixin"]

    def get_products(self):
        return self.mapped("product_template_ids")

    def needs_product_update(self, vals):
        return any(k in vals for k in ("name", "product_template_ids"))
