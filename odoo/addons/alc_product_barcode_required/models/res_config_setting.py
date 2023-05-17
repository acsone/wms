# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    product_barcode_required = fields.Boolean(
        "Make barcode required on product by default.",
        default=False,
        config_parameter="product_barcode_required",
    )
