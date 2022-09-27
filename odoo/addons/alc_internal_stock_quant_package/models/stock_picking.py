# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    empty_internal_package_on_transfer = fields.Boolean(
        compute="_compute_empty_internal_package_on_transfer",
    )

    def _get_out_picking(self):
        # this method is coupled with sale.order _compute_picking_ids, so any override
        # there should have an equivalent override of this method
        self.ensure_one()
        domain = [
            ("group_id", "=", self.group_id.id),
            ("picking_type_id.code", "=", "outgoing"),
            ("state", "not in", ["cancel", "done"]),
        ]
        return self.search(domain, limit=1)  # what should we do if we got more than 1?

    def _get_carrier(self):
        self.ensure_one()
        if self.picking_type_id.code != "outgoing":
            carrier = self._get_out_picking().carrier_id
        else:
            carrier = self.carrier_id
        return carrier

    @api.depends("picking_type_id.empty_internal_package_on_transfer", "carrier_id")
    def _compute_empty_internal_package_on_transfer(self):
        for record in self:
            carrier_id = record._get_carrier().id
            picking_type_id = record.picking_type_id.id
            value = self.env["stock.picking.type"]._empty_internal_package_on_transfer(
                picking_type_id, carrier_id,
            )
            record.empty_internal_package_on_transfer = value

    @api.multi
    def put_in_pack(self):
        self._packop_clear_internal_result_packages()
        return super(StockPicking, self).put_in_pack()

    @api.multi
    def do_transfer(self):
        self._packop_clear_internal_result_packages()
        res = super(StockPicking, self).do_transfer()
        self._empty_transferred_internal_packages()
        return res

    @api.multi
    def _empty_transferred_internal_packages(self):
        """
        Remove products from internal quant packages on picking done
        """
        pickings = self.filtered(
            lambda p: p.empty_internal_package_on_transfer and p.state == "done"
        )
        packages = pickings.mapped("pack_operation_pack_ids.package_id")
        internal_packages = packages.filtered("is_internal")
        internal_packages.unpack()

    @api.multi
    def _packop_clear_internal_result_packages(self):
        """
        Remove links between pack operations and stock quant package to ensure
        that pack operations are put into a non internal stock.quant.package
        """
        pack_operations = self._get_packops_internal_package_used_to_empty()
        pack_operations.write({"result_package_id": False})

    @api.multi
    def _get_packops_internal_package_used_to_empty(self):
        pickings = self.filtered("empty_internal_package_on_transfer")
        return pickings.mapped("pack_operation_ids").filtered(
            lambda pop: pop.result_package_id.is_internal
        )
