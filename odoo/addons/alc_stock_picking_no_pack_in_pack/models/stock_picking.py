# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):

    _inherit = "stock.picking"

    @api.multi
    def put_in_pack(self):
        for pick in self:
            pack_operation_ids = self.env["stock.pack.operation"]
            if pick.picking_type_subcode == "PICK":
                # If it's not the picking OUT for the pick/ship mecanism, everything stays the same
                return super(StockPicking, self).put_in_pack()

            if (
                pick.picking_type_code == "outgoing"
                and pick.carrier_id.id
                == self.env.ref("alc_delivery_carrier_gls.delivery_carrier_gls_be").id
            ):

                pack_operation_candidates = [
                    x
                    for x in pick.pack_operation_ids
                    if x.qty_done > 0 and (not x.result_package_id)
                ]

                package = [
                    x.package_id for x in pack_operation_candidates if x.package_id
                ]
                if len(package) > 1:
                    raise ValidationError(_("More than one pack"))

                if not package:
                    return super(StockPicking, self).put_in_pack()

                for operation in pack_operation_candidates:
                    # If we haven't done all qty in operation, we have to split into 2 operation
                    op = operation
                    if operation.qty_done < operation.product_qty:
                        new_operation = operation.copy(
                            {
                                "product_qty": operation.qty_done,
                                "qty_done": operation.qty_done,
                            }
                        )

                        operation.write(
                            {
                                "product_qty": operation.product_qty
                                - operation.qty_done,
                                "qty_done": 0,
                            }
                        )
                        if operation.pack_lot_ids:
                            packlots_transfer = [
                                (4, x.id) for x in operation.pack_lot_ids
                            ]
                            new_operation.write({"pack_lot_ids": packlots_transfer})

                            # the stock.pack.operation.lot records now belong to the new, packaged stock.pack.operation
                            # we have to create new ones with new quantities for our original, unfinished stock.pack.operation
                            new_operation._copy_remaining_pack_lot_ids(operation)

                        op = new_operation
                    pack_operation_ids |= op
                if pack_operation_candidates:
                    pack_operation_ids.check_tracking()
                    pack_operation_ids.write({"result_package_id": package[0].id})
                else:
                    raise ValidationError(
                        _("Please process some quantities to put in the pack first!")
                    )
                return package[0]

            return super(StockPicking, self).put_in_pack()
