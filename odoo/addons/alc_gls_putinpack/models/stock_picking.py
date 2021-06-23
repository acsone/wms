# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_gls_put_in_pack(self):
        """ Dedicated put in pack button for GLS

        For GLS deliveries, we replace the default ve returned by the put_in_pack
        method by a specific GLS wizard.
        """
        self.ensure_one()
        res = self.put_in_pack()
        if not res:  # specific_stock bypasses the super raise
            raise ValidationError(_("There is no package to process."))
        if self.delivery_type == "gls":
            final_pack_id = res["res_id"] if isinstance(res, dict) else res.id
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

    def do_transfer(self):
        """If the packaging is missing on some package of a GLS picking, sending it
           would fail anyway (on missing packaging). This means the user would have to
           open the wizard on the correct package.
           To simplify this process, we directly return the first missing one,
           so that clicking the button repeatedly would eventually work.
        """
        gls_pickings = self.filtered(lambda p: p.delivery_type == "gls")
        gls_packages = gls_pickings.mapped("package_ids")
        for package in gls_packages:
            if not package.packaging_id:
                return self._get_gls_put_in_pack_wizard_action(package.id)
        return super(StockPicking, self).do_transfer()
