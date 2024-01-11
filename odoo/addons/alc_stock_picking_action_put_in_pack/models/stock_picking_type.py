# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_picking import PickingType


class StockPickingType(PickingType):

    package_type_required_on_put_in_pack = fields.Boolean(
        help="Check this if you need to force users to select the package type on put "
        "in pack even for a single product. If not checked, the put in pack will "
        "use the product default package type."
    )
