# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin
from odoo.addons.shopinvader_schema_sale.schemas import Sale, SaleSearch


class TestSaleCartRestApi(TransactionCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create({"name": "test partner"})

        cls.order = cls.env["sale.order"].create(
            {
                "sale_channel_id": cls.env.ref("alc_sale_channel.sale_channel_web").id,
                "partner_id": cls.partner.id,
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.reset_extendable_registry()
        super().tearDownClass()

    def test_channel_in_cart(self):
        sale = Sale.from_sale_order(self.order)
        self.assertEqual("web", sale.channel)

    def test_sale_search_channel(self):
        sale_search = SaleSearch()
        domain = sale_search.to_odoo_domain(self.env)
        self.assertIn(
            ("sale_channel_id", "in", self.env["sale.channel"]._get_internal_ids()),
            domain,
        )
