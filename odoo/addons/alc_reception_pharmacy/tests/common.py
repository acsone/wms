# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class CommonReceptionPharmacyCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=True, queue_job__no_delay=True
            )
        )

        # Create customer with delivery address
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner",
                "street": "25 rue des bourgeois",
                "zip": "5000",
                "country_id": cls.env.ref("base.be").id,
                "type": "delivery",
                "is_delivered_by_alcyon": True,
            }
        )

        # Create the product for reception
        cls.product = cls.env["product.product"].browse(
            cls.env.ref("alc_reception_pharmacy.product_colis_souverain").id
        )

        cls.bin = cls.env["stock.location"].create({"name": "Test unit"})

        # Instance of reception pharmacy
        cls.ReceptionPharmacy = cls.env["reception.pharmacy"]
        cls.ReceptionPharmacyLine = cls.env["reception.pharmacy.line"]

        cls.warehouse_1 = cls.env.ref("stock.warehouse0")
        cls.warehouse_1.write(
            {
                "name": "Test Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "TST",
            }
        )
        cls.warehouse_1.pick_type_id.code = "internal"
        cls.bin.location_id = cls.warehouse_1.lot_stock_id.id
        cls.env["stock.location"]._parent_store_compute()

        # cls.warehouse_1.pick_type_id.group_pickings = True
        cls.warehouse_1.out_type_id.group_pickings = True
        cls.carrier = cls.env["delivery.carrier"].search(
            [("free_over", "=", False)], limit=1
        )

        cls.env["ir.model.data"].create(
            {
                "module": "__setup__",
                "name": "deliver_carrier_alcyon",
                "model": "delivery.carrier",
                "res_id": cls.carrier.id,
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "test product2",
                "default_code": "987654312",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        cls._set_qty_in_loc_only(cls.product2, 100)

    def setUp(self):
        super().setUp()
        # mute logger
        loggers = ["odoo.addons.queue_job.models.base"]
        for logger in loggers:
            logging.getLogger(logger).addFilter(self)

        @self.addCleanup
        def un_mute_logger():
            for logger_ in loggers:
                logging.getLogger(logger_).removeFilter(self)

    def filter(self, record):
        # required to mute logger
        return 0

    @classmethod
    def _validate_reception_and_return_picking(cls, reception):
        existing_pickings = cls.env["stock.picking"].search([])
        reception.validate()
        new_pickings = cls.env["stock.picking"].search([]) - existing_pickings
        return new_pickings

    @classmethod
    def _set_qty_in_loc_only(cls, product, qty, location=None):
        location = location or cls.env.ref("stock.stock_location_stock")
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "inventory_quantity": qty,
                "location_id": location.id,
            }
        ).action_apply_inventory()

    @classmethod
    def _create_and_prepare_so(cls):
        cls.so1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "warehouse_id": cls.warehouse_1.id,
                "carrier_id": cls.carrier.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product2.name,
                            "product_id": cls.product2.id,
                            "product_uom_qty": 15.0,
                            "product_uom": cls.product2.uom_id.id,
                        },
                    )
                ],
            }
        )
        cls.so1.action_confirm()

        cls.picking = cls.so1.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "internal"
        )

        cls.picking.action_confirm()
        cls.picking.action_assign()
        for pack_op in cls.picking.move_line_ids:
            pack_op.qty_done = pack_op.reserved_uom_qty
        cls.picking._action_done()
        cls.shipping = cls.so1.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )

        cls.shipping.action_confirm()
        cls.shipping.action_assign()
        for pack_op in cls.shipping.move_line_ids:
            pack_op.qty_done = pack_op.reserved_uom_qty
