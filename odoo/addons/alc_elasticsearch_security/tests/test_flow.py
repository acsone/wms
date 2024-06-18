# Copyright 2021 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from psycopg2.errors import UniqueViolation

from odoo.tools import mute_logger

from .common import TestESRoles


class TestESRolesFlow(TestESRoles):
    def test_default_partner_role(self):
        # given
        vals_partner = {"name": "P"}
        # when
        partner = self.env["res.partner"].create(vals_partner)
        # then
        self.assertTrue("guest" in partner.elasticsearch_role)
        self.assertTrue(partner.partner_type in partner.elasticsearch_role)
        price_role_name = partner.property_product_pricelist.role_name
        self.assertTrue(price_role_name in partner.elasticsearch_role)

    def test_partner_role(self):
        # given
        vals_partner = {"name": "P", "partner_type": "guest"}
        partner = self.env["res.partner"].create(vals_partner)
        # when
        partner.property_product_pricelist = self.pricelist
        # then
        expected = set(partner.elasticsearch_role.split(","))
        # remove potential role from alc_elasticsearch_security_vt_groups
        expected.discard("non_alcyonnaire")
        self.assertSetEqual(
            expected,
            {self.pricelist.role_name, "guest"},
        )

    def test_unique_pricelist_role(self):
        self.assertFalse(self.backend.role_ids)
        self.backend.create_pricelist_roles()
        self.assertTrue(self.backend.role_ids)
        with self.assertRaises(UniqueViolation), mute_logger("odoo.sql_db"):
            self.backend.role_ids[0].copy({})

    def test_pricelist_role(self):
        self.assertFalse(self.backend.role_ids)
        self.backend.create_pricelist_roles()
        self.assertTrue(self.backend.role_ids)
        pricelist_role = self.backend.role_ids.filtered(
            lambda r: r.pricelist_id == self.pricelist
        )
        self.assertEqual(pricelist_role.name, self.pricelist.role_name)
        self.assertDictEqual(
            json.loads(pricelist_role.body),
            {
                "index_permissions": [
                    {
                        "index_patterns": ["alc_shopinvader_variant_*"],
                        "fls": [
                            "indicated_price",
                            f"price.{self.pricelist.role_name}.*",
                            f"price.{self.pricelist.discount_role_name}.*",
                            f"current_{self.pricelist.role_name}",
                            f"current_{self.pricelist.discount_role_name}",
                            f"current_{self.pricelist.discount_role_name}_exclusive",
                        ],
                    }
                ]
            },
        )
