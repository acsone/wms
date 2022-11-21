# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

import psycopg2

from odoo import _, models
from odoo.tools import float_compare

from odoo.addons.queue_job.exception import RetryableJobError
from odoo.addons.queue_job.job import identity_exact, job

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _moves_to_assign_domain(self):
        domain = [
            ("picking_type_id.subcode", "=", "PICK"),
            ("state", "=", "confirmed"),
            ("product_id", "in", self.ids),
            ("picking_id.operator_id", "=", False),
            ("procure_method", "=", "make_to_stock"),
        ]
        return domain

    @job(default_channel="root.background.stock_reassign_trial")  # priority=6
    def _moves_auto_assign(self):
        """ Find pickings and relaunch reservation """
        IrConfigParameter = self.env["ir.config_parameter"]
        enabled = IrConfigParameter.get_param(
            "stock_reassign_auto.reassign_trial_enabled", ""
        ).lower() in ["true", "1", "t", "y", "yes"]
        if not enabled:
            return
        self.ensure_one()
        available = (
            float_compare(
                self.qty_available, 0, precision_rounding=self.uom_id.rounding
            )
            > 0
        )
        if not available:
            return
        move = self.env["stock.move"].search(self._moves_to_assign_domain(), limit=1)
        if not move:
            return
        picking = move.picking_id
        try:
            self.env.cr.execute(
                "SELECT id FROM stock_picking WHERE id = %s FOR UPDATE NOWAIT",
                (picking.id,),
            )
        except psycopg2.OperationalError as err:
            if err.pgcode == "55P03":  # could not obtain the lock
                _logger.debug(
                    "Another job is already auto-assigning moves and acquired a"
                    " lock on one or some of stock.picking %s, retry later.",
                    picking.id,
                )
                raise RetryableJobError(
                    "Could not obtain lock on transfers, will retry.", ignore_retry=True
                )
            raise
        self.env["stock.move"]._do_reassign_product(picking, self)
        if (
            float_compare(
                self.qty_available, 0, precision_rounding=self.uom_id.rounding
            )
            > 0
        ):
            self._prepare_reassign()

    def _prepare_reassign(self):
        for product in self:
            product.with_delay(
                description=_("Try reserving for product %s") % product.id,
                priority=6,
                identity_key=identity_exact,
            )._moves_auto_assign()
        # Path: odoo/addons/stock_reassign_auto/models/stock.py
