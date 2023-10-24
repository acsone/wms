# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.connector_search_engine.models.se_index import SeIndex as SeIndexBase

from ..tools.alc_eshop_info_banner_serializer import (
    AlcEshopInfoBannerShopinvaderSerializer,
)


class SeIndex(SeIndexBase):
    serializer_type = fields.Selection(
        selection_add=[
            ("alc_eshop_info_banner", "Eshop Info Banner"),
        ],
        ondelete={"alc_eshop_info_banner": "cascade"},
    )

    @api.constrains("model_id", "serializer_type")
    def _check_model(self):
        eshop_info_banner_model = self.env["ir.model"].search(
            [("model", "=", "alc.eshop.info.banner")], limit=1
        )
        for se_index in self:
            if (
                se_index.serializer_type == "alc_eshop_info_banner"
                and se_index.model_id != eshop_info_banner_model
            ):
                raise ValidationError(_("'Serializer Type' must match 'Model'"))

    def _get_serializer(self):
        self.ensure_one()
        if self.serializer_type == "alc_eshop_info_banner":
            return AlcEshopInfoBannerShopinvaderSerializer()
        return super()._get_serializer()
