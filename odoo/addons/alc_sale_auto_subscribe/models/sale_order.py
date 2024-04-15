# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.sale.models import sale_order


class SaleOrder(sale_order.SaleOrder):
    def _message_auto_subscribe_followers(self, updated_values, default_subtype_ids):
        # We want to auto subscribe the callcenter to the SO by default
        followers = super()._message_auto_subscribe_followers(
            updated_values, default_subtype_ids
        )
        user = self.env.ref(
            "alc_sale_auto_subscribe.alc_user_callcenter", raise_if_not_found=False
        )
        if user:
            followers.append((user.partner_id.id, default_subtype_ids, False))
        return followers
