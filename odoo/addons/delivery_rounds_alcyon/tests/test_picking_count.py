# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.delivery_rounds.tests.common import DeliveryRoundTestCase


class TestInstancePickingCount(DeliveryRoundTestCase):
    @classmethod
    def _setup_picking_zones(cls):
        PickingZone = cls.env["picking.zone"]
        cls.zone_ali = PickingZone.create({"name": "Aliments", "code": "01"})
        cls.zone_med = PickingZone.create({"name": "Med", "code": "02"})
        cls.zone_frigo = PickingZone.create({"name": "Frigo", "code": "03"})
        cls.zone_mat = PickingZone.create({"name": "Mat", "code": "04"})

    @classmethod
    def _setup_picking_types(cls):
        PickingType = cls.env["stock.picking.type"]

        wh = cls.env.ref("stock.warehouse0")
        picking_sequence = wh.in_type_id.sequence_id

        cls.type_ali = PickingType.create(
            {
                "name": "Pick Aliments",
                "code": "internal",
                "subcode": "PICK",
                "picking_zone_id": cls.zone_ali.id,
                "sequence_id": picking_sequence.id,
            }
        )
        cls.type_med = PickingType.create(
            {
                "name": "Pick Med",
                "code": "internal",
                "subcode": "PICK",
                "picking_zone_id": cls.zone_med.id,
                "sequence_id": picking_sequence.id,
            }
        )
        cls.type_frigo = PickingType.create(
            {
                "name": "Pick Frigo",
                "code": "internal",
                "subcode": "PICK",
                "picking_zone_id": cls.zone_frigo.id,
                "sequence_id": picking_sequence.id,
            }
        )
        cls.type_mat = PickingType.create(
            {
                "name": "Pick Mat",
                "code": "internal",
                "subcode": "PICK",
                "picking_zone_id": cls.zone_mat.id,
                "sequence_id": picking_sequence.id,
            }
        )

    @classmethod
    def setUpClass(cls):
        super(TestInstancePickingCount, cls).setUpClass()
        cls._setup_picking_zones()
        cls._setup_picking_types()

    def test_picking_count(self):
        """Test quantities are computed correctly on round instance"""

        round_1 = self.delivery_round_1
        self.assertEqual(round_1.count_picking_available_total, 0)
        self.assertEqual(round_1.count_picking_done_total, 0)
        self.assertEqual(round_1.count_picking_available_partner, 0)
        self.assertEqual(round_1.count_picking_available_weight, 0)

        self.assertEqual(round_1.count_picking_available_total_ali, 0)
        self.assertEqual(round_1.count_picking_available_total_med, 0)
        self.assertEqual(round_1.count_picking_available_total_frigo, 0)
        self.assertEqual(round_1.count_picking_available_total_mat, 0)
        self.assertEqual(round_1.count_picking_available_total_pharm, 0)

        self.assertEqual(round_1.count_picking_done_total_ali, 0)
        self.assertEqual(round_1.count_picking_done_total_med, 0)
        self.assertEqual(round_1.count_picking_done_total_frigo, 0)
        self.assertEqual(round_1.count_picking_done_total_mat, 0)
        self.assertEqual(round_1.count_picking_done_total_pharm, 0)

        pick1 = self._create_picking_pick(partner=self.partner1)
        pick2 = self._create_picking_pick(partner=self.partner2)
        pick3 = self._create_picking_pick(partner=self.partner3)
        pick4 = self._create_picking_pick(partner=self.partner1)
        pick5 = self._create_picking_pick(partner=self.partner2)
        pick6 = self._create_picking_pick(partner=self.partner3)

        ship1 = self._create_picking_out(self.partner1)
        ship2 = self._create_picking_out(self.partner2)
        ship3 = self._create_picking_out(self.partner3)

        # we don't care about the details if it is really
        # in that state, it is only for the round to think it is
        pick1.move_lines.write({"state": "assigned"})
        pick2.move_lines.write({"state": "assigned"})
        pick3.move_lines.write({"state": "waiting"})

        # Reassign pickings to picking zones
        pick1.picking_type_id = self.type_ali
        pick2.picking_type_id = self.type_ali
        pick3.picking_type_id = self.type_med
        pick4.picking_type_id = self.type_frigo
        pick5.picking_type_id = self.type_mat
        pick6.picking_type_id = self.type_mat

        ship1.move_lines.write({"state": "waiting"})
        ship2.move_lines.write({"state": "waiting"})
        ship3.move_lines.write({"state": "waiting"})

        pickings = pick1 | pick2 | pick3 | pick4 | pick5 | pick6 | ship1 | ship2 | ship3
        self.delivery_round_1._assign_pickings(pickings)

        pick1.move_lines.write({"state": "done"})
        pick4.move_lines.write({"state": "done"})
        ship1.move_lines.write({"state": "done"})

        self.assertEqual(round_1.count_picking_available_total, 5)
        self.assertEqual(round_1.count_picking_available_partner, 3)
        self.assertEqual(round_1.count_picking_available_weight, 50)

        self.assertEqual(round_1.count_picking_available_total_ali, 2)
        self.assertEqual(round_1.count_picking_available_total_med, 2)
        self.assertEqual(round_1.count_picking_available_total_frigo, 1)
        self.assertEqual(round_1.count_picking_available_total_mat, 0)
        self.assertEqual(round_1.count_picking_available_total_pharm, 0)

        self.assertEqual(round_1.count_picking_done_total, 2)

        self.assertEqual(round_1.count_picking_done_total_ali, 0)
        self.assertEqual(round_1.count_picking_done_total_med, 1)
        self.assertEqual(round_1.count_picking_done_total_frigo, 1)
        self.assertEqual(round_1.count_picking_done_total_mat, 0)
        self.assertEqual(round_1.count_picking_done_total_pharm, 0)
