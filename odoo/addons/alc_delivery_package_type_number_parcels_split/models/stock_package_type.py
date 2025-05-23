# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPackageType(models.Model):

    _inherit = "stock.package.type"

    auto_distribute_products_in_parcels = fields.Boolean(
        string="Auto-distribute products in parcels",
        help="If checked, on put in pack, as many packs as the number of parcels "
        " will be created. Products will be 'equally' and 'randomly' "
        "distributed among the various packs. If unchecked, only one pack will "
        "be created and all products will be put in this pack. This option is "
        "if you want to create a pack for each parcel but don't want to follow "
        "the content of the parcels since you can put your different parcels "
        "in different locations and still know where the different parts of your "
        "delivery are. This option is only available if the number of parcels "
        "is greater than 1.",
        default=False,
    )
