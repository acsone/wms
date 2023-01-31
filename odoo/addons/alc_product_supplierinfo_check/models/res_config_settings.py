# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models import res_config


class ResConfigSettings(res_config.ResConfigSettings):

    check_alcyon_constraints_on_supplierinfo = fields.Boolean(
        default=False,
        help="Activate special check defined for alcyon on supplierinfo.",
        config_parameter="alc_product_supplierinfo_check.check_alcyon_constraints_on_supplierinfo",
    )
