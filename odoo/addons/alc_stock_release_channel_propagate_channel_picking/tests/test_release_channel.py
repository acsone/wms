# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockReleaseChannelPropagation(TransactionCase):
    def test_default(self):
        channel = self.env["stock.release.channel"].create({"name": "Test"})

        self.assertTrue(channel.propagate_to_pickings_chain)
