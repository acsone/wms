# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _get_gls_pack_package(self, operations):
        """Private method, only call it if conditions are checked before."""
        pack_operation_candidates = self.pack_operation_ids.browse()
        for op in (o for o in operations if not o.result_package_id):
            pack_operation_candidates |= op
        package = pack_operation_candidates.mapped("package_id")
        if len(package) > 1:
            raise ValidationError(_("More than one pack"))
        return package

    def button_gls_put_in_pack(self):
        """ Dedicated put in pack button for GLS"""
        self.ensure_one()
        return self._get_gls_put_in_pack_wizard_action(False)

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
