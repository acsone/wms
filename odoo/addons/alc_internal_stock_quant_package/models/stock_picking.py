# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

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
        pickings = self._get_picking_to_empty_internal_packages().filtered(
            lambda p: p.state == "done"
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
    def _get_picking_to_empty_internal_packages(self):
        return self.filtered(
            lambda p: p.picking_type_id.empty_internal_package_on_transfer
        )

    @api.multi
    def _get_packops_internal_package_used_to_empty(self):
        pickings = self._get_picking_to_empty_internal_packages()
        return pickings.mapped("pack_operation_ids").filtered(
            lambda pop: pop.result_package_id.is_internal
        )
