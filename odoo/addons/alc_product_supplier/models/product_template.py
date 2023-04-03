# © 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields

from odoo.addons.partner_manual_rank.models.res_partner import ResPartner
from odoo.addons.product.models import product_template


class ProductTemplate(product_template.ProductTemplate):

    supplier_id = fields.Many2one[ResPartner](
        string="Vendor",
        readonly=True,
        domain=[("is_supplier", "=", True)],
        related="seller_ids.partner_id",
        store=True,
        index=True,
    )
    supplier_rel_id = fields.Integer(
        string="Vendor ID",
        readonly=True,
        related="supplier_id.id",
        store=False,
    )
    vendor_product_code = fields.Char(
        "Vendor Product Code",
        readonly=True,
        related="seller_ids.product_code",
        store=True,
        index=True,
    )
