# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    update_scheduled_date = fields.Boolean(
        help="Will update scheduled date of picking based on process end date(time).",
        config_parameter="stock_release_channel_process_end_time.update_scheduled_date",
    )
