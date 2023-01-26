# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models import res_config


class ResConfigSettings(res_config.ResConfigSettings):

    max_delay_to_process_receipt = fields.Integer(
        default=5,
        help="Maximum delay to handle the receipt of goods.",
        config_parameter="stock_grn.max_delay_to_process_receipt",
    )
