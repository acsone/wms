# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import pytz

from odoo import fields

from odoo.addons.delivery_rounds.tests.common import DeliveryRoundTestCase
from odoo.addons.queue_job.tests.common import JobMixin


class TestAutoClosePickings(DeliveryRoundTestCase, JobMixin):
    @classmethod
    def setUpClass(cls):
        super(TestAutoClosePickings, cls).setUpClass()

        PickingZone = cls.env["picking.zone"]
        cls.zone_med = PickingZone.create({"name": "M (Med)", "code": "05"})

        PickingType = cls.env["stock.picking.type"]

        wh = cls.env.ref("stock.warehouse0")
        picking_sequence = wh.in_type_id.sequence_id

        cls.type_med = PickingType.create(
            {
                "name": "Pick Med",
                "code": "internal",
                "subcode": "PICK",
                "picking_zone_id": cls.zone_med.id,
                "sequence_id": picking_sequence.id,
            }
        )

        cls.tag_monday = cls.env["round.tag"].create({"name": "Monday"})
        cls.delivery_template.write(
            {
                "auto_close_picking_launched": True,
                "time_reopen_picking_launched": 0.5,
                "time_leave_planned": 9,
                "time_picking_planned": 6,
                "tag_ids": [(4, cls.tag_monday.id)],
            }
        )
        cls.delivery_round_1.write(
            {
                "auto_close_picking_launched": True,
                "time_reopen_picking_launched": 0.5,
                "time_leave_planned": 9,
                "time_picking_planned": 6,
                "date": "2022-07-06",
            }
        )
        cls.version = cls.env["round.template.version"].create(
            {
                "name": "Version test",
                "template_ids": [(6, 0, [cls.delivery_template.id])],
            }
        )

        cls.MakeDeliveryPlanWizard = cls.env["round.wizard.makeplan"]
        cls.wizard = cls.MakeDeliveryPlanWizard.create(
            {
                "version_id": cls.version.id,
                "tag_ids": [(6, 0, [cls.tag_monday.id])],
                "execution_date": "2022-07-06",
            }
        )

    def test_auto_close_all_pickings_done(self):
        pick1 = self._create_picking_pick(partner=self.partner1)
        pick2 = self._create_picking_pick(partner=self.partner2)
        pick3 = self._create_picking_pick(partner=self.partner3)

        pick1.picking_type_id = self.type_med
        pick2.picking_type_id = self.type_med
        pick3.picking_type_id = self.type_med

        pick1.action_confirm()
        pick1.action_assign()
        pick1.force_assign()

        pick2.action_confirm()
        pick2.action_assign()
        pick2.force_assign()

        pick3.action_confirm()
        pick3.action_assign()
        pick3.force_assign()

        pickings = pick1 | pick2 | pick3
        self.delivery_round_1._assign_pickings(pickings)
        self.delivery_round_1.picking_med_launched = True

        pickings.assign_operator()

        self.assertFalse(self.delivery_round_1.picking_med_launched)

    def test_no_auto_close_all_pickings_done(self):
        self.delivery_round_1.auto_close_picking_launched = False
        pick1 = self._create_picking_pick(partner=self.partner1)
        pick2 = self._create_picking_pick(partner=self.partner2)
        pick3 = self._create_picking_pick(partner=self.partner3)

        pick1.picking_type_id = self.type_med
        pick2.picking_type_id = self.type_med
        pick3.picking_type_id = self.type_med

        pick1.action_confirm()
        pick1.action_assign()
        pick1.force_assign()

        pick2.action_confirm()
        pick2.action_assign()
        pick2.force_assign()

        pick3.action_confirm()
        pick3.action_assign()
        pick3.force_assign()

        pickings = pick1 | pick2 | pick3
        self.delivery_round_1._assign_pickings(pickings)
        self.delivery_round_1.picking_med_launched = True

        pickings.assign_operator()

        self.assertTrue(self.delivery_round_1.picking_med_launched)

    def test_no_auto_open_pickings(self):
        self.delivery_round_1.auto_close_picking_launched = False
        job_counter = self.job_counter()
        # create delivery plan
        self.wizard.confirm()
        # Then no job created to reopen pickings
        queue_job = job_counter.search_created()
        self.assertEqual(len(queue_job), 0)

    def test_auto_open_pickings(self):
        job_counter = self.job_counter()
        # create delivery plan
        self.wizard.confirm()
        # Then job created to reopen pickings
        queue_job = job_counter.search_created()
        self.assertEqual(len(queue_job), 1)
        date_relaunch = fields.Datetime.from_string(
            self.delivery_round_1.date + " 07:45:00"
        )
        bru_tz = pytz.timezone("Europe/Brussels")
        utc_tz = pytz.timezone("UTC")
        eta_time = bru_tz.localize(date_relaunch).astimezone(utc_tz)
        self.assertEqual(queue_job.eta, fields.Datetime.to_string(eta_time))

    def test_toggle_by_zone(self):
        self.assertFalse(self.delivery_round_1.picking_launched)

        self.assertFalse(self.delivery_round_1.picking_ali_launched)
        self.delivery_round_1.toggle_picking_ali_launched()
        self.assertTrue(self.delivery_round_1.picking_ali_launched)

        self.assertFalse(self.delivery_round_1.picking_med_launched)
        self.delivery_round_1.toggle_picking_med_launched()
        self.assertTrue(self.delivery_round_1.picking_med_launched)

        self.assertFalse(self.delivery_round_1.picking_mat_launched)
        self.delivery_round_1.toggle_picking_mat_launched()
        self.assertTrue(self.delivery_round_1.picking_mat_launched)

        self.assertFalse(self.delivery_round_1.picking_frigo_launched)
        self.delivery_round_1.toggle_picking_frigo_launched()
        self.assertTrue(self.delivery_round_1.picking_frigo_launched)

        self.assertTrue(self.delivery_round_1.picking_launched)

    def test_toggle_global(self):
        self.assertFalse(self.delivery_round_1.picking_launched)
        self.assertFalse(self.delivery_round_1.picking_ali_launched)
        self.assertFalse(self.delivery_round_1.picking_med_launched)
        self.assertFalse(self.delivery_round_1.picking_mat_launched)
        self.assertFalse(self.delivery_round_1.picking_frigo_launched)

        self.delivery_round_1.toggle_picking_launched()

        self.assertTrue(self.delivery_round_1.picking_ali_launched)
        self.assertTrue(self.delivery_round_1.picking_med_launched)
        self.assertTrue(self.delivery_round_1.picking_mat_launched)
        self.assertTrue(self.delivery_round_1.picking_frigo_launched)
        self.assertTrue(self.delivery_round_1.picking_launched)

    def test_assign_batch_one_picking_left_todo(self):
        # 3 picks in the delivery round, we create a batch with 2
        pick1 = self._create_picking_pick(partner=self.partner1)
        pick2 = self._create_picking_pick(partner=self.partner2)
        pick3 = self._create_picking_pick(partner=self.partner3)

        pick1.picking_type_id = self.type_med
        pick2.picking_type_id = self.type_med
        pick3.picking_type_id = self.type_med

        pick1.action_confirm()
        pick1.action_assign()
        pick1.force_assign()

        pick2.action_confirm()
        pick2.action_assign()
        pick2.force_assign()

        pick3.action_confirm()
        pick3.action_assign()
        pick3.force_assign()

        pickings = pick1 | pick2

        self.delivery_round_1._assign_pickings(pickings)
        self.delivery_round_1._assign_pickings(pick3)
        self.delivery_round_1.picking_med_launched = True

        batch = self.env["stock.picking.wave"].create(
            {"picking_ids": [(6, None, pickings.ids)]}
        )
        batch.picking_ids.action_confirm()
        batch.picking_ids.action_assign()

        batch.assign_operator()
        self.assertTrue(self.delivery_round_1.picking_med_launched)

    def test_assign_batch_close_zone(self):
        # 3 picks in the delivery round, we create a batch with 2
        pick1 = self._create_picking_pick(partner=self.partner1)
        pick2 = self._create_picking_pick(partner=self.partner2)
        pick3 = self._create_picking_pick(partner=self.partner3)

        pick1.picking_type_id = self.type_med
        pick2.picking_type_id = self.type_med
        pick3.picking_type_id = self.type_med

        pick1.action_confirm()
        pick1.action_assign()
        pick1.force_assign()

        pick2.action_confirm()
        pick2.action_assign()
        pick2.force_assign()

        pick3.action_confirm()
        pick3.action_assign()
        pick3.force_assign()

        pickings = pick1 | pick2 | pick3

        self.delivery_round_1._assign_pickings(pickings)
        self.delivery_round_1.picking_med_launched = True

        batch = self.env["stock.picking.wave"].create(
            {"picking_ids": [(6, None, pickings.ids)]}
        )
        batch.picking_ids.action_confirm()
        batch.picking_ids.action_assign()

        batch.assign_operator()
        self.assertFalse(self.delivery_round_1.picking_med_launched)
