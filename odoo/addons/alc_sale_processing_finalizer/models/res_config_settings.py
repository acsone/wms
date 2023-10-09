# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_config import ResConfigSettings as ConfigSettings


class ResConfigSettings(ConfigSettings):

    send_processing_finalizer_email = fields.Boolean(
        "Auto-finalized email",
        default=False,
        config_parameter="alc_sale_processing_finalizer.send_email",
    )
