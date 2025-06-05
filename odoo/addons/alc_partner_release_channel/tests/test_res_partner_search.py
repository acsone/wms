# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestResPartnerSearch(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        self.ResPartner = self.env["res.partner"]
        self.StockReleaseChannel = self.env["stock.release.channel"]

        self.channel_alpha = self.StockReleaseChannel.create({"name": "Alpha Channel"})
        self.channel_beta = self.StockReleaseChannel.create({"name": "Beta Channel"})
        self.channel_gamma = self.StockReleaseChannel.create({"name": "Gamma Channel"})

        self.partner_a = self.ResPartner.create({"name": "Partner A"})
        self.partner_b = self.ResPartner.create({"name": "Partner B"})
        self.partner_c = self.ResPartner.create({"name": "Partner C"})
        self.partner_d = self.ResPartner.create({"name": "Partner D"})

        self.partner_a.located_in_stock_release_channel_ids = [
            Command.link(self.channel_alpha.id)
        ]
        self.partner_b.located_in_stock_release_channel_ids = [
            Command.link(self.channel_alpha.id),
            Command.link(self.channel_beta.id),
        ]
        self.partner_c.located_in_stock_release_channel_ids = [
            Command.link(self.channel_gamma.id)
        ]

    def test_search_located_in_stock_release_channel_ids_like(self):
        # Search for partners located in 'Alpha Channel'
        partners = self.ResPartner.search(
            [("located_in_stock_release_channel_ids", "like", "Alpha")]
        )
        self.assertIn(self.partner_a, partners)
        self.assertIn(self.partner_b, partners)
        self.assertNotIn(self.partner_c, partners)
        self.assertNotIn(self.partner_d, partners)

        # Search for partners located in 'Beta Channel'
        partners = self.ResPartner.search(
            [("located_in_stock_release_channel_ids", "like", "Beta")]
        )
        self.assertNotIn(self.partner_a, partners)
        self.assertIn(self.partner_b, partners)
        self.assertNotIn(self.partner_c, partners)
        self.assertNotIn(self.partner_d, partners)

        # Search for partners located in 'Gamma Channel'
        partners = self.ResPartner.search(
            [("located_in_stock_release_channel_ids", "like", "Gamma")]
        )
        self.assertNotIn(self.partner_a, partners)
        self.assertNotIn(self.partner_b, partners)
        self.assertIn(self.partner_c, partners)
        self.assertNotIn(self.partner_d, partners)

        # Search for a non-existent channel
        partners = self.ResPartner.search(
            [("located_in_stock_release_channel_ids", "like", "NonExistent")]
        )
        self.assertFalse(partners)

    def test_search_located_in_stock_release_channel_ids_ilike(self):
        partners = self.ResPartner.search(
            [("located_in_stock_release_channel_ids", "ilike", "alpha")]
        )
        self.assertIn(self.partner_a, partners)
        self.assertIn(self.partner_b, partners)
        self.assertNotIn(self.partner_c, partners)
        self.assertNotIn(self.partner_d, partners)

    def test_search_located_in_stock_release_channel_ids_unsupported_operator(self):
        with self.assertRaises(UserError):
            self.ResPartner.search(
                [("located_in_stock_release_channel_ids", "=", "Alpha")]
            )

    def test_search_located_in_stock_release_channel_ids_unsupported_value_type(self):
        with self.assertRaises(UserError):
            self.ResPartner.search(
                [("located_in_stock_release_channel_ids", "like", 123)]
            )

    def test_partner_with_no_channel(self):
        partners = self.ResPartner.search(
            [("located_in_stock_release_channel_ids", "like", "Alpha")]
        )
        self.assertNotIn(self.partner_d, partners)

        partners = self.ResPartner.search(
            [("located_in_stock_release_channel_ids", "like", "Gamma")]
        )
        self.assertNotIn(self.partner_d, partners)
