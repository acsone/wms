# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    product_description_vectorization_enabled = fields.Boolean(
        string="Enable Product Description Vectorization",
        help="Check this if you want to enable the generation of a vector for the "
        "product description using a pre-trained model. This vector will be used to "
        "find similar products.",
        config_parameter="alc_product_similarity_settings.product_description_vectorization_enabled",
    )
