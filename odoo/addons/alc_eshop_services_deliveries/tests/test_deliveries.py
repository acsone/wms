# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestDeliveriesService


class TestDocumentsServiceFlow(TestDeliveriesService):
    def test_search_done(self):
        with self.service() as service:
            done = service._search_done()
            self.assertEqual(done, self.picking_done + self.picking_half)

    def test_search_canceled(self):
        with self.service() as service:
            canceled = service._search_canceled()
            self.assertEqual(canceled, self.picking_cancel + self.picking_half)
