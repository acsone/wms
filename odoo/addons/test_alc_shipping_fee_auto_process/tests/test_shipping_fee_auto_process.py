# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command

from odoo.addons.alc_shipping_fee.tests.common import TestShippingFeeCommon


class TestRCDeliverShipFee(TestShippingFeeCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        dock = cls.env.ref("shipment_advice.stock_dock_demo")
        cls.rc1.shipment_planning_method = "simple"
        cls.rc1.dock_id = dock.id

    def test_fixed_and_extra_fees_auto_process_validation(self):
        so3 = self.env["sale.order"].create(
            {
                "partner_id": self.partner3.id,
                "carrier_id": self.delivery_method_5.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "price_unit": 70,
                        },
                    )
                ],
            }
        )
        so3.action_confirm()
        so3.picking_ids.assign_release_channel()
        channel = so3.picking_ids.release_channel_id
        channel.auto_deliver = True
        channel.action_lock()
        channel.action_deliver()
        self.assertEqual(channel.state, "delivering")
        channel._process_shipments()
        advices = channel.shipment_advice_ids.filtered(
            lambda s: s.state not in ("done", "cancel")
        )
        advices[0]._auto_process()
        self.assertEqual(self.get_shipping_cost(so3), self.fixed_fee + self.fee)

    def test_fixed_no_fee_auto_process_validation(self):
        """No shipping cost added if partner is set accordingly."""
        self.partner3.help_with_fee = False
        self.partner3.help_with_fixed_fee = False
        so3 = self.env["sale.order"].create(
            {
                "partner_id": self.partner3.id,
                "carrier_id": self.delivery_method_5.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "price_unit": 70,
                        },
                    )
                ],
            }
        )
        so3.action_confirm()
        so3.picking_ids.assign_release_channel()
        channel = so3.picking_ids.release_channel_id
        channel.auto_deliver = True
        channel.action_lock()
        channel.action_deliver()
        self.assertEqual(channel.state, "delivering")
        channel._process_shipments()
        advices = channel.shipment_advice_ids.filtered(
            lambda s: s.state not in ("done", "cancel")
        )
        advices[0]._auto_process()
        self.assertEqual(self.get_shipping_cost(so3), 0)
