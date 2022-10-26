# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError

from odoo.addons.alc_stock_picking_batch_creation.tests.common import (
    AlcClusterPickingCommonFeatures,
)
from odoo.addons.delivery_rounds.tests.common import DeliveryRoundTestCase


class TestBatchByDeliveryCarrier(
    AlcClusterPickingCommonFeatures, DeliveryRoundTestCase
):
    @classmethod
    def setUpClass(cls):
        super(TestBatchByDeliveryCarrier, cls).setUpClass()
        # We need a valid location to make the query on delivery_rounds
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.stock_location.write(
            {"zone": "G", "corridor": "A", "shelf": "42", "height": "4", "box": "B12"}
        )
        cls.carrier1 = cls.env["delivery.carrier"].create({"name": "carrier1"})
        cls.carrier2 = cls.env["delivery.carrier"].create({"name": "carrier2"})
        cls.carrier3 = cls.env["delivery.carrier"].create({"name": "carrier3"})
        cls.env = cls.env(context=dict(cls.env.context, test_queue_job_no_delay=True))
        cls.operator_1 = cls.env.user.copy()
        cls.delivery_template1 = cls.env["round.template"].create(
            {"name": "Unittest delivery template 1"}
        )
        cls.delivery_round1 = cls.env["round.instance"].create(
            {
                "template_id": cls.delivery_template1.id,
                "date": "2022-10-28",
                "time_picking_planned": 8,
                "state": "draft",
            }
        )

        cls.delivery_template2 = cls.env["round.template"].create(
            {"name": "Unittest delivery template 2"}
        )
        cls.delivery_round2 = cls.env["round.instance"].create(
            {
                "template_id": cls.delivery_template2.id,
                "date": "2022-10-28",
                "time_picking_planned": 10,
                "state": "draft",
            }
        )

        cls.delivery_template3 = cls.env["round.template"].create(
            {"name": "Unittest delivery template 3"}
        )
        cls.delivery_round3 = cls.env["round.instance"].create(
            {
                "template_id": cls.delivery_template3.id,
                "date": "2022-10-28",
                "time_picking_planned": 10,
                "state": "draft",
            }
        )
        sale1 = cls._confirm_sale_order(carrier_id=cls.carrier1.id)
        sale2 = cls._confirm_sale_order(carrier_id=cls.carrier2.id)
        sale3 = cls._confirm_sale_order(carrier_id=cls.carrier1.id)
        sale4 = cls._confirm_sale_order(carrier_id=cls.carrier2.id)
        sale5 = cls._confirm_sale_order(carrier_id=cls.carrier3.id)

        cls.picks1 = sale1.picking_ids.filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        cls.picks2 = sale2.picking_ids.filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        cls.picks3 = sale3.picking_ids.filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        cls.picks4 = sale4.picking_ids.filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        cls.picks5 = sale5.picking_ids.filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )

        cls.picks = cls.picks1 | cls.picks2 | cls.picks3 | cls.picks4 | cls.picks5
        cls.picks.write({"picking_type_id": cls.picking_type_ali.id})
        cls.picks.action_confirm()
        cls.picks.action_assign()
        cls.picks.force_assign()
        cls.wiz = cls.makePickingBatch.create(
            {
                "user_id": cls.operator_1.id,
                "picking_type_ids": [(4, cls.picking_type_ali.id)],
                "stock_device_type_ids": [
                    (4, cls.device1.id),
                    (4, cls.device2.id),
                    (4, cls.device3.id),
                ],
                "only_one_delivery_round_by_cluster": False,
            }
        )

        cls.operator_1.only_one_delivery_round_by_cluster = False
        # We need a picking zone to make the query on delivery_rounds
        picking_zone_ali = cls.env["picking.zone"].create(
            {"code": "04", "name": "Aliment"}
        )
        cls.picking_type_ali.picking_zone_id = picking_zone_ali

    def test_get_pickings_to_batch_one_carrier(self):
        pickings = self.picks1 | self.picks3
        self.delivery_round1._do_assign_pickings(pickings)
        pickings2 = self.picks2 | self.picks4
        self.delivery_round2._do_assign_pickings(pickings2)
        self.delivery_round1.button_picking_start()
        self.delivery_round2.button_picking_start()
        self.wiz.write({"delivery_carrier_ids": [(4, self.carrier1.id)]})

        candidates_pickings = self.wiz._candidates_pickings_to_batch(
            user=self.operator_1
        )
        self.assertEqual(candidates_pickings, pickings)

    def test_get_pickings_to_batch_two_carriers(self):
        pickings = self.picks1 | self.picks3
        self.delivery_round1._do_assign_pickings(pickings)
        pickings2 = self.picks2 | self.picks4
        self.delivery_round2._do_assign_pickings(pickings2)
        self.delivery_round1.button_picking_start()
        self.delivery_round2.button_picking_start()
        carriers = self.carrier1 | self.carrier2
        self.wiz.write({"delivery_carrier_ids": [(6, 0, carriers.ids)]})

        candidates_pickings = self.wiz._candidates_pickings_to_batch(
            user=self.operator_1
        )
        self.assertEqual(candidates_pickings, pickings | pickings2)

    def test_get_pickings_to_batch_no_carrier(self):
        self.delivery_round1._do_assign_pickings(self.picks5)
        self.delivery_round1.button_picking_start()
        carriers = self.carrier1 | self.carrier2
        self.wiz.write({"delivery_carrier_ids": [(6, 0, carriers.ids)]})

        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.wiz._candidates_pickings_to_batch(user=self.operator_1)

    def test_get_pickings_deliveries_same_carrier(self):
        self.delivery_round1._do_assign_pickings(self.picks1)
        self.delivery_round1.button_picking_start()
        self.delivery_round3._do_assign_pickings(self.picks3)
        self.delivery_round3.button_picking_start()
        self.delivery_round2._do_assign_pickings(self.picks2)
        self.delivery_round2.button_picking_start()
        self.wiz.write({"delivery_carrier_ids": [(4, self.carrier1.id)]})

        candidates_pickings = self.wiz._candidates_pickings_to_batch(
            user=self.operator_1
        )
        self.assertEqual(candidates_pickings, self.picks1 | self.picks3)
