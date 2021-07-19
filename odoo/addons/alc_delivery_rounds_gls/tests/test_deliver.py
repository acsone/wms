# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.delivery_rounds.tests.common import DeliverDeliveryRoundTestCase


class TestDeliveryRoundGls(DeliverDeliveryRoundTestCase):
    def test_deliver(self):
        carrier_gls = self.env.ref("delivery_carrier_label_gls.delivery_carrier_gls")

        self.partner1.is_sale_back_order_cancel = False
        delivery_round, picks, _ships = self._prepare_delivery_round()
        delivery_round.button_close()

        picking_gls = picks[0]
        picking_gls.carrier_id = carrier_gls

        # we simulate action_done (since it would call GLS it would need to be mocked)
        picking_gls.write({"state": "done"})
        delivery_round._deliver(background=False)  # now works as expected
        # delivery_round.instance_customer_ids._deliver(background=False)  # same
        self.assertTrue(picking_gls.delivery_round_customer_id.delivered)
