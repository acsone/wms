# © 2017 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.sale_stock.models.sale_order import SaleOrder as SaleOrderBase


class SaleOrder(SaleOrderBase):

    is_consignment = fields.Boolean(
        "For Consignment",
        help="Procurement will be generated for the consignment location "
        "of the selected customer",
    )
