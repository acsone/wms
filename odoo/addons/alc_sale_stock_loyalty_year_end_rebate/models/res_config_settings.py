# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    display_rebate_on_sale_order_report = fields.Boolean(
        default=False,
        config_parameter="alc_sale_stock_loyalty_year_end_rebate.display_rebate_on_sale_order_report",
    )
