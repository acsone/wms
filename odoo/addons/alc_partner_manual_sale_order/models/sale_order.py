# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.sale.models.sale_order import SaleOrder as SaleOrderBase

from .res_partner import ResPartner


class SaleOrder(SaleOrderBase):

    manual_sale_order_allowed = fields.Boolean(
        related="partner_id.manual_sale_order_allowed", readonly=True
    )
    partner_id = fields.Many2one[ResPartner](
        domain="[('type', '!=', 'private'), ('company_id', 'in', (False, company_id)), ('manual_sale_order_allowed','=',True)]"
    )
