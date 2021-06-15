# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def put_in_pack(self):
        """For GLS deliveries, replace the returned action by the GLS wizard."""
        # beware: the package can be edited in the picking before action_done is called.
        # therefore, this module is unsafe: it's the responsibility of the user not to
        # do that. They can still resend a package in case of error though.
        res = super(StockPicking, self).put_in_pack()
        final_pack_id = res["res_id"] if isinstance(res, dict) else res.id
        if self.carrier_id.delivery_type == "gls":
            res = self._get_gls_put_in_pack_wizard_action(final_pack_id)
        return res

    def _get_gls_put_in_pack_wizard_action(self, package_id):
        xmlid = "alc_gls_putinpack.delivery_package_gls_wizard_act_window"
        window_action = self.env.ref(xmlid).read()[0]
        vals_wizard = {"picking_id": self.id, "package_id": package_id}
        wizard = self.env["delivery.package.gls.wizard"].create(vals_wizard)
        wizard.onchange_package_id()
        window_action["res_id"] = wizard.id
        return window_action
