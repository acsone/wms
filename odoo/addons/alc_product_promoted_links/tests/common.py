# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestPromotedLinks(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPromotedLinks, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        vals_product_promotes = {"name": "P1", "default_code": "C1"}
        cls.product_promotes = cls.env["product.template"].create(vals_product_promotes)
        vals_product_promoted = {"name": "P2", "default_code": "C2"}
        cls.product_promoted = cls.env["product.template"].create(vals_product_promoted)

        cls.link_type = cls.env.ref("alc_product_promoted_links.link_type_promotes")
