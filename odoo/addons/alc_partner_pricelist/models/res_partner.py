# Copyright 2017 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.product.models.product_pricelist import Pricelist
from odoo.addons.sale.models.res_partner import ResPartner as BaseResPartner


class ResPartner(BaseResPartner):

    supplier_promotion_sale_allowed = fields.Boolean(
        string="Supplier promotion allowed on sale"
    )
    discount_pricelist_ids = fields.Many2many[Pricelist](
        relation="partner_discount_pricelist_rel",
        column1="partner_id",
        column2="pricelist_id",
        string="Alcyon Discount Pricelist",
    )

    @api.model
    def _commercial_fields(self):
        """Adds fields as commercial fields so.

        theirs values will be synced to children partners.
        """
        commercial_fields = super()._commercial_fields()
        if not commercial_fields or not isinstance(commercial_fields, list):
            commercial_fields = []
        commercial_fields.extend(
            ["supplier_promotion_sale_allowed", "discount_pricelist_ids"]
        )
        return commercial_fields
