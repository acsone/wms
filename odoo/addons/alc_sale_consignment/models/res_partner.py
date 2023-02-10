# © 2017 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.sale.models.res_partner import ResPartner as ResPartnerBase
from odoo.addons.stock.models.stock_location import Location


class ResPartner(ResPartnerBase):

    property_stock_consignment_customer = fields.Many2one[Location](
        string="Customer Consignment Location",
        company_dependent=True,
        help="This stock location will be used for consignment orders "
        "as the destination location for goods you send to this partner",
        domain=[("usage", "=", "internal")],
    )
