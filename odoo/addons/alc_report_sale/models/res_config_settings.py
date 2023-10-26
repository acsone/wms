# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_config import ResConfigSettings as ConfigSettings


class ResConfigSettings(ConfigSettings):

    on_confirm_generate_quotation_report = fields.Boolean(
        "Generate quotation report on confirm",
        default=False,
        config_parameter="alc_report_sale.on_confirm_generate_quotation_report",
    )
    on_confirm_generate_and_send_pharmacist_report = fields.Boolean(
        "Generate pharmacist report on confirm",
        default=False,
        config_parameter="alc_report_sale.on_confirm_generate_and_send_pharmacist_report",
    )
