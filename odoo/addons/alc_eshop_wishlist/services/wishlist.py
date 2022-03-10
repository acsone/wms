# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class WishlistService(Component):
    _inherit = "shopinvader.wishlist.service"

    @restapi.method(
        [(["/<int:_id>/update"], "POST")],
        input_param=restapi.CerberusValidator("_validator_update"),
        output_param=restapi.CerberusValidator("_wishlist_output_schema"),
    )
    def bulk_update(self, _id, **params):
        """Wishlist update all at once"""
        record = self._get(_id)
        params = self._prepare_params(params.copy(), mode="update")
        # unlink all existing lines first
        params["set_line_ids"].insert(0, (5, 0, 0))
        record.write(params)
        self._post_update(record)
        return self._to_json_one(record)
