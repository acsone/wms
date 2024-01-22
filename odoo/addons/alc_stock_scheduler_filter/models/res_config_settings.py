# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models import res_config


class ResConfigSettings(res_config.ResConfigSettings):

    apply_filter_on_orderpoint_scheduler = fields.Boolean(
        default=False,
        help="Activate filter when running the scheduler to run the scheduler on specific"
        "suppliers, days or configured day on the partner supplier form.",
        config_parameter="alc_stock_scheduler_filter.apply_filter_on_orderpoint_scheduler",
    )
