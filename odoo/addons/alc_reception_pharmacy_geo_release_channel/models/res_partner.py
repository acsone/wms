# Copyright 2023 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields

from odoo.addons.alc_reception_pharmacy.models.res_partner import (
    ResPartner as PartnerPharmacy,
)
from odoo.addons.stock_release_channel_geoengine.models.res_partner import (
    ResPartner as Partner,
)


class ResPartner(Partner):

    is_delivered_by_alcyon = fields.Boolean(
        compute="_compute_is_delivered_by_alcyon",
        store=False,
    )
    partner_shipping_id = fields.Many2one[PartnerPharmacy](
        search="_search_partner_shipping_id",
    )

    @api.depends(
        "stock_release_channel_ids",
        "child_ids",
        "partner_shipping_id",
        "partner_shipping_id.located_in_stock_release_channel_ids",
    )
    def _compute_is_delivered_by_alcyon(self):
        partner_alcyon = self.env.user.company_id.partner_id
        for rec in self:
            # Compute the field depending on manual release channels and computed ones
            # based on geo localization.
            result_stock_release_channel_ids = (
                rec.partner_shipping_id.located_in_stock_release_channel_ids
                | rec.stock_release_channel_ids
            )
            rec.is_delivered_by_alcyon = (
                partner_alcyon
                in result_stock_release_channel_ids.mapped("carrier_ids").mapped(
                    "partner_id"
                )
            )

    def _search_partner_shipping_id(self, operator, value):
        return [("partner_shipping_id.name", operator, value)]
