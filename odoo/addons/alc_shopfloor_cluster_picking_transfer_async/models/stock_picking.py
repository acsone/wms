# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models

from odoo.addons.queue_job.job import identity_exact, job


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def _get_picking_to_validate(self):
        return self.filtered(lambda p: p.state not in ("done", "cancel"))

    def _delay_do_transfer(self):
        for picking in self._get_picking_to_validate():
            description = _("Validate picking %s") % picking.display_name
            picking.with_delay(
                identity_key=identity_exact, description=description
            )._do_transfer()

    @job(default_channel="root.background.stock_picking_validate")
    def _do_transfer(self):
        for rec in self._get_picking_to_validate():
            if rec.pack_operation_ids:
                rec.do_transfer()
            if rec.state != "done" and rec.batch_id:
                # Unassign not validated pickings from the batch, they will be
                # processed in another batch automatically later on
                rec.write({"batch_id": False, "operator_id": False, "printed": False})
