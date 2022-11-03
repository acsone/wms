# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.shopinvader_search_engine_update_product.tests.common import (
    TestProductUpdate,
)


class TestProductLinkUpdate(TestProductUpdate):
    @classmethod
    def setUpClass(cls):
        super(TestProductLinkUpdate, cls).setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                # compatibility flag when you run tests on a db
                # where `product_variant_multi_link` is installed.
                _product_variant_link_bypass_check=True,
            )
        )
        cls.product_template_2 = cls.env["product.template"].create({"name": "P2"})
        cls.product_2 = cls.product_template_2.product_variant_id

        cls.product_template_3 = cls.env["product.template"].create({"name": "P3"})
        cls.product_3 = cls.product_template_3.product_variant_id

        xmlid = "product_template_multi_link.product_template_link_type_up_selling"
        cls.link_type_up_sell = cls.env.ref(xmlid)
        cls.model = cls.env["product.template.link"]

        cls.product_templates = (
            cls.product_template + cls.product_template_2 + cls.product_template_3
        )
        cls.backend.bind_all_product(domain=[("id", "in", cls.product_templates.ids)])
        cls.binding_2 = cls.product_2.shopinvader_bind_ids
        cls.binding_3 = cls.product_3.shopinvader_bind_ids
        cls.bindings = cls.binding + cls.binding_2 + cls.binding_3
        cls.bindings.write({"to_update": "false"})
