# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from .common import TestProductLinkUpdate


class TestProductLinkUpdateFlow(TestProductLinkUpdate):
    def test_flow(self):
        # given
        vals = {
            "left_product_tmpl_id": self.product_template.id,
            "right_product_tmpl_id": self.product_template_2.id,
            "type_id": self.link_type_up_sell.id,
        }
        # when
        link = self.model.create(vals)
        # then
        self.assertEqual(self.binding.to_update, "true")
        self.assertEqual(self.binding_2.to_update, "true")
        self.assertEqual(self.binding_3.to_update, "false")

        # given
        self.bindings.write({"to_update": "false"})
        # when
        link.right_product_tmpl_id = self.product_template_3
        # then
        self.assertEqual(self.binding.to_update, "true")
        self.assertEqual(self.binding_3.to_update, "true")
        self.assertEqual(self.binding_2.to_update, "true")

        # given
        self.bindings.write({"to_update": "false"})
        # when
        link.unlink()
        # then
        self.assertEqual(self.binding.to_update, "true")
        self.assertEqual(self.binding_3.to_update, "true")
        self.assertEqual(self.binding_2.to_update, "false")
